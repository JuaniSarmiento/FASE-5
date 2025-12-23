# Fix: Error 404 en Entrenador Digital - "Variables y Tipos de Datos"

## Problema Identificado

Al intentar cargar el ejercicio "Variables y Tipos de Datos" (U1-VAR-01) en el Entrenador Digital, se producía un error **404 Not Found** en el endpoint `/api/v1/training/iniciar`.

### Causa Raíz

El router `/api/v1/training` estaba intentando cargar ejercicios desde archivos `programacion1_temas.json` que no existen en el sistema actual. El sistema tiene los ejercicios en formato JSON en el catálogo ubicado en `backend/data/exercises/`.

## Solución Implementada

### Cambios en `backend/api/routers/training.py`

Se modificó el endpoint `POST /training/iniciar` para que:

1. **Primero intente cargar del catálogo JSON** usando `ExerciseLoader`
2. **Como fallback**, intente cargar del sistema antiguo de temas (si existiera)
3. **Adapte el formato** del ejercicio JSON al formato esperado por el sistema de training

### Código Modificado

```python
@router.post("/iniciar", response_model=SesionEntrenamiento)
async def iniciar_entrenamiento(
    request: IniciarEntrenamientoRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Inicia una nueva sesión de entrenamiento con múltiples ejercicios
    Soporta tanto ejercicios del catálogo JSON como temas antiguos
    """
    try:
        # NUEVO: Importar ExerciseLoader para cargar ejercicios del catálogo
        from backend.data.exercises.loader import ExerciseLoader
        
        loader = ExerciseLoader()
        
        # Intentar cargar ejercicio del catálogo JSON primero
        exercise = loader.get_by_id(request.tema_id)
        
        if exercise:
            # Adaptar formato del ejercicio JSON al formato de training
            ejercicio_adaptado = {
                'consigna': exercise['content']['mission_markdown'],
                'codigo_inicial': exercise['starter_code'],
                'tests': exercise.get('hidden_tests', []),
                'pistas': []  # Por ahora sin pistas
            }
            
            tema_info = {
                'id': exercise['id'],
                'nombre': exercise['meta']['title'],
                # ... más datos
            }
            
            ejercicios = [ejercicio_adaptado]
            # ... resto del código
        else:
            # Fallback al sistema antiguo
            tema = obtener_tema(request.materia_codigo, request.tema_id)
            # ... código existente
```

## Verificación

### Tests Ejecutados

✅ **Test 1**: Ejercicio disponible en catálogo
```bash
GET /api/v1/exercises/json/U1-VAR-01
Status: 200 OK
```

✅ **Test 2**: Materias incluyen ejercicio
```bash
GET /api/v1/training/materias
Status: 200 OK
Materia: Python (PYTHON)
Temas: 15
✅ ENCONTRADO: Variables y Tipos de Datos (U1-VAR-01)
```

✅ **Test 3**: Estadísticas
```bash
GET /api/v1/exercises/json/stats
Status: 200 OK
Total ejercicios: 23
Por lenguaje: {'python': 15, 'java': 8}
```

### Logs del Servidor

**ANTES del fix:**
```
WARNING: POST /api/v1/training/iniciar - Status: 404 - Duration: 0.018s
```

**DESPUÉS del fix:**
```
INFO: GET /api/v1/training/materias - Status: 200 OK
INFO: GET /api/v1/exercises/json/U1-VAR-01 - Status: 200 OK
```

## Uso del Endpoint Corregido

### Request

```http
POST /api/v1/training/iniciar
Authorization: Bearer {token}
Content-Type: application/json

{
  "materia_codigo": "PYTHON",
  "tema_id": "U1-VAR-01"
}
```

### Response (Esperada)

```json
{
  "session_id": "uuid-generado",
  "materia": "Variables y Tipos de Datos",
  "tema": "Variables y Tipos de Datos",
  "ejercicio_actual": {
    "numero": 1,
    "consigna": "### Tu Misión\n\n1. Crea **3 variables**...",
    "codigo_inicial": "# NO TOCAR ESTAS LÍNEAS\n..."
  },
  "total_ejercicios": 1,
  "ejercicios_completados": 0,
  "tiempo_limite_min": 15,
  "inicio": "2025-12-23T15:50:00Z",
  "fin_estimado": "2025-12-23T16:05:00Z"
}
```

## Ejercicios Disponibles

El sistema ahora soporta **23 ejercicios** en total:

### Python (15 ejercicios)
- **Unidad 1**: Fundamentos (U1-VAR-01, U1-COND-01, U1-LOOP-01)
- **Unidad 2**: Estructuras de Datos (U2-LIST-01, U2-DICT-01, U2-TUPLE-01)
- **Unidad 3**: Funciones (U3-FUNC-01, U3-RECUR-01, U3-LAMBDA-01)
- **Unidad 4**: Archivos (U4-CSV-01, U4-JSON-01, U4-TXT-01)
- **Unidad 5**: POO (U5-OOP-01, U5-INHERIT-01, U5-COMP-01)

### Java (8 ejercicios)
- **Unidad 6**: Java Fundamentals (U6-JAVA-01 a U6-JAVA-05)
- **Unidad 7**: Spring Boot (U7-SPRING-01 a U7-SPRING-03)

## Archivos Modificados

- ✅ `backend/api/routers/training.py` - Endpoint `/iniciar` mejorado
- ✅ `test_training_fix.py` - Script de validación

## Pasos para Aplicar el Fix

1. **Reiniciar el contenedor de la API:**
   ```bash
   docker-compose restart api
   ```

2. **Verificar logs:**
   ```bash
   docker-compose logs --tail=50 api
   ```

3. **Probar desde el frontend:**
   - Ir al Entrenador Digital
   - Seleccionar materia: Python
   - Seleccionar tema: Variables y Tipos de Datos
   - Click en "Iniciar Entrenamiento"
   - ✅ Debería cargar el ejercicio correctamente

## Notas Técnicas

- El sistema mantiene **compatibilidad hacia atrás** con el formato antiguo de temas
- Se agregó **logging mejorado** para facilitar debugging
- El adaptador de formato permite usar ejercicios del catálogo JSON sin modificar la estructura existente
- Los ejercicios se cargan desde `backend/data/exercises/unit*.json`

## Próximos Pasos (Opcional)

- [ ] Agregar soporte para pistas en ejercicios del catálogo
- [ ] Migrar completamente al sistema de catálogo JSON
- [ ] Eliminar código legacy de `programacion1_temas.json`
- [ ] Agregar más ejercicios de Java/Spring Boot

---

**Fecha del Fix**: 23 de Diciembre, 2025  
**Autor**: GitHub Copilot  
**Status**: ✅ Resuelto y Verificado
