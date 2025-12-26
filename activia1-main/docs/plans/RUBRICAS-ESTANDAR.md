# Rúbricas Estándar para Ejercicios de Programación

**Fecha**: 2025-12-24
**Versión**: 1.0
**Autor**: Sistema FASE 1.5

---

## 📋 Esquema Pedagógico

Cada ejercicio de programación será evaluado mediante una rúbrica con:

### Características del Sistema

1. **3 Criterios estándar** por ejercicio (pesos suman 100%):
   - **Funcionalidad (40%)**: ¿Resuelve el problema correctamente?
   - **Calidad de código (30%)**: ¿Es legible, mantiene buenas prácticas?
   - **Robustez (30%)**: ¿Maneja casos edge, errores?

2. **4 Niveles** por criterio:
   - **Excelente** (9.0-10.0): Cumplimiento excepcional
   - **Bueno** (7.0-8.9): Cumplimiento satisfactorio
   - **Regular** (5.0-6.9): Cumplimiento básico
   - **Insuficiente** (0.0-4.9): No cumple o cumple parcialmente

3. **Sistema de pistas graduadas** (4 pistas):
   - Pista 1: 5 puntos de penalización
   - Pista 2: 10 puntos de penalización
   - Pista 3: 15 puntos de penalización
   - Pista 4: 20 puntos de penalización

4. **Cálculo de nota final**:
   ```
   Nota Final = max(0, Score_Rubrica - Penalización_Pistas)
   ```

---

## 🎯 Rúbrica Estándar: Criterio 1 - Funcionalidad (40%)

### Excelente (9.0-10.0) - 40 puntos
**Descripción**:
- Implementa todos los casos requeridos correctamente
- Maneja todos los casos edge (límites, valores especiales)
- Los tests pasan al 100% (visibles + ocultos)
- La lógica es clara y completa

**Indicadores**:
- ✅ Todos los tests pasan
- ✅ Implementa casos edge (0, máximo, negativos, etc.)
- ✅ Lógica correcta y completa

---

### Bueno (7.0-8.9) - 32 puntos
**Descripción**:
- Implementa la mayoría de casos correctamente
- Puede faltar el manejo de algunos casos edge
- Al menos 80% de tests pasan
- Lógica mayormente correcta con fallas menores

**Indicadores**:
- ✅ 80-99% de tests pasan
- ⚠️ Falta manejo de 1-2 casos edge
- ✅ Lógica principal correcta

---

### Regular (5.0-6.9) - 24 puntos
**Descripción**:
- Implementa casos básicos correctamente
- Falla en casos intermedios o edge cases
- 50-79% de tests pasan
- Lógica incompleta o con errores significativos

**Indicadores**:
- ⚠️ 50-79% de tests pasan
- ❌ No maneja casos edge
- ⚠️ Lógica parcialmente correcta

---

### Insuficiente (0.0-4.9) - 0 puntos
**Descripción**:
- No implementa correctamente o no funciona
- Menos del 50% de tests pasan
- Lógica incorrecta o ausente
- No resuelve el problema planteado

**Indicadores**:
- ❌ <50% de tests pasan
- ❌ Lógica incorrecta
- ❌ No cumple requisitos mínimos

---

## 💎 Rúbrica Estándar: Criterio 2 - Calidad de Código (30%)

### Excelente (9.0-10.0) - 30 puntos
**Descripción**:
- Código limpio, legible y bien estructurado
- Nombres de variables descriptivos
- Indentación y espaciado correctos
- Sin código duplicado
- Comentarios donde son necesarios

**Indicadores**:
- ✅ Nombres descriptivos (ej: `validar_nota` vs `v`)
- ✅ Indentación correcta
- ✅ Código DRY (Don't Repeat Yourself)
- ✅ Estructura clara (función principal, helpers si necesario)

---

### Bueno (7.0-8.9) - 24 puntos
**Descripción**:
- Código mayormente legible
- Algunos nombres podrían ser más descriptivos
- Indentación mayormente correcta
- Poca duplicación de código
- Estructura aceptable

**Indicadores**:
- ✅ Mayoría de nombres son claros
- ⚠️ Indentación con 1-2 inconsistencias
- ✅ Poca o ninguna duplicación

---

### Regular (5.0-6.9) - 18 puntos
**Descripción**:
- Código difícil de leer en algunas partes
- Nombres de variables poco descriptivos
- Problemas de indentación
- Código duplicado o mal estructurado
- Falta de claridad

**Indicadores**:
- ⚠️ Nombres poco claros (ej: `x`, `a`, `temp`)
- ⚠️ Indentación inconsistente
- ❌ Código duplicado

---

### Insuficiente (0.0-4.9) - 0 puntos
**Descripción**:
- Código ilegible o muy mal estructurado
- Nombres crípticos o sin sentido
- Sin indentación o caótica
- Mucho código duplicado
- Imposible de mantener

**Indicadores**:
- ❌ Nombres sin sentido
- ❌ Sin indentación
- ❌ Muy difícil de leer

---

## 🛡️ Rúbrica Estándar: Criterio 3 - Robustez (30%)

### Excelente (9.0-10.0) - 30 puntos
**Descripción**:
- Maneja todos los errores posibles
- Valida entradas correctamente
- No crashea ante inputs inesperados
- Retorna valores/errores apropiados
- Maneja casos límite perfectamente

**Indicadores**:
- ✅ Validación de tipos de datos
- ✅ Validación de rangos (0-100, etc.)
- ✅ Manejo de casos límite (None, '', 0, etc.)
- ✅ No genera excepciones inesperadas

---

### Bueno (7.0-8.9) - 24 puntos
**Descripción**:
- Maneja la mayoría de errores
- Validaciones básicas presentes
- Puede fallar ante algunos inputs edge
- Generalmente no crashea
- Maneja casos comunes bien

**Indicadores**:
- ✅ Validaciones básicas
- ⚠️ Falta validación de 1-2 casos edge
- ✅ No crashea en casos comunes

---

### Regular (5.0-6.9) - 18 puntos
**Descripción**:
- Poca o nula validación de entradas
- Puede crashear ante inputs inesperados
- No maneja casos edge
- Asume que los datos son siempre válidos
- Frágil ante errores

**Indicadores**:
- ⚠️ Validación mínima o ausente
- ❌ Crashea con inputs inesperados
- ❌ No maneja None, '', etc.

---

### Insuficiente (0.0-4.9) - 0 puntos
**Descripción**:
- Sin validación alguna
- Crashea frecuentemente
- No maneja ningún error
- Código muy frágil
- Inutilizable en producción

**Indicadores**:
- ❌ Sin validación
- ❌ Crashea constantemente
- ❌ Código extremadamente frágil

---

## 📊 Ejemplo Completo: Ejercicio "Validar Nota"

### Consigna
Crea una función `validar_nota(nota)` que:
- Reciba una nota numérica
- Retorne `True` si está entre 0 y 100 (inclusive)
- Retorne `False` si está fuera de ese rango
- Maneje casos edge correctamente

### Pistas Graduadas

**Pista 1 (5 puntos)**: Piensa en los límites del rango válido. ¿Cuál es el mínimo y el máximo?

**Pista 2 (10 puntos)**: Necesitas usar una estructura condicional (if-elif-else) para verificar si la nota está dentro del rango 0-100.

**Pista 3 (15 puntos)**: Usa el operador `or` para detectar si la nota está fuera de los límites: `if nota < 0 or nota > 100:`

**Pista 4 (20 puntos)**:
```python
def validar_nota(nota):
    if nota < 0 or nota > 100:
        return False
    return True
```

### Evaluación con Rúbrica

**Código del Estudiante A** (usa pista 1):
```python
def validar_nota(nota):
    if nota >= 0 and nota <= 100:
        return True
    else:
        return False
```

**Evaluación**:
- **Funcionalidad**: Excelente (40/40) - Todos los tests pasan
- **Calidad**: Bueno (24/30) - Podría simplificar el else
- **Robustez**: Excelente (30/30) - Maneja todos los casos
- **Subtotal Rúbrica**: 94/100
- **Penalización**: 5 puntos (usó 1 pista)
- **Nota Final**: 89/100 ✅

---

**Código del Estudiante B** (usa 3 pistas):
```python
def validar_nota(n):
    if n < 0 or n > 100:
        return False
    return True
```

**Evaluación**:
- **Funcionalidad**: Excelente (40/40) - Todos los tests pasan
- **Calidad**: Regular (18/30) - Nombre de variable poco descriptivo (`n`)
- **Robustez**: Excelente (30/30) - Maneja todos los casos
- **Subtotal Rúbrica**: 88/100
- **Penalización**: 30 puntos (usó 3 pistas: 5+10+15)
- **Nota Final**: 58/100 ⚠️

---

**Código del Estudiante C** (sin pistas):
```python
def validar_nota(nota):
    return 0 <= nota <= 100
```

**Evaluación**:
- **Funcionalidad**: Excelente (40/40) - Todos los tests pasan
- **Calidad**: Excelente (30/30) - Pythonic, conciso, claro
- **Robustez**: Excelente (30/30) - Maneja todos los casos
- **Subtotal Rúbrica**: 100/100
- **Penalización**: 0 puntos (no usó pistas)
- **Nota Final**: 100/100 🌟

---

## 🔧 Formato JSON para Seed

```json
{
  "exercise_id": "U1-VAL-01",
  "max_score": 100,
  "rubric_criteria": [
    {
      "criterion_name": "Funcionalidad",
      "description": "Evaluación de si el código resuelve el problema correctamente",
      "weight": 0.4,
      "order": 1,
      "levels": [
        {
          "level_name": "Excelente",
          "description": "Implementa todos los casos requeridos correctamente, maneja todos los casos edge, 100% de tests pasan",
          "min_score": 9.0,
          "max_score": 10.0,
          "points": 40
        },
        {
          "level_name": "Bueno",
          "description": "Implementa la mayoría de casos correctamente, puede faltar algunos casos edge, 80-99% de tests pasan",
          "min_score": 7.0,
          "max_score": 8.9,
          "points": 32
        },
        {
          "level_name": "Regular",
          "description": "Implementa casos básicos, falla en casos intermedios, 50-79% de tests pasan",
          "min_score": 5.0,
          "max_score": 6.9,
          "points": 24
        },
        {
          "level_name": "Insuficiente",
          "description": "No funciona correctamente, menos del 50% de tests pasan, lógica incorrecta",
          "min_score": 0.0,
          "max_score": 4.9,
          "points": 0
        }
      ]
    },
    {
      "criterion_name": "Calidad de código",
      "description": "Evaluación de legibilidad, estructura y buenas prácticas",
      "weight": 0.3,
      "order": 2,
      "levels": [
        {
          "level_name": "Excelente",
          "description": "Código limpio, legible, bien estructurado, nombres descriptivos, sin duplicación",
          "min_score": 9.0,
          "max_score": 10.0,
          "points": 30
        },
        {
          "level_name": "Bueno",
          "description": "Código mayormente legible, estructura aceptable, pocos problemas de estilo",
          "min_score": 7.0,
          "max_score": 8.9,
          "points": 24
        },
        {
          "level_name": "Regular",
          "description": "Código difícil de leer, nombres poco descriptivos, código duplicado",
          "min_score": 5.0,
          "max_score": 6.9,
          "points": 18
        },
        {
          "level_name": "Insuficiente",
          "description": "Código ilegible, muy mal estructurado, imposible de mantener",
          "min_score": 0.0,
          "max_score": 4.9,
          "points": 0
        }
      ]
    },
    {
      "criterion_name": "Robustez",
      "description": "Evaluación de manejo de errores y casos edge",
      "weight": 0.3,
      "order": 3,
      "levels": [
        {
          "level_name": "Excelente",
          "description": "Maneja todos los errores, valida entradas, no crashea, maneja casos límite perfectamente",
          "min_score": 9.0,
          "max_score": 10.0,
          "points": 30
        },
        {
          "level_name": "Bueno",
          "description": "Maneja la mayoría de errores, validaciones básicas, puede fallar en algunos casos edge",
          "min_score": 7.0,
          "max_score": 8.9,
          "points": 24
        },
        {
          "level_name": "Regular",
          "description": "Poca validación, crashea con inputs inesperados, no maneja casos edge",
          "min_score": 5.0,
          "max_score": 6.9,
          "points": 18
        },
        {
          "level_name": "Insuficiente",
          "description": "Sin validación, crashea frecuentemente, código muy frágil",
          "min_score": 0.0,
          "max_score": 4.9,
          "points": 0
        }
      ]
    }
  ]
}
```

---

## 🎓 Uso en el Sistema

### Para Docentes
1. **Crear ejercicio**: Se asigna automáticamente la rúbrica estándar
2. **Personalizar rúbrica** (opcional): Modificar criterios o niveles específicos del ejercicio
3. **Ver rúbrica**: Al publicar ejercicio, estudiantes ven criterios y niveles

### Para Estudiantes
1. **Ver rúbrica**: Antes de resolver, conocen los criterios de evaluación
2. **Solicitar pistas**: Sistema advierte penalización antes de revelar
3. **Enviar código**: IA evalúa contra la rúbrica
4. **Ver feedback**: Reciben evaluación detallada por criterio + nota final

### Para el Sistema de IA
1. **Cargar rúbrica**: Al evaluar, obtiene criterios y niveles del ejercicio
2. **Analizar código**: Determina nivel alcanzado en cada criterio
3. **Calcular score**: Aplica pesos + penalizaciones
4. **Generar feedback**: Explica por qué obtuvo cada nivel

---

## 📝 Próximos Pasos

1. ✅ **FASE 1.5 completada**: Modelos ORM, schemas, migración
2. ⬜ **FASE 3**: Seed database con rúbricas estándar
3. ⬜ **FASE 4**: API endpoints para CRUD de rúbricas
4. ⬜ **Integración con E-IA-Proc**: Evaluador usa rúbricas
5. ⬜ **Frontend**: Mostrar rúbrica antes de resolver ejercicio

---

**Última actualización**: 2025-12-24
**Estado**: Rúbricas estándar definidas, listas para seed
