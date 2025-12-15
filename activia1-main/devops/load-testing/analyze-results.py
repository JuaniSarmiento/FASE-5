#!/usr/bin/env python3
"""
AI-Native MVP - Load Testing Results Analyzer
Author: Mag. Alberto Cortez
Date: 2025-11-24

Analyzes Artillery JSON reports and generates performance insights.
"""

import json
import sys
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Windows encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class LoadTestAnalyzer:
    """Analyzes Artillery load test results."""

    def __init__(self, report_path: str):
        self.report_path = Path(report_path)
        with open(self.report_path, 'r') as f:
            self.data = json.load(f)

        self.aggregate = self.data.get('aggregate', {})
        self.intermediate = self.data.get('intermediate', [])

    def print_summary(self):
        """Print executive summary."""
        print("=" * 60)
        print("LOAD TEST RESULTS - EXECUTIVE SUMMARY")
        print("=" * 60)
        print()

        # Test duration
        counters = self.aggregate.get('counters', {})
        summaries = self.aggregate.get('summaries', {})

        scenarios_completed = counters.get('vusers.completed', 0)
        scenarios_created = counters.get('vusers.created', 0)
        http_requests = counters.get('http.requests', 0)
        http_responses = counters.get('http.responses', 0)

        print(f"📊 Virtual Users:")
        print(f"   Created:   {scenarios_created}")
        print(f"   Completed: {scenarios_completed}")
        print(f"   Success Rate: {(scenarios_completed/scenarios_created*100):.2f}%")
        print()

        print(f"🌐 HTTP Requests:")
        print(f"   Total Requests:  {http_requests}")
        print(f"   Total Responses: {http_responses}")
        print()

        # HTTP status codes
        print("📈 HTTP Status Codes:")
        status_codes = {k: v for k, v in counters.items() if k.startswith('http.codes.')}
        for code, count in sorted(status_codes.items()):
            code_num = code.split('.')[-1]
            emoji = "✅" if code_num.startswith('2') else "⚠️" if code_num.startswith('4') else "❌"
            print(f"   {emoji} {code_num}: {count} ({count/http_responses*100:.1f}%)")
        print()

        # Response times
        print("⏱️  Response Times:")
        http_response_time = summaries.get('http.response_time', {})
        if http_response_time:
            print(f"   Min:    {http_response_time.get('min', 0):.0f} ms")
            print(f"   Max:    {http_response_time.get('max', 0):.0f} ms")
            print(f"   Mean:   {http_response_time.get('mean', 0):.0f} ms")
            print(f"   Median: {http_response_time.get('median', 0):.0f} ms")
            print(f"   p95:    {http_response_time.get('p95', 0):.0f} ms")
            print(f"   p99:    {http_response_time.get('p99', 0):.0f} ms")
        print()

        # Errors
        errors = counters.get('errors.ETIMEDOUT', 0) + \
                 counters.get('errors.ECONNREFUSED', 0) + \
                 counters.get('errors.ENOTFOUND', 0)

        print(f"❌ Errors:")
        print(f"   Timeouts:         {counters.get('errors.ETIMEDOUT', 0)}")
        print(f"   Connection Refused: {counters.get('errors.ECONNREFUSED', 0)}")
        print(f"   Not Found:        {counters.get('errors.ENOTFOUND', 0)}")
        print(f"   Total Errors:     {errors}")
        print(f"   Error Rate:       {(errors/http_requests*100):.2f}%" if http_requests > 0 else "   Error Rate:       N/A")
        print()

        # Throughput
        rps = summaries.get('http.request_rate', {})
        if rps:
            print(f"🚀 Throughput:")
            print(f"   Requests/sec (mean): {rps.get('mean', 0):.1f}")
            print(f"   Requests/sec (max):  {rps.get('max', 0):.1f}")
        print()

    def analyze_performance(self):
        """Analyze performance against SLAs."""
        print("=" * 60)
        print("PERFORMANCE ANALYSIS (SLA Compliance)")
        print("=" * 60)
        print()

        summaries = self.aggregate.get('summaries', {})
        http_response_time = summaries.get('http.response_time', {})

        # Define SLAs
        slas = {
            'p95': 2000,  # 95th percentile < 2s
            'p99': 5000,  # 99th percentile < 5s
            'mean': 1000,  # Mean < 1s
        }

        print("SLA Targets:")
        print(f"   Mean response time:  < {slas['mean']} ms")
        print(f"   95th percentile:     < {slas['p95']} ms")
        print(f"   99th percentile:     < {slas['p99']} ms")
        print()

        print("Actual Performance:")
        for metric, target in slas.items():
            actual = http_response_time.get(metric, 0)
            status = "✅ PASS" if actual < target else "❌ FAIL"
            print(f"   {metric.upper()}: {actual:.0f} ms (target: {target} ms) {status}")
        print()

        # Error rate SLA
        counters = self.aggregate.get('counters', {})
        http_requests = counters.get('http.requests', 1)  # Avoid division by zero
        errors = sum(v for k, v in counters.items() if k.startswith('errors.'))
        error_rate = (errors / http_requests) * 100

        error_rate_sla = 5.0  # Max 5% error rate
        error_status = "✅ PASS" if error_rate < error_rate_sla else "❌ FAIL"

        print(f"Error Rate: {error_rate:.2f}% (target: < {error_rate_sla}%) {error_status}")
        print()

    def analyze_scalability(self):
        """Analyze HPA scaling behavior from intermediate results."""
        print("=" * 60)
        print("SCALABILITY ANALYSIS (HPA Behavior)")
        print("=" * 60)
        print()

        if not self.intermediate:
            print("⚠️  No intermediate data available")
            print()
            return

        print("Response Time Over Time:")
        print(f"{'Time':<8} {'Mean (ms)':<12} {'p95 (ms)':<12} {'RPS':<10} {'Errors'}")
        print("-" * 60)

        for period in self.intermediate:
            timestamp = period.get('timestamp', 0)
            time_str = datetime.fromtimestamp(timestamp / 1000).strftime('%H:%M:%S')

            summaries = period.get('summaries', {})
            response_time = summaries.get('http.response_time', {})
            request_rate = summaries.get('http.request_rate', {})

            mean_rt = response_time.get('mean', 0)
            p95_rt = response_time.get('p95', 0)
            rps = request_rate.get('mean', 0)

            counters = period.get('counters', {})
            errors = sum(v for k, v in counters.items() if k.startswith('errors.'))

            print(f"{time_str:<8} {mean_rt:<12.0f} {p95_rt:<12.0f} {rps:<10.1f} {errors}")

        print()
        print("💡 Insights:")
        print("   - Monitor for response time degradation during ramp-up")
        print("   - Check if HPA triggered new pods during peak load")
        print("   - Verify error rate remains low throughout test")
        print()

    def generate_recommendations(self):
        """Generate optimization recommendations."""
        print("=" * 60)
        print("RECOMMENDATIONS")
        print("=" * 60)
        print()

        summaries = self.aggregate.get('summaries', {})
        counters = self.aggregate.get('counters', {})

        http_response_time = summaries.get('http.response_time', {})
        p95 = http_response_time.get('p95', 0)
        p99 = http_response_time.get('p99', 0)
        mean = http_response_time.get('mean', 0)

        http_requests = counters.get('http.requests', 1)
        errors = sum(v for k, v in counters.items() if k.startswith('errors.'))
        error_rate = (errors / http_requests) * 100

        recommendations = []

        # Performance recommendations
        if mean > 1000:
            recommendations.append({
                'severity': 'HIGH',
                'category': 'Performance',
                'issue': f'Mean response time is {mean:.0f} ms (target: <1000 ms)',
                'actions': [
                    'Review database query performance',
                    'Check Redis cache hit rate',
                    'Profile slow endpoints',
                    'Consider increasing backend replicas'
                ]
            })

        if p95 > 2000:
            recommendations.append({
                'severity': 'HIGH',
                'category': 'Performance',
                'issue': f'p95 response time is {p95:.0f} ms (target: <2000 ms)',
                'actions': [
                    'Optimize database connection pooling',
                    'Review LLM provider latency',
                    'Check for N+1 query problems',
                    'Increase HPA max replicas'
                ]
            })

        if p99 > 5000:
            recommendations.append({
                'severity': 'MEDIUM',
                'category': 'Performance',
                'issue': f'p99 response time is {p99:.0f} ms (target: <5000 ms)',
                'actions': [
                    'Identify outlier requests',
                    'Review timeout configurations',
                    'Check for resource contention'
                ]
            })

        # Error rate recommendations
        if error_rate > 5:
            recommendations.append({
                'severity': 'CRITICAL',
                'category': 'Reliability',
                'issue': f'Error rate is {error_rate:.2f}% (target: <5%)',
                'actions': [
                    'Review application logs for error patterns',
                    'Check database connection limits',
                    'Verify resource limits are sufficient',
                    'Investigate timeout errors'
                ]
            })

        # HPA recommendations
        http_codes_200 = counters.get('http.codes.200', 0)
        success_rate = (http_codes_200 / http_requests) * 100 if http_requests > 0 else 0

        if success_rate < 95:
            recommendations.append({
                'severity': 'HIGH',
                'category': 'Scalability',
                'issue': f'Success rate is {success_rate:.1f}% (target: >95%)',
                'actions': [
                    'Review HPA configuration (target CPU/memory)',
                    'Check if HPA scaled fast enough',
                    'Consider aggressive scaling policies',
                    'Review pod resource requests/limits'
                ]
            })

        # Display recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                severity_emoji = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }
                emoji = severity_emoji.get(rec['severity'], '⚪')

                print(f"{emoji} Recommendation #{i}: {rec['category']}")
                print(f"   Severity: {rec['severity']}")
                print(f"   Issue: {rec['issue']}")
                print(f"   Actions:")
                for action in rec['actions']:
                    print(f"      • {action}")
                print()
        else:
            print("✅ No critical issues found. System performing within SLAs.")
            print()

    def run_full_analysis(self):
        """Run complete analysis."""
        self.print_summary()
        self.analyze_performance()
        self.analyze_scalability()
        self.generate_recommendations()


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze-results.py <artillery-report.json>")
        print()
        print("Example:")
        print("  python analyze-results.py /tmp/artillery-report-full.json")
        sys.exit(1)

    report_path = sys.argv[1]

    if not Path(report_path).exists():
        print(f"❌ Error: Report file not found: {report_path}")
        sys.exit(1)

    print()
    analyzer = LoadTestAnalyzer(report_path)
    analyzer.run_full_analysis()

    print("=" * 60)
    print("Analysis complete!")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()