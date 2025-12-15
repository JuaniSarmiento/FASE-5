# 🔧 Fix de Validación Backend - Error 422

## Problema Identificado

Al ejecutar los tests, se recibió un **error 422 (Unprocessable Entity)** al crear sesiones:

```json
{
  "error": "Request failed with status code 422"
}
```

## Root Cause

**Mismatch entre valores del frontend y enums del backend:**

### Backend Enums (Valores Esperados)

1. **`AgentMode`** (para campo `mode` en sesiones):
   ```python
   class AgentMode(str, Enum):
       TUTOR = "TUTOR"           # ✅ Mayúsculas
       EVALUATOR = "EVALUATOR"   # ✅ Mayúsculas
       SIMULATOR = "SIMULATOR"   # ✅ Mayúsculas
       RISK_ANALYST = "RISK_ANALYST"
       GOVERNANCE = "GOVERNANCE"
   ```

2. **`SimulatorType`** (para campo `simulator_type`):
   ```python
   class SimulatorType(str, Enum):
       PRODUCT_OWNER = "product_owner"          # ✅ Lowercase con underscore
       SCRUM_MASTER = "scrum_master"            # ✅ Lowercase con underscore
       TECH_INTERVIEWER = "tech_interviewer"    # ✅ Lowercase con underscore
       INCIDENT_RESPONDER = "incident_responder"
       CLIENT = "client"
       DEVSECOPS = "devsecops"
   ```

### Valores Incorrectos del Frontend

❌ **TestPage.tsx**: Enviaba `mode: 'guided'` → Debería ser `'TUTOR'`  
❌ **TestPage.tsx**: Enviaba `mode: 'autonomous'` → Debería ser `'SIMULATOR'`  
❌ **SimulatorsPage.tsx**: Usaba IDs como `'PRODUCT_OWNER'` (mayúsculas) → Debería ser `'product_owner'`  
❌ **TestPage.tsx**: Usaba IDs como `'S-IA-PO'` → Debería ser `'product_owner'`

---

## Solución Implementada

### 1. **TestPage.tsx** - Correcciones Principales

#### a) Función de Mapeo de Simuladores
```typescript
// Nueva función para mapear IDs de frontend a backend
const mapSimulatorId = (frontendId: string): string => {
  const mapping: Record<string, string> = {
    'S-IA-PO': 'product_owner',
    'S-IA-SM': 'scrum_master',
    'S-IA-TE': 'tech_interviewer',
    'S-IA-IR': 'incident_responder',
    'S-IA-CX': 'client',
    'S-IA-DSO': 'devsecops'
  };
  return mapping[frontendId] || frontendId;
};
```

#### b) Creación de Sesión Principal
```typescript
// ANTES (INCORRECTO)
const sessionResponse = await apiClient.createSession({
  student_id: 'test-student-001',
  activity_id: 'test-activity-001',
  mode: 'guided'  // ❌ Valor inválido
});

// DESPUÉS (CORREGIDO)
const sessionResponse = await apiClient.createSession({
  student_id: 'test-student-001',
  activity_id: 'test-activity-001',
  mode: 'TUTOR'  // ✅ Enum válido
});
```

#### c) Tests de Simuladores
```typescript
// ANTES (INCORRECTO)
const poResponse = await apiClient.interactWithSimulator({
  session_id: sessionId,
  simulator_type: 'S-IA-PO',  // ❌ ID del frontend
  prompt: 'Necesito ayuda...',
  context: {}
});

// DESPUÉS (CORREGIDO)
const poResponse = await apiClient.interactWithSimulator({
  session_id: sessionId,
  simulator_type: 'product_owner',  // ✅ Enum del backend
  prompt: 'Necesito ayuda...',
  context: {}
});
```

#### d) Test Individual de Simuladores
```typescript
// ANTES (INCORRECTO)
const sessionResponse = await apiClient.createSession({
  student_id: 'test-student-sim',
  activity_id: 'test-simulator',
  mode: 'autonomous'  // ❌ Valor inválido
});

// DESPUÉS (CORREGIDO)
const sessionResponse = await apiClient.createSession({
  student_id: 'test-student-sim',
  activity_id: 'test-simulator',
  mode: 'SIMULATOR',  // ✅ Enum válido
  simulator_type: simulatorType  // ✅ Incluir simulator_type
});

// Usar función de mapeo para convertir IDs
const backendSimulatorType = mapSimulatorId(simulatorType);
const response = await apiClient.interactWithSimulator({
  session_id: sessionId,
  simulator_type: backendSimulatorType,  // ✅ Valor mapeado
  prompt: `Hola, soy un estudiante...`,
  context: {}
});
```

---

### 2. **SimulatorsPage.tsx** - Correcciones

#### a) IDs de Simuladores
```typescript
// ANTES (INCORRECTO)
const simulators = [
  { id: 'PRODUCT_OWNER', name: 'Product Owner', ... },  // ❌ Mayúsculas
  { id: 'SCRUM_MASTER', name: 'Scrum Master', ... },
  ...
];

// DESPUÉS (CORREGIDO)
const simulators = [
  { id: 'product_owner', name: 'Product Owner', ... },  // ✅ Backend enum
  { id: 'scrum_master', name: 'Scrum Master', ... },
  { id: 'tech_interviewer', name: 'Tech Interviewer', ... },
  { id: 'incident_responder', name: 'Incident Responder', ... },
  { id: 'client', name: 'Cliente', ... },
  { id: 'devsecops', name: 'DevSecOps', ... },
];
```

#### b) Creación de Sesión de Simulador
```typescript
// ANTES (INCORRECTO)
const response = await apiClient.createSession({
  student_id: 'student_001',
  activity_id: 'simulator_' + sim.id.toLowerCase(),  // Conversión innecesaria
  mode: 'SIMULATOR',
  simulator_type: sim.id.toLowerCase()  // Conversión innecesaria
});

// DESPUÉS (CORREGIDO)
const response = await apiClient.createSession({
  student_id: 'student_001',
  activity_id: 'simulator_' + sim.id,  // ✅ Ya está en lowercase
  mode: 'SIMULATOR',  // ✅ Correcto
  simulator_type: sim.id  // ✅ Ya está en formato correcto
});
```

---

## Validación del Backend

### Schema de SessionCreate
```python
class SessionCreate(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=255)
    activity_id: str = Field(..., min_length=1, max_length=255)
    mode: SessionMode = Field(...)  # Debe ser: TUTOR, EVALUATOR, SIMULATOR
    simulator_type: Optional[str] = Field(None, max_length=50)
    
    @model_validator(mode='after')
    def validate_simulator_type_required(self):
        # Si mode=SIMULATOR, simulator_type es REQUERIDO
        if self.mode == SessionMode.SIMULATOR:
            if not self.simulator_type:
                raise ValueError("simulator_type is required when mode=SIMULATOR")
```

### Reglas de Validación
1. **`mode`**: OBLIGATORIO - Debe ser uno de: `TUTOR`, `EVALUATOR`, `SIMULATOR`, `RISK_ANALYST`, `GOVERNANCE`
2. **`simulator_type`**: OPCIONAL - Pero REQUERIDO cuando `mode=SIMULATOR`
3. **`simulator_type` valores**: Debe ser uno de: `product_owner`, `scrum_master`, `tech_interviewer`, `incident_responder`, `client`, `devsecops`

---

## Archivos Modificados

| Archivo | Líneas | Cambios |
|---------|--------|---------|
| `frontEnd/src/pages/TestPage.tsx` | 7-20 | ✅ Agregada función `mapSimulatorId` |
| `frontEnd/src/pages/TestPage.tsx` | 28 | ✅ Cambió `mode: 'guided'` → `mode: 'TUTOR'` |
| `frontEnd/src/pages/TestPage.tsx` | 39 | ✅ Cambió `'S-IA-PO'` → `'product_owner'` |
| `frontEnd/src/pages/TestPage.tsx` | 48 | ✅ Cambió `'S-IA-SM'` → `'scrum_master'` |
| `frontEnd/src/pages/TestPage.tsx` | 110-116 | ✅ Corregido test individual con `mode: 'SIMULATOR'` y `simulator_type` |
| `frontEnd/src/pages/TestPage.tsx` | 120 | ✅ Usa `mapSimulatorId()` para convertir IDs |
| `frontEnd/src/pages/SimulatorsPage.tsx` | 4-10 | ✅ IDs cambiados a lowercase con underscore |
| `frontEnd/src/pages/SimulatorsPage.tsx` | 25-26 | ✅ Removido `.toLowerCase()` innecesario |

---

## Testing

### Valores Correctos para Testing

#### Crear Sesión de Tutor
```typescript
await apiClient.createSession({
  student_id: 'test-student',
  activity_id: 'test-activity',
  mode: 'TUTOR'  // ✅ Sin simulator_type
});
```

#### Crear Sesión de Simulador
```typescript
await apiClient.createSession({
  student_id: 'test-student',
  activity_id: 'test-activity',
  mode: 'SIMULATOR',  // ✅ Mode correcto
  simulator_type: 'product_owner'  // ✅ Requerido con mode=SIMULATOR
});
```

#### Interactuar con Simulador
```typescript
await apiClient.interactWithSimulator({
  session_id: 'session-uuid',
  simulator_type: 'scrum_master',  // ✅ Lowercase con underscore
  prompt: 'Mi pregunta...',
  context: {}
});
```

---

## Estado Actual

✅ **CORREGIDO** - Todos los valores ahora coinciden con los enums del backend  
✅ **VALIDADO** - SessionsPage ya usaba valores correctos  
✅ **MEJORADO** - TestPage con función de mapeo para mejor mantenibilidad  
✅ **SIMPLIFICADO** - SimulatorsPage usa IDs directos sin conversión

---

## Lecciones Aprendidas

### Best Practices
1. **Siempre verificar schemas del backend** antes de implementar frontend
2. **Usar TypeScript enums** que coincidan con backend enums
3. **Centralizar mapeos** en funciones reutilizables
4. **Documentar valores válidos** en comentarios del código
5. **Validar con backend API docs** (Swagger/OpenAPI)

### Checklist para Nuevos Endpoints
- [ ] Leer schema de request en backend
- [ ] Verificar enums y valores válidos
- [ ] Revisar validadores (`@model_validator`)
- [ ] Crear tipos TypeScript que coincidan
- [ ] Testear con valores edge-case
- [ ] Documentar valores válidos en código

---

## Próximos Tests

Ahora que los valores están corregidos, deberías poder:

1. ✅ Ejecutar "▶️ Ejecutar Todas las Pruebas" sin errores 422
2. ✅ Testear cada simulador individualmente
3. ✅ Crear sesiones en SessionsPage sin problemas
4. ✅ Usar simuladores en SimulatorsPage correctamente

**¡Prueba nuevamente desde http://localhost:3000/test!**

