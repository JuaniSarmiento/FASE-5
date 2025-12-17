import requests
import json

print("🧪 Test de Evaluación con IA (GPU)")
print("=" * 50)

code = """total = 42600
promedio = 14200.00
print('Cálculos completados')"""

payload = {"student_code": code}

print("\n📤 Enviando código...")
print(code)
print("\n⏳ Esperando respuesta (puede tardar 10-30 segundos)...")

response = requests.post(
    "http://localhost:8000/api/v1/exercises/json/U1-VAR-01/submit",
    json=payload,
    timeout=300
)

if response.status_code == 200:
    result = response.json()
    print("\n✅ ¡EVALUACIÓN EXITOSA!")
    print("=" * 50)
    print(f"Score: {result['evaluation']['score']}/100")
    print(f"Status: {result['evaluation']['status']}")
    print(f"\n📝 Resumen:")
    print(result['evaluation']['summary_markdown'])
    print(f"\n📊 Dimensiones:")
    print(f"  • Funcionalidad: {result['dimensions']['functionality']['score']}/10")
    print(f"  • Calidad: {result['dimensions']['code_quality']['score']}/10")
    print(f"  • Robustez: {result['dimensions']['robustness']['score']}/10")
    print(f"\n🎮 XP Ganado: +{result['gamification']['xp_earned']}")
    
    if 'metadata' in result and result['metadata']:
        print(f"\n🤖 Modelo IA: {result['metadata']['llm_model']}")
    
    print("\n" + "=" * 50)
    print("✅ LA EVALUACIÓN CON IA FUNCIONA CORRECTAMENTE!")
    print("=" * 50)
else:
    print(f"\n❌ Error: {response.status_code}")
    print(response.text)
