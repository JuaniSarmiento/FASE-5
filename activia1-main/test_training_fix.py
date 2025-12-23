"""
Script para probar el fix del endpoint de training
Verifica que se pueda iniciar entrenamiento con ejercicios del catálogo
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_ejercicio_disponible():
    """Verifica que el ejercicio esté disponible en el catálogo"""
    print("1. Verificando ejercicio U1-VAR-01 en catálogo...")
    
    response = requests.get(f"{BASE_URL}/exercises/json/U1-VAR-01")
    
    if response.status_code == 200:
        exercise = response.json()
        print("✅ Ejercicio encontrado en catálogo")
        print(f"   ID: {exercise['id']}")
        print(f"   Título: {exercise['meta']['title']}")
        print(f"   Dificultad: {exercise['meta']['difficulty']}")
        print(f"   Tiempo estimado: {exercise['meta']['estimated_time_min']} min")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_materias_disponibles():
    """Verifica que las materias incluyan los ejercicios del catálogo"""
    print("\n2. Verificando endpoint /training/materias...")
    
    # Este endpoint puede requerir auth, vamos a verificar primero
    response = requests.get(f"{BASE_URL}/training/materias")
    
    if response.status_code == 401:
        print("⚠️  Endpoint requiere autenticación (esperado)")
        return None
    elif response.status_code == 200:
        materias = response.json()
        print(f"✅ Materias obtenidas: {len(materias)}")
        
        for materia in materias:
            print(f"\n   Materia: {materia['materia']} ({materia['codigo']})")
            print(f"   Temas: {len(materia['temas'])}")
            
            # Buscar U1-VAR-01
            for tema in materia['temas']:
                if tema['id'] == 'U1-VAR-01':
                    print(f"   ✅ ENCONTRADO: {tema['nombre']}")
                    return True
        
        print("   ⚠️  U1-VAR-01 no encontrado en las materias")
        return False
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_stats():
    """Verifica las estadísticas de ejercicios"""
    print("\n3. Verificando estadísticas...")
    
    response = requests.get(f"{BASE_URL}/exercises/json/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Estadísticas obtenidas")
        print(f"   Total ejercicios: {stats['total_exercises']}")
        print(f"   Por dificultad: {stats['by_difficulty']}")
        print(f"   Por lenguaje: {stats.get('by_language', {})}")
        print(f"   Tiempo total: {stats['total_time_hours']} horas")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("TEST: Verificación de ejercicios del catálogo")
    print("="*80)
    
    resultados = []
    
    # Test 1: Ejercicio disponible
    resultados.append(test_ejercicio_disponible())
    
    # Test 2: Materias (puede fallar por auth)
    result_materias = test_materias_disponibles()
    if result_materias is not None:
        resultados.append(result_materias)
    
    # Test 3: Stats
    resultados.append(test_stats())
    
    print("\n" + "="*80)
    if all(resultados):
        print("✅ TODOS LOS TESTS DISPONIBLES PASARON")
        print("\nNOTA: Para probar el endpoint /training/iniciar necesitas:")
        print("  1. Estar autenticado")
        print("  2. Enviar: POST /api/v1/training/iniciar")
        print("     Body: {\"materia_codigo\": \"PYTHON\", \"tema_id\": \"U1-VAR-01\"}")
    else:
        print(f"⚠️  ALGUNOS TESTS FALLARON ({sum(resultados)}/{len(resultados)} pasaron)")
    print("="*80)

