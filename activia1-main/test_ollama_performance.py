"""
Script para probar el rendimiento de Ollama y medir tokens/segundo
"""
import requests
import time
import json

OLLAMA_URL = "http://localhost:11434"

def test_ollama_performance():
    """Prueba el rendimiento de Ollama con diferentes prompts"""
    
    print("=" * 70)
    print("PRUEBA DE RENDIMIENTO DE OLLAMA")
    print("=" * 70)
    
    # Verificar que Ollama está disponible
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        print(f"\n✓ Ollama está disponible en {OLLAMA_URL}")
        models = response.json()
        print(f"✓ Modelos disponibles: {[m['name'] for m in models.get('models', [])]}")
    except Exception as e:
        print(f"✗ Error conectando a Ollama: {e}")
        return
    
    # Prompts de prueba
    prompts = [
        {
            "name": "Prompt Corto",
            "prompt": "Explica qué es la inteligencia artificial en 2 oraciones."
        },
        {
            "name": "Prompt Mediano",
            "prompt": "Explica los beneficios y desafíos de la inteligencia artificial en la educación. Sé específico y conciso."
        },
        {
            "name": "Prompt Largo",
            "prompt": "Escribe un análisis detallado sobre el impacto de la inteligencia artificial en la sociedad moderna, incluyendo aspectos éticos, económicos y tecnológicos. Estructura tu respuesta en párrafos claros."
        }
    ]
    
    for test in prompts:
        print(f"\n{'=' * 70}")
        print(f"TEST: {test['name']}")
        print(f"{'=' * 70}")
        print(f"Prompt: {test['prompt'][:80]}...")
        
        # Preparar request
        payload = {
            "model": "mistral:7b-instruct",
            "prompt": test['prompt'],
            "stream": True,
            "options": {
                "temperature": 0.7,
                "num_predict": 200
            }
        }
        
        # Realizar request con streaming
        start_time = time.time()
        token_count = 0
        response_text = ""
        
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                stream=True,
                timeout=180
            )
            
            first_token_time = None
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    
                    if 'response' in data:
                        token = data['response']
                        response_text += token
                        token_count += 1
                        
                        if first_token_time is None:
                            first_token_time = time.time()
                    
                    if data.get('done', False):
                        break
            
            end_time = time.time()
            
            # Calcular métricas
            total_time = end_time - start_time
            time_to_first_token = first_token_time - start_time if first_token_time else 0
            tokens_per_second = token_count / total_time if total_time > 0 else 0
            
            # Mostrar resultados
            print(f"\n{'─' * 70}")
            print(f"RESULTADOS:")
            print(f"{'─' * 70}")
            print(f"✓ Tokens generados: {token_count}")
            print(f"✓ Tiempo total: {total_time:.2f} segundos")
            print(f"✓ Tiempo al primer token: {time_to_first_token:.2f} segundos")
            print(f"✓ Velocidad: {tokens_per_second:.2f} tokens/segundo")
            print(f"\nRespuesta generada:")
            print(f"{'─' * 70}")
            print(response_text[:300] + "..." if len(response_text) > 300 else response_text)
            
        except Exception as e:
            print(f"✗ Error durante la generación: {e}")
    
    print(f"\n{'=' * 70}")
    print("PRUEBAS COMPLETADAS")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    test_ollama_performance()
