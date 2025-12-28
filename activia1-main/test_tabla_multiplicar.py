"""
Test específico para el ejercicio de Tabla de Multiplicar
"""
import sys
import os
import subprocess
import tempfile
import time
import re

def execute_python_code(code: str, test_input: str, timeout_seconds: int = 5) -> tuple[str, str, int]:
    """
    Ejecuta código Python de forma segura con restricciones de sandbox.
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


def test_tabla_multiplicar():
    """Test del ejercicio SEC-06: Tabla de Multiplicar"""
    
    # Código original (con líneas vacías)
    codigo_original = '''numero = int(input("Ingrese un número entero: "))

print(f"""
{numero} x 0 = {numero * 0}
{numero} x 1 = {numero * 1}
{numero} x 2 = {numero * 2}
{numero} x 3 = {numero * 3}
{numero} x 4 = {numero * 4}
{numero} x 5 = {numero * 5}
{numero} x 6 = {numero * 6}
{numero} x 7 = {numero * 7}
{numero} x 8 = {numero * 8}
{numero} x 9 = {numero * 9}
""")'''

    # Código alternativo (sin líneas vacías)
    codigo_alternativo = '''numero = int(input("Ingrese un número entero: "))

print(f"""{numero} x 0 = {numero * 0}
{numero} x 1 = {numero * 1}
{numero} x 2 = {numero * 2}
{numero} x 3 = {numero * 3}
{numero} x 4 = {numero * 4}
{numero} x 5 = {numero * 5}
{numero} x 6 = {numero * 6}
{numero} x 7 = {numero * 7}
{numero} x 8 = {numero * 8}
{numero} x 9 = {numero * 9}""")'''

    tests = [
        {
            "nombre": "Test 1: Tabla del 5",
            "input": "5\n",
            "expected_pattern": ".*5 x 0 = 0.*5 x 1 = 5.*5 x 9 = 45.*"
        },
        {
            "nombre": "Test 2: Tabla del 3",
            "input": "3\n",
            "expected_pattern": ".*3 x 0 = 0.*3 x 5 = 15.*3 x 9 = 27.*"
        }
    ]
    
    print("\n" + "="*70)
    print("Probando ejercicio: Tabla de Multiplicar (SEC-06)")
    print("="*70)
    
    for version_name, codigo in [("ORIGINAL (con líneas vacías)", codigo_original), 
                                   ("ALTERNATIVO (sin líneas vacías)", codigo_alternativo)]:
        print(f"\n{'='*70}")
        print(f"Versión: {version_name}")
        print(f"{'='*70}")
        print(f"\nCódigo:")
        print("-" * 40)
        print(codigo)
        print("-" * 40)
        
        tests_passed = 0
        for test in tests:
            print(f"\n{test['nombre']}")
            print(f"  Input: {test['input'].strip()}")
            
            stdout, stderr, exec_time = execute_python_code(
                codigo,
                test['input'],
                timeout_seconds=5
            )
            
            if stderr:
                print(f"  ❌ ERROR: {stderr}")
            else:
                print(f"  Output:")
                print("  " + "\n  ".join(stdout.split("\n")))
                print(f"\n  Expected pattern: {test['expected_pattern']}")
                
                # Probar el pattern
                if re.search(test['expected_pattern'], stdout, re.DOTALL):
                    print(f"  ✅ PASADO (tiempo: {exec_time}ms)")
                    tests_passed += 1
                else:
                    print(f"  ❌ FALLÓ - Pattern no coincide")
                    # Mostrar qué partes del pattern no coinciden
                    patterns = test['expected_pattern'].replace(".*", "|").split("|")
                    patterns = [p.strip() for p in patterns if p.strip()]
                    print(f"  Buscando partes:")
                    for p in patterns:
                        if p in stdout:
                            print(f"    ✅ Encontrado: '{p}'")
                        else:
                            print(f"    ❌ No encontrado: '{p}'")
        
        print(f"\n{'-'*70}")
        print(f"Resultado: {tests_passed}/{len(tests)} tests pasados")
        print(f"{'-'*70}")


if __name__ == "__main__":
    test_tabla_multiplicar()
