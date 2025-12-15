# 🎓 Sistema de Autenticación + Ejercicios de Código con IA

Sistema completo de autenticación con roles y módulo de ejercicios de código Python evaluados por IA (Ollama).

## 🚀 Características Implementadas

### ✅ Sistema de Autenticación
- **Registro de usuarios** con roles: Estudiante, Tutor, Administrador
- **Login/Logout** con JWT tokens (duración: 7 días)
- **Protección de rutas** - requiere autenticación
- **Perfil de usuario** visible en el header
- **Gestión de sesión** persistente en localStorage

### ✅ Módulo de Ejercicios de Código
- **10 ejercicios progresivos** de Python (niveles 1-10)
- **Editor de código** integrado (Monaco Editor - mismo que VS Code)
- **Ejecución automática** de tests unitarios
- **Evaluación con IA** usando Ollama (llama3.2:3b)
- **Métricas de calidad**: Calidad, Legibilidad, Eficiencia, Buenas Prácticas
- **Retroalimentación** personalizada de la IA
- **Estadísticas de progreso** por usuario
- **Sistema de pistas** para ayudar al estudiante

## 📦 Estructura de Base de Datos

### Tabla: `users`
```sql
- id (String, PK)
- email (String, UNIQUE)
- username (String, UNIQUE)
- hashed_password (String)
- full_name (String, nullable)
- role (Enum: student, tutor, admin)
- is_active (String: "true"/"false")
- created_at (DateTime)
- updated_at (DateTime)
```

### Tabla: `exercises`
```sql
- id (String, PK)
- title (String)
- description (Text)
- difficulty_level (Integer 1-10)
- starter_code (Text)
- test_cases (JSON)
- hints (JSON)
- max_score (Float)
- time_limit_seconds (Integer)
- created_at (DateTime)
```

### Tabla: `user_exercise_submissions`
```sql
- id (String, PK)
- user_id (String, FK)
- exercise_id (String, FK)
- submitted_code (Text)
- passed_tests (Integer)
- total_tests (Integer)
- ai_score (Float)
- ai_feedback (Text)
- code_quality_score (Float)
- readability_score (Float)
- efficiency_score (Float)
- best_practices_score (Float)
- is_correct (String)
- submitted_at (DateTime)
```

## 🎯 Uso del Sistema

### Inicialización (Primera vez)

```powershell
# Opción 1: Con Docker (RECOMENDADO)
docker compose up --build

# Opción 2: Manual
# Terminal 1 - Backend
python -m backend.scripts.init_db         # Crear tablas
python -m backend.scripts.init_exercises  # Poblar ejercicios
cd backend
python -m uvicorn api.main:app --reload

# Terminal 2 - Frontend
cd frontEnd
npm install
npm run dev
```

### Flujo de Usuario

#### 1. **Registro**
- Ir a http://localhost:5173/register
- Ingresar: username, email, password, nombre completo (opcional)
- Seleccionar rol: Estudiante / Tutor / Administrador
- El sistema crea el usuario y genera un token JWT

#### 2. **Login**
- Ir a http://localhost:5173/login
- Ingresar email y password
- Redirige automáticamente al dashboard

#### 3. **Ver Ejercicios**
- Clic en "💻 Ejercicios de Código" en el menú lateral
- Ver estadísticas: Total, Completados, Envíos, Puntuación Promedio
- Filtrar por dificultad: Fácil (1-3), Medio (4-6), Difícil (7-10)

#### 4. **Resolver Ejercicio**
- Clic en cualquier ejercicio
- Leer descripción y requisitos
- (Opcional) Ver pistas con el botón "💡 Ver Pistas"
- Escribir código en el editor Monaco
- Clic en "▶️ Ejecutar y Evaluar"

#### 5. **Ver Resultados**
- **Tests**: Muestra cuántos tests pasaron (ej: 3/3)
- **Evaluación de IA**: Puntuación general + desglose
  - Calidad del código (0-10)
  - Legibilidad (0-10)
  - Eficiencia (0-10)
  - Buenas prácticas (0-10)
- **Retroalimentación**: Comentarios de la IA sobre el código

## 📝 Ejercicios Disponibles

| Nivel | Título | Descripción | Conceptos |
|-------|--------|-------------|-----------|
| 1 | Suma de Dos Números | Función básica de suma | Variables, funciones |
| 2 | Par o Impar | Verificar paridad | Condicionales, módulo |
| 3 | Factorial | Calcular factorial | Recursión/iteración |
| 4 | Invertir Cadena | Revertir string | Slicing, strings |
| 5 | Fibonacci | Serie de Fibonacci | Listas, bucles |
| 6 | Palíndromo | Verificar palíndromo | Strings, comparación |
| 7 | Ordenamiento Burbuja | Implementar bubble sort | Algoritmos, sorting |
| 8 | Búsqueda Binaria | Búsqueda en array ordenado | Algoritmos, búsqueda |
| 9 | Números Primos | Encontrar primos en rango | Optimización, matemáticas |
| 10 | Dijkstra Simplificado | Camino más corto en grafo | Grafos, algoritmos avanzados |

## 🔧 API Endpoints

### Autenticación
```
POST   /api/v1/auth/register       # Registrar usuario
POST   /api/v1/auth/token          # Login (OAuth2)
GET    /api/v1/auth/me             # Obtener usuario actual
```

### Ejercicios
```
GET    /api/v1/exercises           # Listar ejercicios (?difficulty=N)
GET    /api/v1/exercises/{id}      # Obtener ejercicio específico
POST   /api/v1/exercises/submit    # Enviar código para evaluación
GET    /api/v1/exercises/user/submissions  # Historial de envíos
GET    /api/v1/exercises/stats     # Estadísticas del usuario
```

## 🤖 Evaluación con IA

El sistema usa **Ollama** con el modelo **llama3.2:3b** para evaluar el código:

### Prompt de Evaluación
```
Eres un profesor de programación. Evalúa el siguiente código Python:

EJERCICIO:
{exercise_description}

CÓDIGO DEL ESTUDIANTE:
{submitted_code}

RESULTADOS DE TESTS: {passed_tests}/{total_tests} pasaron

Proporciona una evaluación en JSON:
{
  "overall_score": 0-10,
  "code_quality": 0-10,
  "readability": 0-10,
  "efficiency": 0-10,
  "best_practices": 0-10,
  "feedback": "Retroalimentación constructiva..."
}
```

### Proceso de Evaluación
1. **Ejecución de Tests**: Corre el código contra test cases predefinidos
2. **Medición de Performance**: Tiempo de ejecución en ms
3. **Evaluación de IA**: Análisis cualitativo del código
4. **Cálculo de Puntaje**: Combina resultados de tests + evaluación IA
5. **Guardado**: Almacena submission con todos los datos

## 🎨 Frontend - Componentes Creados

### Páginas
- `LoginPage.tsx` - Formulario de login
- `RegisterPage.tsx` - Formulario de registro
- `ExercisesPage.tsx` - Lista de ejercicios con filtros
- `ExerciseDetailPage.tsx` - Editor de código + resultados

### Contextos
- `AuthContext.tsx` - Gestión de autenticación y usuario actual

### Componentes
- `ProtectedRoute.tsx` - HOC para proteger rutas privadas

### Servicios
- `apiClient.ts` - Actualizado con método `setToken()`

## 🔐 Seguridad

- **Passwords**: Hasheados con bcrypt (passlib)
- **Tokens JWT**: Firmados con SECRET_KEY, expiración 7 días
- **Código Python**: Ejecutado en subprocess aislado con timeout
- **Rate Limiting**: Prevención de abuso en endpoints críticos

## 📊 Métricas de IA

Cada submission es evaluada en 5 dimensiones:

1. **Overall Score (0-10)**: Puntuación general
2. **Code Quality (0-10)**: Estructura, organización
3. **Readability (0-10)**: Nombres claros, comentarios
4. **Efficiency (0-10)**: Complejidad temporal/espacial
5. **Best Practices (0-10)**: Convenciones, idiomaticidad

## 🚨 Troubleshooting

### Error: "Could not validate credentials"
- Verificar que el token JWT no haya expirado
- Hacer logout y login nuevamente

### Error: "Table already exists"
- Los modelos tienen `extend_existing=True`, está OK
- Si persiste: eliminar `ai_native_mvp.db` y reiniciar

### Ollama no responde
- Verificar que Ollama esté corriendo: `ollama list`
- Verificar que llama3.2:3b esté instalado: `ollama pull llama3.2:3b`

### Tests no se ejecutan
- El código Python debe imprimir el resultado esperado
- Verificar formato de output con los test_cases del ejercicio

## 📚 Tecnologías Utilizadas

**Backend:**
- FastAPI
- SQLAlchemy
- PostgreSQL/SQLite
- Ollama (llama3.2:3b)
- PyJWT
- passlib (bcrypt)

**Frontend:**
- React 18
- TypeScript
- Monaco Editor
- Tailwind CSS
- React Router
- Axios

**DevOps:**
- Docker & Docker Compose
- Uvicorn (ASGI server)

---

## 🎉 Sistema Completo

El sistema ahora cuenta con:
- ✅ Autenticación completa con roles
- ✅ 10 ejercicios progresivos de Python
- ✅ Editor de código integrado
- ✅ Evaluación automática con IA
- ✅ Estadísticas y progreso
- ✅ Retroalimentación personalizada
- ✅ Interfaz responsiva y moderna

**¡Listo para usar!** 🚀
