import argparse
import json
import statistics
import time
import os
from typing import Any, Dict, List, Optional, Tuple

import httpx


def _extract_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    # Ollama commonly returns these fields for /api/chat.
    # Not all are guaranteed; keep it defensive.
    return {
        "prompt_tokens": data.get("prompt_eval_count"),
        "completion_tokens": data.get("eval_count"),
        "total_duration_ns": data.get("total_duration"),
        "load_duration_ns": data.get("load_duration"),
        "prompt_eval_duration_ns": data.get("prompt_eval_duration"),
        "eval_duration_ns": data.get("eval_duration"),
    }


def _tokens_per_second(tokens: Optional[int], duration_ns: Optional[int]) -> Optional[float]:
    if not tokens or not duration_ns:
        return None
    if duration_ns <= 0:
        return None
    return float(tokens) / (float(duration_ns) / 1e9)


def _post_chat(
    client: httpx.Client,
    base_url: str,
    model: str,
    prompt: str,
    options: Optional[Dict[str, Any]] = None,
) -> Tuple[float, Dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    if options:
        payload["options"] = options

    start = time.perf_counter()
    resp = client.post(url, json=payload)
    elapsed = time.perf_counter() - start

    resp.raise_for_status()
    data = resp.json()
    return elapsed, data


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Ollama /api/chat speed")
    parser.add_argument("--base-url", default="http://ollama:11434", help="Ollama base URL")
    parser.add_argument("--model", default="mistral:7b-instruct", help="Model name (no change required)")
    parser.add_argument("--runs", type=int, default=5, help="Number of measured runs")
    parser.add_argument("--warmup", type=int, default=1, help="Warmup runs (not included in stats)")
    parser.add_argument(
        "--prompt",
        default="Responde SOLO con: OK",
        help="Prompt to send",
    )
    parser.add_argument("--timeout", type=float, default=180.0, help="HTTP timeout seconds")
    parser.add_argument("--num-ctx", type=int, default=None, help="Send options.num_ctx")
    parser.add_argument("--num-thread", type=int, default=None, help="Send options.num_thread")
    parser.add_argument("--num-gpu", type=int, default=None, help="Send options.num_gpu")
    parser.add_argument(
        "--sweep-ctx",
        default=None,
        help="Comma-separated list of num_ctx values to benchmark (e.g., 1024,2048,3072)",
    )

    args = parser.parse_args()

    env_prompt = os.getenv("BENCH_PROMPT")
    if env_prompt:
        args.prompt = env_prompt

    base_options: Dict[str, Any] = {}
    if args.num_ctx is not None:
        base_options["num_ctx"] = args.num_ctx
    if args.num_thread is not None:
        base_options["num_thread"] = args.num_thread
    if args.num_gpu is not None:
        base_options["num_gpu"] = args.num_gpu

    sweep_ctx: Optional[List[int]] = None
    if args.sweep_ctx:
        sweep_ctx = [int(x.strip()) for x in args.sweep_ctx.split(",") if x.strip()]
        if not sweep_ctx:
            sweep_ctx = None

    def run_one(label: str, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        times: List[float] = []
        tps_list: List[float] = []
        completion_tokens_list: List[int] = []

        with httpx.Client(timeout=httpx.Timeout(args.timeout)) as client:
            for _ in range(max(args.warmup, 0)):
                _post_chat(client, args.base_url, args.model, args.prompt, options=options)

            for _ in range(max(args.runs, 1)):
                elapsed, data = _post_chat(client, args.base_url, args.model, args.prompt, options=options)
                times.append(elapsed)

                metrics = _extract_metrics(data)
                completion_tokens = metrics.get("completion_tokens")
                eval_duration_ns = metrics.get("eval_duration_ns")

                if isinstance(completion_tokens, int):
                    completion_tokens_list.append(completion_tokens)

                tps = _tokens_per_second(
                    completion_tokens if isinstance(completion_tokens, int) else None,
                    eval_duration_ns if isinstance(eval_duration_ns, int) else None,
                )
                if tps is not None:
                    tps_list.append(tps)

        return {
            "label": label,
            "options": options or {},
            "runs": len(times),
            "wall_time_s": {
                "avg": statistics.mean(times),
                "p50": statistics.median(times),
                "min": min(times),
                "max": max(times),
            },
            "completion_tokens": {
                "avg": statistics.mean(completion_tokens_list) if completion_tokens_list else None,
            },
            "completion_tokens_per_second": {
                "avg": statistics.mean(tps_list) if tps_list else None,
                "p50": statistics.median(tps_list) if tps_list else None,
            },
        }

    if sweep_ctx:
        results = []
        for ctx in sweep_ctx:
            opts = dict(base_options)
            opts["num_ctx"] = ctx
            results.append(run_one(label=f"num_ctx={ctx}", options=opts))

        print(
            json.dumps(
                {
                    "base_url": args.base_url,
                    "model": args.model,
                    "prompt": args.prompt,
                    "results": results,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    summary = run_one(label="single", options=base_options if base_options else None)
    summary["base_url"] = args.base_url
    summary["model"] = args.model
    summary["prompt"] = args.prompt

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
