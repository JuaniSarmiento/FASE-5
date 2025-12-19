"""
Script para verificar cuántos ejercicios está devolviendo el backend
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🔍 VERIFICANDO EJERCICIOS EN EL BACKEND")
print("=" * 80)

try:
    # Verificar endpoint JSON
    print("\n📊 GET /exercises/json/list")
    response = requests.get(f"{BASE_URL}/exercises/json/list")
    
    if response.status_code == 200:
        ejercicios = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Total ejercicios: {len(ejercicios)}")
        
        # Agrupar por lenguaje
        by_lang = {}
        for ej in ejercicios:
            meta = ej.get('meta', {}) if 'meta' in ej else {}
            # El ID puede indicar el lenguaje
            if 'JAVA' in ej.get('id', ''):
                lang = 'java'
            elif 'SPRING' in ej.get('id', ''):
                lang = 'java (spring-boot)'
            else:
                lang = 'python'
            
            by_lang[lang] = by_lang.get(lang, 0) + 1
        
        print(f"\n📋 Por lenguaje:")
        for lang, count in by_lang.items():
            print(f"   - {lang}: {count}")
        
        print(f"\n📝 Primeros 5 ejercicios:")
        for i, ej in enumerate(ejercicios[:5], 1):
            print(f"   {i}. {ej.get('id', 'N/A')}: {ej.get('title', ej.get('meta', {}).get('title', 'N/A'))}")
        
        if len(ejercicios) > 5:
            print(f"   ... y {len(ejercicios) - 5} más")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:200])
        
except Exception as e:
    print(f"❌ Error conectando al backend: {e}")
    print("\nAsegúrate de que el backend esté corriendo:")
    print("  python -m backend")

# Verificar stats
try:
    print("\n" + "=" * 80)
    print("📊 GET /exercises/json/stats")
    response = requests.get(f"{BASE_URL}/exercises/json/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Verificar filtros
try:
    print("\n" + "=" * 80)
    print("🎯 GET /exercises/json/filters")
    response = requests.get(f"{BASE_URL}/exercises/json/filters")
    
    if response.status_code == 200:
        filters = response.json()
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(filters, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:200])
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 80)
