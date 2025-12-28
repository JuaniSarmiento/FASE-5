"""
Test para verificar que el ejercicio de temperaturas ahora funciona
"""
import sys
import os
import subprocess
import tempfile
import time
import re

def execute_python_code(code: str, test_input: str, timeout_seconds: int = 5) -> tuple[str, str, int]:
    """Ejecuta código Python de forma segura."""
    sandbox_wrapper = '''
import sys
try:
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, ({timeout}, {timeout} + 1))
except (ImportError, AttributeError, ValueError):
    pass

import math
restricted_builtins = {{
    'print': print, 'input': input, 'math': math,
    'len': len, 'range': range, 'int': int, 'float': float,
    'str': str, 'bool': bool, 'list': list, 'dict': dict,
    'set': set, 'tuple': tuple, 'abs': abs, 'max': max,
    'min': min, 'sum': sum, 'sorted': sorted, 'reversed': reversed,
    'enumerate': enumerate, 'zip': zip, 'map': map,
    'filter': filter, 'any': any, 'all': all,
    'isinstance': isinstance, 'type': type, 'round': round,
    'pow': pow, 'divmod': divmod, 'chr': chr, 'ord': ord,
    'True': True, 'False': False, 'None': None,
}}
__builtins__ = restricted_builtins
'''.format(timeout=timeout_seconds)

    sandboxed_code = sandbox_wrapper + code

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(sandboxed_code)
        temp_file = f.name

    try:
        start_time = time.time()
        result = subprocess.run(
            ['python', '-I', temp_file],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env={'PATH': os.environ.get('PATH', ''), 'PYTHONDONTWRITEBYTECODE': '1'}
        )
        execution_time = int((time.time() - start_time) * 1000)
        return result.stdout.strip(), result.stderr.strip(), execution_time
    except subprocess.TimeoutExpired:
        return "", "Error: Tiempo de ejecución excedido", timeout_seconds * 1000
    except Exception as e:
        return "", f"Error: {str(e)}", 0
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


# Código del usuario (correcto)
codigo_usuario = '''# NO TOCAR ESTAS LÍNEAS
# Ejercicio: Análisis de Temperaturas
temperaturas = [23.5, 25.1, 22.8, 24.3, 26.0, 23.9, 25.5]

# TODO: Calcula el promedio
total_temp = 0
for temp in temperaturas:
    total_temp += temp

promedio = total_temp / len(temperaturas)

# TODO: Encuentra máxima y mínima
temp_max = temperaturas[0]
temp_min = temperaturas[0]

for temp in temperaturas:
    if temp > temp_max:
        temp_max = temp
    if temp < temp_min:
        temp_min = temp

# TODO: Cuenta días sobre el promedio
dias_sobre_promedio = 0
for temp in temperaturas:
    if temp > promedio:
        dias_sobre_promedio += 1

# TODO: Imprime el reporte
print("=== REPORTE METEOROLÓGICO ===")
print(f"Promedio: {promedio:.2f}°C")
print(f"Máxima: {temp_max}°C")
print(f"Mínima: {temp_min}°C")
print(f"Días sobre promedio: {dias_sobre_promedio}")
'''

print("\n" + "="*70)
print("TEST CORREGIDO: Análisis de Temperaturas")
print("="*70)

# Test CORREGIDO del JSON
test_corregido = {
    "input": "",
    "expected": ".*Promedio:\\s*24\\.4[34]°C.*Máxima:\\s*26\\.0°C.*Mínima:\\s*22\\.8°C.*Días sobre promedio:\\s*3.*"
}

print(f"\nTest configurado:")
print(f"  Input: {repr(test_corregido['input'])}")
print(f"  Expected (regex): {test_corregido['expected']}")

# Ejecutar código
stdout, stderr, exec_time = execute_python_code(codigo_usuario, test_corregido['input'])

if stderr:
    print(f"\n❌ ERROR: {stderr}")
else:
    print(f"\nOutput generado:")
    print("-" * 40)
    print(stdout)
    print("-" * 40)
    
    # Verificar con regex (CON re.DOTALL)
    if re.search(test_corregido['expected'], stdout, re.DOTALL):
        print(f"\n✅ TEST PASADO (tiempo: {exec_time}ms)")
        print("\n🎉 El test ahora funciona correctamente!")
    else:
        print(f"\n❌ TEST FALLÓ")
        print(f"\nPattern esperado: {test_corregido['expected']}")
        print(f"Output recibido: {repr(stdout)}")

print("\n" + "="*70)
print("RESUMEN")
print("="*70)
print("✅ Test ANTES (incorrecto):")
print("   promedio == 24.44 and temp_max == 26.0 and ...")
print("   ❌ Intentaba evaluar variables fuera de scope")
print()
print("✅ Test AHORA (correcto):")
print("   .*Promedio:\\\\s*24\\\\.4[34]°C.*Máxima:\\\\s*26\\\\.0°C...")
print("   ✅ Verifica el OUTPUT con regex pattern")
print("="*70 + "\n")
