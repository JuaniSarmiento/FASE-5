"""
Test específico para el ejercicio de Análisis de Temperaturas
"""
import sys
import os
import subprocess
import tempfile
import time
import re

def execute_python_code(code: str, test_input: str, timeout_seconds: int = 5) -> tuple[str, str, int]:
    """
    Ejecuta código Python de forma segura.
    """
    DANGEROUS_IMPORTS = [
        'os', 'subprocess', 'sys', 'shutil', 'pathlib',
        'socket', 'requests', 'urllib', 'http',
        'multiprocessing', 'threading', 'asyncio',
        'pickle', 'marshal', 'shelve',
        'ctypes', 'cffi', 'importlib',
        'builtins', '__builtins__',
        'code', 'codeop', 'compile',
    ]

    DANGEROUS_PATTERNS = [
        '__import__', 'exec(', 'eval(', 'compile(',
        'open(', 'file(',
        'globals(', 'locals(', 'vars(',
        'getattr(', 'setattr(', 'delattr(',
        '__class__', '__bases__', '__subclasses__',
        '__mro__', '__code__', '__globals__',
        'breakpoint(', 'help(',
    ]

    code_lower = code.lower()
    for dangerous_import in DANGEROUS_IMPORTS:
        patterns = [
            f'import {dangerous_import}',
            f'from {dangerous_import}',
            f'__import__("{dangerous_import}"',
            f"__import__('{dangerous_import}'",
        ]
        for pattern in patterns:
            if pattern.lower() in code_lower:
                return "", f"Error de seguridad: Import '{dangerous_import}' no permitido", 0

    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in code_lower:
            return "", f"Error de seguridad: Patrón '{pattern}' no permitido", 0

    sandbox_wrapper = '''
import sys

try:
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, ({timeout}, {timeout} + 1))
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
except (ImportError, AttributeError, ValueError):
    pass

import math
restricted_builtins = {{
    'print': print,
    'input': input,
    'math': math,
    'len': len,
    'range': range,
    'int': int,
    'float': float,
    'str': str,
    'bool': bool,
    'list': list,
    'dict': dict,
    'set': set,
    'tuple': tuple,
    'abs': abs,
    'max': max,
    'min': min,
    'sum': sum,
    'sorted': sorted,
    'reversed': reversed,
    'enumerate': enumerate,
    'zip': zip,
    'map': map,
    'filter': filter,
    'any': any,
    'all': all,
    'isinstance': isinstance,
    'type': type,
    'round': round,
    'pow': pow,
    'divmod': divmod,
    'chr': chr,
    'ord': ord,
    'hex': hex,
    'bin': bin,
    'oct': oct,
    'format': format,
    'repr': repr,
    'hash': hash,
    'id': id,
    'slice': slice,
    'iter': iter,
    'next': next,
    'True': True,
    'False': False,
    'None': None,
    'Exception': Exception,
    'ValueError': ValueError,
    'TypeError': TypeError,
    'IndexError': IndexError,
    'KeyError': KeyError,
    'ZeroDivisionError': ZeroDivisionError,
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
            env={
                'PATH': os.environ.get('PATH', ''),
                'PYTHONDONTWRITEBYTECODE': '1',
                'PYTHONUNBUFFERED': '1',
            }
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


def test_temperaturas():
    """Test del ejercicio de Análisis de Temperaturas"""
    
    # Código del usuario
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
    print("Probando ejercicio: Análisis de Temperaturas (U1-LOOP-01)")
    print("="*70)
    print(f"\nCódigo del usuario:")
    print("-" * 40)
    print(codigo_usuario)
    print("-" * 40)
    
    # Test del JSON (esperado)
    test_json = {
        "input": "",
        "expected": "promedio == 24.44 and temp_max == 26.0 and temp_min == 22.8 and dias_sobre_promedio == 3"
    }
    
    print(f"\n{'='*70}")
    print("TEST CONFIGURADO EN JSON (hidden_tests)")
    print(f"{'='*70}")
    print(f"Input: {repr(test_json['input'])}")
    print(f"Expected: {test_json['expected']}")
    
    # Ejecutar código
    stdout, stderr, exec_time = execute_python_code(
        codigo_usuario,
        test_json['input'],
        timeout_seconds=5
    )
    
    if stderr:
        print(f"\n❌ ERROR: {stderr}")
        return False
    
    print(f"\nOutput generado:")
    print("-" * 40)
    print(stdout)
    print("-" * 40)
    
    # Intentar evaluar el expected (como lo haría el backend)
    print(f"\n{'='*70}")
    print("EVALUANDO EXPECTED")
    print(f"{'='*70}")
    
    # El expected intenta evaluar variables que no están en scope
    print(f"\n⚠️ PROBLEMA: El expected intenta evaluar:")
    print(f"   {test_json['expected']}")
    print(f"\nPero estas variables (promedio, temp_max, etc.) NO están disponibles")
    print(f"porque el código solo genera OUTPUT con print().")
    
    # Lo que el backend debería hacer es verificar el output
    print(f"\n{'='*70}")
    print("SOLUCIÓN: Verificar el OUTPUT en lugar de variables")
    print(f"{'='*70}")
    
    # Tests correctos basados en output
    expected_patterns = [
        ("Promedio correcto", r"Promedio:\s*24\.4[34]°C"),
        ("Máxima correcta", r"Máxima:\s*26\.0°C"),
        ("Mínima correcta", r"Mínima:\s*22\.8°C"),
        ("Días sobre promedio", r"Días sobre promedio:\s*3"),
    ]
    
    tests_passed = 0
    for desc, pattern in expected_patterns:
        if re.search(pattern, stdout):
            print(f"  ✅ {desc}")
            tests_passed += 1
        else:
            print(f"  ❌ {desc} - Pattern: {pattern}")
    
    print(f"\n{'='*70}")
    print(f"Resultado: {tests_passed}/{len(expected_patterns)} verificaciones pasadas")
    print(f"{'='*70}")
    
    # Valores esperados
    print(f"\n{'='*70}")
    print("VALORES ESPERADOS VS CALCULADOS")
    print(f"{'='*70}")
    temps = [23.5, 25.1, 22.8, 24.3, 26.0, 23.9, 25.5]
    promedio_real = sum(temps) / len(temps)
    max_real = max(temps)
    min_real = min(temps)
    dias_real = sum(1 for t in temps if t > promedio_real)
    
    print(f"Promedio esperado: 24.44 (real: {promedio_real:.2f})")
    print(f"Máxima esperada: 26.0 (real: {max_real})")
    print(f"Mínima esperada: 22.8 (real: {min_real})")
    print(f"Días sobre promedio: 3 (real: {dias_real})")
    
    return tests_passed == len(expected_patterns)


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" TEST DE EJERCICIO: ANÁLISIS DE TEMPERATURAS")
    print("="*70)
    
    resultado = test_temperaturas()
    
    print("\n" + "="*70)
    print(" CONCLUSIÓN")
    print("="*70)
    if resultado:
        print("✅ El código es CORRECTO y genera el output esperado")
    else:
        print("❌ Hay problemas con el código")
    
    print("\n⚠️ PROBLEMA IDENTIFICADO:")
    print("   El test en el JSON está mal configurado.")
    print("   Intenta evaluar variables que no están en scope.")
    print("\n✅ SOLUCIÓN:")
    print("   Cambiar el test para verificar el OUTPUT con regex patterns.")
    print("="*70 + "\n")
