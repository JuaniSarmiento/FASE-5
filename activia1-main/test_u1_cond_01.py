"""
Test para verificar que el ejercicio U1-COND-01 funciona correctamente
"""

# Código del estudiante
def obtener_letra(nota):
    """
    Convierte una nota numérica a letra.
    Args:
        nota (int/float): Calificación entre 0-100
    Returns:
        str: Letra (A, B, C, D, F) o "INVALID"
    """
    # Validar que la nota esté en el rango correcto
    if nota < 0 or nota > 100:
        return "INVALID"
    
    # Lógica de conversión
    if nota >= 90:
        return "A"
    elif nota >= 80:
        return "B"
    elif nota >= 70:
        return "C"
    elif nota >= 60:
        return "D"
    else:
        return "F"

# Tests del ejercicio
tests = [
    {"input": "obtener_letra(95)", "expected": "A"},
    {"input": "obtener_letra(82)", "expected": "B"},
    {"input": "obtener_letra(75)", "expected": "C"},
    {"input": "obtener_letra(65)", "expected": "D"},
    {"input": "obtener_letra(45)", "expected": "F"},
    {"input": "obtener_letra(105)", "expected": "INVALID"},
    {"input": "obtener_letra(-10)", "expected": "INVALID"},
]

print("="*80)
print("TEST: Ejercicio U1-COND-01 - Sistema de Calificaciones")
print("="*80)

tests_passed = 0
tests_total = len(tests)

for i, test in enumerate(tests, 1):
    test_input = test['input']
    expected = test['expected']
    
    # Ejecutar el test
    try:
        actual = eval(test_input)
        
        if str(actual) == str(expected):
            print(f"✅ Test {i}/{tests_total} PASADO: {test_input} = {actual}")
            tests_passed += 1
        else:
            print(f"❌ Test {i}/{tests_total} FALLÓ:")
            print(f"   Input: {test_input}")
            print(f"   Esperado: {expected}")
            print(f"   Obtenido: {actual}")
    except Exception as e:
        print(f"❌ Test {i}/{tests_total} ERROR:")
        print(f"   Input: {test_input}")
        print(f"   Error: {e}")

print("\n" + "="*80)
print(f"Resultado: {tests_passed}/{tests_total} tests pasados")
if tests_passed == tests_total:
    print("✅ ¡TODOS LOS TESTS PASARON!")
else:
    print(f"⚠️  {tests_total - tests_passed} tests fallaron")
print("="*80)
