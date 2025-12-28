# Fix: Ejercicio 6 - Tabla de Multiplicar

## 🐛 Problema

El ejercicio SEC-06 (Tabla de Multiplicar) no pasaba los tests a pesar de que el código era correcto:

```python
numero = int(input("Ingrese un número entero: "))

print(f"""
{numero} x 0 = {numero * 0}
{numero} x 1 = {numero * 1}
{numero} x 2 = {numero * 2}
# ... más líneas
{numero} x 9 = {numero * 9}
""")
```

### Output Generado (correcto):
```
Ingrese un número entero: 
5 x 0 = 0
5 x 1 = 5
5 x 2 = 10
5 x 3 = 15
...
5 x 9 = 45
```

### Expected Pattern:
```python
".*5 x 0 = 0.*5 x 1 = 5.*5 x 9 = 45.*"
```

## 🔍 Causa Raíz

El sistema usaba `re.search()` **sin el flag `re.DOTALL`**, lo que causaba que:

- El metacarácter `.` (punto) **NO coincidiera con saltos de línea** (`\n`)
- El patrón `.*` se detenía en cada `\n`
- Los patterns que intentaban coincidir texto a través de múltiples líneas **fallaban**

### Demostración:

```python
output = "Línea 1\nLínea 2\nLínea 3"
pattern = ".*Línea 1.*Línea 3.*"

# SIN re.DOTALL
re.search(pattern, output)  # ❌ None - No coincide

# CON re.DOTALL
re.search(pattern, output, re.DOTALL)  # ✅ Match - Coincide
```

## ✅ Solución

**Archivo**: `backend/api/routers/training.py` (línea ~779)

```python
# ANTES (❌)
if re.search(expected_str, actual_output):
    tests_passed += 1

# DESPUÉS (✅)
if re.search(expected_str, actual_output, re.DOTALL):
    tests_passed += 1
```

## 📊 Impacto

Este cambio afecta a **TODOS** los ejercicios que:

1. ✅ Generan output multilínea
2. ✅ Usan patterns regex con `.*` para coincidir entre líneas
3. ✅ Tienen tests que verifican múltiples líneas de output

### Ejercicios Beneficiados:

| ID | Ejercicio | Descripción |
|----|-----------|-------------|
| SEC-06 | Tabla de Multiplicar | Imprime 10 líneas (0 a 9) |
| SEC-03 | Datos Personales | Puede tener múltiples líneas |
| Futuros | Cualquier ejercicio multilínea | Ahora funcionará correctamente |

## 🧪 Verificación

### Test Manual:

```bash
# Ejecutar test específico
python test_tabla_multiplicar.py

# Ejecutar test de regex
python test_regex_dotall.py
```

### Resultado Esperado:

```
✅ PASADO: Tabla del 5 (2/2 tests)
✅ PASADO: Tabla del 3 (2/2 tests)
```

## 📚 Documentación

El cambio está documentado en:
- ✅ `GUIA_TESTS_INPUT.md` - Sección "Outputs Multilínea"
- ✅ `GUIA_TESTS_INPUT.md` - Troubleshooting

## 🔐 Seguridad

✅ Este cambio **NO afecta la seguridad** del sandbox:
- Solo modifica cómo se comparan patterns regex
- No cambia la ejecución del código del usuario
- Mantiene todas las restricciones existentes

## 🎯 Conclusión

El ejercicio SEC-06 ahora funciona correctamente. El flag `re.DOTALL` permite que los patterns regex coincidan correctamente con output multilínea, que es esencial para ejercicios que imprimen tablas, listas, o cualquier formato con múltiples líneas.

---

**Fecha**: 28 de diciembre de 2025  
**Archivos Modificados**:
1. `backend/api/routers/training.py` - Agregado `re.DOTALL`
2. `GUIA_TESTS_INPUT.md` - Documentación actualizada
3. `test_tabla_multiplicar.py` - Test de verificación (nuevo)
4. `test_regex_dotall.py` - Test de demostración (nuevo)
