# Guía: Tests para Ejercicios con input()

## Problema Solucionado

Los ejercicios que usan `input()` para obtener datos del usuario necesitaban tests que pudieran simular esa entrada. Antes, `input()` estaba bloqueado por seguridad y los tests fallaban.

## Solución Implementada

### 1. **Permitir `input()` en el sandbox** ✅

**Archivo**: `backend/api/routers/exercises.py`

Se realizaron los siguientes cambios:

```python
# ANTES: input() estaba bloqueado
DANGEROUS_PATTERNS = [
    '__import__', 'exec(', 'eval(', 'compile(',
    'open(', 'file(', 'input(',  # ❌ Bloqueado
    'globals(', 'locals(', 'vars(',
    # ...
]

# DESPUÉS: input() ahora está permitido
DANGEROUS_PATTERNS = [
    '__import__', 'exec(', 'eval(', 'compile(',
    'open(', 'file(',
    # 'input(' - PERMITIDO: necesario para ejercicios de entrada del usuario ✅
    'globals(', 'locals(', 'vars(',
    # ...
]
```

### 2. **Agregar `input` y `math` a builtins permitidos** ✅

```python
# Restrict builtins
import math
restricted_builtins = {
    'print': print,
    'input': input,  # ✅ Necesario para ejercicios de entrada del usuario
    'math': math,    # ✅ Necesario para ejercicios matemáticos
    'len': len,
    'range': range,
    # ... otros builtins seguros
}
```

### 3. **Corregir import de `resource` para Windows** ✅

```python
# ANTES: resource se importaba directamente (falla en Windows)
import sys
import resource

# DESPUÉS: import condicional
import sys

try:
    import resource
    # ... configurar límites
except (ImportError, AttributeError, ValueError):
    pass  # Windows no tiene el módulo resource
```

## Cómo Funciona

### Simulación de Input

Cuando se ejecuta un test, el sistema:

1. **Toma el campo `input` del test** (ej: `"Marcos\n"`)
2. **Lo pasa como stdin al subprocess** usando `subprocess.run(..., input=test_input)`
3. **El código del usuario llama `input()`** y recibe automáticamente ese valor
4. **Se captura el output** y se compara con el `expected`

### Ejemplo de Test

```python
{
    "test_number": 1,
    "description": "Verifica saludo con nombre 'Marcos'",
    "input": "Marcos\n",           # ✅ Valor simulado para input()
    "expected": ".*Hola Marcos.*", # ✅ Patrón regex esperado en output
    "is_hidden": False,
    "timeout_seconds": 5
}
```

### Código del Usuario

```python
nombre = input("Ingrese su nombre: ")
print(f"Hola {nombre}!")
```

### Flujo de Ejecución

```
Test Input: "Marcos\n"
    ↓
subprocess.run(..., input="Marcos\n")
    ↓
Código ejecuta: nombre = input("Ingrese su nombre: ")
    ↓
input() recibe "Marcos" automáticamente
    ↓
Código imprime: "Hola Marcos!"
    ↓
Output capturado: "Ingrese su nombre: Hola Marcos!"
    ↓
Se compara con expected usando regex: ".*Hola Marcos.*"
    ↓
✅ Test PASADO
```

## Tipos de Tests Soportados

### 1. **Input Simple** (1 valor)

```python
{
    "input": "Marcos\n",
    "expected": ".*Hola Marcos.*"
}
```

### 2. **Múltiples Inputs** (varios valores separados por `\n`)

```python
{
    "input": "Juan\nPerez\n25\nArgentina\n",
    "expected": ".*Soy Juan Perez.*25.*Argentina.*"
}
```

### 3. **Input Numérico**

```python
{
    "input": "5\n",
    "expected": ".*78\\.5.*31\\.4.*"  # área y perímetro
}
```

### 4. **Input con Decimales**

```python
{
    "input": "2.5\n",
    "expected": ".*19\\.6.*15\\.7.*"
}
```

## Patrones Regex en Expected

El campo `expected` puede usar **expresiones regulares** para hacer coincidencias flexibles.

⚠️ **IMPORTANTE**: El sistema usa `re.search(..., re.DOTALL)` para que el `.` coincida con saltos de línea.

| Patrón | Significado | Ejemplo |
|--------|-------------|---------|
| `.*` | Cualquier texto (incluye `\n`) | `".*Hola.*"` coincide con "Ingrese:\nHola Marcos!" |
| `\\.` | Punto literal | `"78\\.5"` coincide con "78.5" |
| `\\d+` | Uno o más dígitos | `"\\d+ años"` coincide con "25 años" |
| `[A-Z]` | Una letra mayúscula | `"Hola [A-Z]\\w+"` coincide con "Hola Marcos" |

### Outputs Multilínea

Para ejercicios que generan **múltiples líneas**, usa `.*` entre las partes que quieres verificar:

```python
# ✅ CORRECTO - verifica líneas específicas en orden
"expected": ".*5 x 0 = 0.*5 x 1 = 5.*5 x 9 = 45.*"

# Este pattern coincide con:
# """
# Ingrese un número: 
# 5 x 0 = 0
# 5 x 1 = 5
# 5 x 2 = 10
# ...
# 5 x 9 = 45
# """
```

### Por Qué re.DOTALL es Importante

```python
# SIN re.DOTALL (❌ MALO):
# El . NO coincide con \n, por lo que .* se detiene en cada salto de línea
re.search(".*5 x 0 = 0.*5 x 1 = 5.*", output)  # ❌ Falla en output multilínea

# CON re.DOTALL (✅ BUENO):
# El . SÍ coincide con \n, por lo que .* puede atravesar múltiples líneas
re.search(".*5 x 0 = 0.*5 x 1 = 5.*", output, re.DOTALL)  # ✅ Funciona
```

## Agregar Más Módulos Seguros

Si necesitas permitir otros módulos Python seguros (como `random`, `datetime`, etc.):

### En `backend/api/routers/exercises.py`:

```python
# Restrict builtins
import math
import random  # Agregar aquí el módulo

restricted_builtins = {
    'print': print,
    'input': input,
    'math': math,
    'random': random,  # Y aquí también
    # ... resto de builtins
}
```

### Módulos Seguros Recomendados:

- ✅ `math` - Operaciones matemáticas
- ✅ `random` - Números aleatorios (con semilla fija en tests)
- ✅ `datetime` - Manejo de fechas y horas
- ✅ `collections` - Estructuras de datos avanzadas
- ✅ `itertools` - Herramientas para iteradores
- ✅ `functools` - Programación funcional
- ✅ `re` - Expresiones regulares
- ✅ `json` - Manejo de JSON
- ✅ `string` - Utilidades de strings

### Módulos BLOQUEADOS (por seguridad):

- ❌ `os`, `sys`, `subprocess` - Acceso al sistema operativo
- ❌ `socket`, `requests`, `urllib` - Acceso a red
- ❌ `pickle`, `marshal` - Serialización insegura
- ❌ `ctypes`, `cffi` - Acceso a código nativo
- ❌ `multiprocessing`, `threading` - Control de procesos

## Testing Manual

Para probar manualmente los ejercicios con input:

```bash
# Ejecutar script de prueba
python test_input_exercises.py
```

Esto probará:
- ✅ Saludo Personalizado (SEC-02)
- ✅ Datos Personales (SEC-03)
- ✅ Área y Perímetro del Círculo (SEC-04)

## Verificación en Backend

Para verificar que los tests funcionan en el sistema completo:

```bash
# 1. Arrancar el backend
cd backend
python -m uvicorn api.main:app --reload

# 2. Hacer una prueba de ejecución
curl -X POST "http://localhost:8000/api/v1/training/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_id": "SEC-02",
    "codigo_usuario": "nombre = input(\"Nombre: \")\nprint(f\"Hola {nombre}!\")"
  }'
```

## Estructura de Tests en seed_secuenciales.py

```python
TESTS_SECUENCIALES = {
    "SEC-02": [
        {
            "test_number": 1,
            "description": "Verifica saludo con nombre 'Marcos'",
            "input": "Marcos\n",           # ✅ Input simulado
            "expected": ".*Hola Marcos.*", # ✅ Pattern regex
            "is_hidden": False,            # Visible para estudiante
            "timeout_seconds": 5
        },
        {
            "test_number": 2,
            "description": "Verifica saludo con nombre 'Ana'",
            "input": "Ana\n",
            "expected": ".*Hola Ana.*",
            "is_hidden": True,             # Test oculto
            "timeout_seconds": 5
        }
    ]
}
```

## Beneficios de Esta Solución

1. ✅ **Seguro**: Mantiene el sandbox activo con restricciones
2. ✅ **Automático**: Los tests se ejecutan sin intervención manual
3. ✅ **Flexible**: Soporta regex para comparaciones complejas
4. ✅ **Multiplataforma**: Funciona en Windows, Linux y Mac
5. ✅ **Extensible**: Fácil agregar más módulos seguros
6. ✅ **Tests Ocultos**: Algunos tests no se muestran al estudiante
7. ✅ **Feedback Claro**: Mensajes de error descriptivos

## Troubleshooting

### Problema: Test falla con "Error de seguridad: Patrón 'input(' no permitido"

**Solución**: Verifica que `'input('` esté comentado en `DANGEROUS_PATTERNS`:

```python
# 'input(' - PERMITIDO: necesario para ejercicios de entrada del usuario
```

### Problema: "ModuleNotFoundError: No module named 'resource'"

**Solución**: Verifica que el import sea condicional:

```python
try:
    import resource
    # ...
except (ImportError, AttributeError, ValueError):
    pass
```

### Problema: Test falla con "Error: import 'math' no permitido"

**Solución**: Verifica que `math` NO esté en `DANGEROUS_IMPORTS` y SÍ esté en `restricted_builtins`.

### Problema: Expected no coincide pero el output parece correcto

**Solución**: Usa patrones regex más flexibles:

```python
# ❌ Muy estricto
"expected": "Hola Marcos!"

# ✅ Flexible
"expected": ".*Hola Marcos.*"
```

### Problema: Tests fallan en ejercicios multilínea (ej: Tabla de Multiplicar)

**Causa**: El sistema usaba `re.search()` sin el flag `re.DOTALL`, lo que hacía que `.` no coincidiera con saltos de línea (`\n`).

**Solución**: Se agregó `re.DOTALL` al `re.search()` en `backend/api/routers/training.py`:

```python
# ANTES (❌)
if re.search(expected_str, actual_output):

# DESPUÉS (✅)
if re.search(expected_str, actual_output, re.DOTALL):
```

**Ejemplo**: Ejercicio SEC-06 (Tabla de Multiplicar)
```python
# Este código ahora pasa todos los tests:
numero = int(input("Ingrese un número entero: "))
print(f"""
{numero} x 0 = {numero * 0}
{numero} x 1 = {numero * 1}
...
{numero} x 9 = {numero * 9}
""")

# Test que verifica:
{
    "expected": ".*5 x 0 = 0.*5 x 1 = 5.*5 x 9 = 45.*"  # ✅ Funciona con re.DOTALL
}
```

## Próximos Pasos

Si necesitas agregar más tipos de ejercicios:

1. **Ejercicios con archivos** (simulados en memoria)
2. **Ejercicios con random** (usando semilla fija)
3. **Ejercicios con fechas** (usando `datetime`)
4. **Ejercicios con estructuras de datos** (`collections`)

Consulta este documento y adapta la configuración según necesites.

---

**Última actualización**: 28 de diciembre de 2025  
**Archivos modificados**:
- `backend/api/routers/exercises.py`
- `test_input_exercises.py` (nuevo)
