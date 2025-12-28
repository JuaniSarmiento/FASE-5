"""
Script para probar ejercicios con input()
"""
import sys
import os
import subprocess
import tempfile
import time
import re

# Copiar la función execute_python_code directamente aquí para evitar imports complejos
def execute_python_code(code: str, test_input: str, timeout_seconds: int = 5) -> tuple[str, str, int]:
    """
    Ejecuta código Python de forma segura con restricciones de sandbox.
    """
    # ==========================================================================
    # SECURITY: Validate code before execution
    # ==========================================================================
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
        # 'input(' - PERMITIDO: necesario para ejercicios de entrada del usuario
        'globals(', 'locals(', 'vars(',
        'getattr(', 'setattr(', 'delattr(',
        '__class__', '__bases__', '__subclasses__',
        '__mro__', '__code__', '__globals__',
        'breakpoint(', 'help(',
    ]

    # Check for dangerous imports
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

    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in code_lower:
            return "", f"Error de seguridad: Patrón '{pattern}' no permitido", 0

    # ==========================================================================
    # Create sandboxed execution script
    # ==========================================================================
    sandbox_wrapper = '''
import sys

# Limit resources (Linux/Mac only)
try:
    import resource
    # Limit memory to 50MB
    resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024))
    # Limit CPU time to timeout + 1 second
    resource.setrlimit(resource.RLIMIT_CPU, ({timeout}, {timeout} + 1))
    # Disable file creation
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    # Limit number of processes
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
except (ImportError, AttributeError, ValueError):
    pass  # Windows doesn't have resource module or doesn't support some limits

# Restrict builtins
restricted_builtins = {{
    'print': print,
    'input': input,  # Necesario para ejercicios de entrada del usuario
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

# Allow safe modules
import math
restricted_builtins['math'] = math

# User code below (executed with restricted builtins)
__builtins__ = restricted_builtins

'''.format(timeout=timeout_seconds)

    sandboxed_code = sandbox_wrapper + code

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(sandboxed_code)
        temp_file = f.name

    try:
        start_time = time.time()
        result = subprocess.run(
            ['python', '-I', temp_file],  # -I: isolated mode
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env={  # Minimal environment
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

def test_saludo_personalizado():
    """Prueba el ejercicio SEC-02: Saludo Personalizado"""
    
    # Código del usuario (correcto)
    codigo_usuario = '''nombre = input("Ingrese su nombre: ")
print(f"Hola {nombre}!")'''
    
    # Tests
    tests = [
        {
            "nombre": "Test 1: Marcos",
            "input": "Marcos\n",
            "expected_pattern": "Hola Marcos"
        },
        {
            "nombre": "Test 2: Ana",
            "input": "Ana\n",
            "expected_pattern": "Hola Ana"
        },
        {
            "nombre": "Test 3: Pedro",
            "input": "Pedro\n",
            "expected_pattern": "Hola Pedro"
        }
    ]
    
    print("\n" + "="*70)
    print("Probando ejercicio: Saludo Personalizado (SEC-02)")
    print("="*70)
    print(f"\nCódigo del usuario:")
    print("-" * 40)
    print(codigo_usuario)
    print("-" * 40)
    
    tests_passed = 0
    for test in tests:
        print(f"\n{test['nombre']}")
        print(f"  Input: {test['input'].strip()}")
        
        stdout, stderr, exec_time = execute_python_code(
            codigo_usuario,
            test['input'],
            timeout_seconds=5
        )
        
        if stderr:
            print(f"  ❌ ERROR: {stderr}")
        else:
            print(f"  Output: {stdout}")
            if test['expected_pattern'] in stdout:
                print(f"  ✅ PASADO (tiempo: {exec_time}ms)")
                tests_passed += 1
            else:
                print(f"  ❌ FALLÓ - Expected: '{test['expected_pattern']}'")
    
    print(f"\n{'='*70}")
    print(f"Resultado: {tests_passed}/{len(tests)} tests pasados")
    print(f"{'='*70}\n")
    
    return tests_passed == len(tests)


def test_datos_personales():
    """Prueba el ejercicio SEC-03: Datos Personales"""
    
    # Código del usuario (correcto)
    codigo_usuario = '''nombre = input("Nombre: ")
apellido = input("Apellido: ")
edad = input("Edad: ")
lugar = input("Lugar: ")
print(f"Soy {nombre} {apellido}, tengo {edad} años y vivo en {lugar}.")'''
    
    # Tests
    tests = [
        {
            "nombre": "Test 1: Juan Perez",
            "input": "Juan\nPerez\n25\nArgentina\n",
            "expected_patterns": ["Soy Juan Perez", "25", "Argentina"]
        },
        {
            "nombre": "Test 2: Maria Gomez",
            "input": "Maria\nGomez\n30\nEspaña\n",
            "expected_patterns": ["Soy Maria Gomez", "30", "España"]
        }
    ]
    
    print("\n" + "="*70)
    print("Probando ejercicio: Datos Personales (SEC-03)")
    print("="*70)
    print(f"\nCódigo del usuario:")
    print("-" * 40)
    print(codigo_usuario)
    print("-" * 40)
    
    tests_passed = 0
    for test in tests:
        print(f"\n{test['nombre']}")
        print(f"  Input: {repr(test['input'])}")
        
        stdout, stderr, exec_time = execute_python_code(
            codigo_usuario,
            test['input'],
            timeout_seconds=5
        )
        
        if stderr:
            print(f"  ❌ ERROR: {stderr}")
        else:
            print(f"  Output: {stdout}")
            all_patterns_found = all(pattern in stdout for pattern in test['expected_patterns'])
            if all_patterns_found:
                print(f"  ✅ PASADO (tiempo: {exec_time}ms)")
                tests_passed += 1
            else:
                print(f"  ❌ FALLÓ - Expected patterns: {test['expected_patterns']}")
    
    print(f"\n{'='*70}")
    print(f"Resultado: {tests_passed}/{len(tests)} tests pasados")
    print(f"{'='*70}\n")
    
    return tests_passed == len(tests)


def test_circulo():
    """Prueba el ejercicio SEC-04: Área y Perímetro del Círculo"""
    
    # Código del usuario (correcto)
    codigo_usuario = '''import math
radio = float(input("Ingrese el radio: "))
area = math.pi * radio ** 2
perimetro = 2 * math.pi * radio
print(f"El área es: {area:.2f}")
print(f"El perímetro es: {perimetro:.2f}")'''
    
    # Tests
    tests = [
        {
            "nombre": "Test 1: Radio 5",
            "input": "5\n",
            "expected_patterns": ["78.5", "31.4"]
        },
        {
            "nombre": "Test 2: Radio 10",
            "input": "10\n",
            "expected_patterns": ["314", "62.8"]
        }
    ]
    
    print("\n" + "="*70)
    print("Probando ejercicio: Área y Perímetro del Círculo (SEC-04)")
    print("="*70)
    print(f"\nCódigo del usuario:")
    print("-" * 40)
    print(codigo_usuario)
    print("-" * 40)
    
    tests_passed = 0
    for test in tests:
        print(f"\n{test['nombre']}")
        print(f"  Input: {test['input'].strip()}")
        
        stdout, stderr, exec_time = execute_python_code(
            codigo_usuario,
            test['input'],
            timeout_seconds=5
        )
        
        if stderr:
            print(f"  ❌ ERROR: {stderr}")
        else:
            print(f"  Output: {stdout}")
            all_patterns_found = all(pattern in stdout for pattern in test['expected_patterns'])
            if all_patterns_found:
                print(f"  ✅ PASADO (tiempo: {exec_time}ms)")
                tests_passed += 1
            else:
                print(f"  ❌ FALLÓ - Expected patterns: {test['expected_patterns']}")
    
    print(f"\n{'='*70}")
    print(f"Resultado: {tests_passed}/{len(tests)} tests pasados")
    print(f"{'='*70}\n")
    
    return tests_passed == len(tests)


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" TEST DE EJERCICIOS CON INPUT()")
    print("="*70)
    
    results = []
    
    # Test 1: Saludo Personalizado
    results.append(("Saludo Personalizado", test_saludo_personalizado()))
    
    # Test 2: Datos Personales
    results.append(("Datos Personales", test_datos_personales()))
    
    # Test 3: Círculo (usa math + input)
    results.append(("Círculo", test_circulo()))
    
    # Resumen final
    print("\n" + "="*70)
    print(" RESUMEN FINAL")
    print("="*70)
    for exercise_name, passed in results:
        status = "✅ PASADO" if passed else "❌ FALLÓ"
        print(f"{status}: {exercise_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\n{total_passed}/{len(results)} ejercicios pasaron todos sus tests")
    print("="*70 + "\n")
