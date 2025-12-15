# Plan de Reorganización del Proyecto Phoenix MVP

## 📊 Estructura Actual (Problemática)

```
Fase2py/
├── src/ai_native_mvp/           # ❌ Doble anidación innecesaria
│   ├── agents/
│   ├── api/
│   ├── core/
│   └── ...
├── 50+ archivos .md en raíz     # ❌ Documentación dispersa
├── tests/                       # ✅ OK
├── scripts/                     # ✅ OK  
├── kubernetes/                  # ✅ OK
├── load-testing/                # ✅ OK
├── security-audit/              # ✅ OK
├── user-acceptance-testing/     # ✅ OK
├── grafana/                     # ✅ OK
├── frontEnd/                    # ✅ OK
└── examples/                    # ✅ OK
```

## ✅ Nueva Estructura (Profesional)

```
phoenix-mvp/
├── backend/                     # 🆕 Backend principal (antes src/ai_native_mvp)
│   ├── agents/                  # Agentes AI
│   ├── api/                     # REST API (FastAPI)
│   ├── core/                    # Lógica de negocio
│   ├── database/                # Modelos y repositorios
│   ├── llm/                     # Proveedores LLM (solo Ollama + Mock)
│   ├── models/                  # Modelos de dominio
│   ├── services/                # Servicios de aplicación
│   ├── export/                  # Exportación de datos
│   ├── __init__.py
│   └── __main__.py
│
├── frontend/                    # 🆕 Frontend (renombrado de frontEnd)
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── docs/                        # 🆕 Toda la documentación consolidada
│   ├── README.md                # Índice principal de docs
│   ├── architecture/            # Docs de arquitectura
│   │   ├── ARQUITECTURA.md
│   │   ├── C4_MODEL.md
│   │   └── IMPLEMENTACIONES_ARQUITECTURALES.md
│   ├── deployment/              # Docs de deployment
│   │   ├── DOCKER.md
│   │   ├── KUBERNETES.md
│   │   ├── STAGING.md
│   │   └── PRODUCTION.md
│   ├── guides/                  # Guías de usuario
│   │   ├── ESTUDIANTE.md
│   │   ├── DOCENTE.md
│   │   ├── ADMINISTRADOR.md
│   │   └── DEVELOPER.md
│   ├── llm/                     # Docs de LLM
│   │   ├── OLLAMA_GUIDE.md
│   │   ├── OLLAMA_QUICKSTART.md
│   │   └── LLM_INTEGRATION.md
│   ├── api/                     # Docs de API
│   │   └── API_REFERENCE.md
│   ├── testing/                 # Docs de testing
│   │   ├── TESTING_GUIDE.md
│   │   ├── UAT.md
│   │   └── LOAD_TESTING.md
│   ├── security/                # Docs de seguridad
│   │   └── SECURITY_AUDIT.md
│   └── project/                 # Docs del proyecto
│       ├── HITOS.md
│       ├── SPRINTS.md
│       ├── CERTIFICACION.md
│       └── USER_STORIES.md
│
├── tests/                       # Tests (sin cambios)
│   ├── test_agents.py
│   ├── test_llm_factory.py
│   ├── test_ollama_provider.py
│   └── ...
│
├── devops/                      # 🆕 Herramientas DevOps consolidadas
│   ├── kubernetes/              # Deployment K8s
│   ├── monitoring/              # Prometheus + Grafana
│   │   ├── grafana/
│   │   ├── prometheus.yml
│   │   └── docker-compose.monitoring.yml
│   ├── load-testing/            # Tests de carga (Locust)
│   ├── security-audit/          # Auditoría de seguridad
│   └── scripts/                 # Scripts de utilidad
│       ├── init_database.py
│       ├── run_api.py
│       └── deploy.sh
│
├── uat/                         # 🆕 User Acceptance Testing (renombrado)
│   ├── scenarios/
│   ├── reports/
│   └── README.md
│
├── examples/                    # Ejemplos de uso (sin cambios)
│   ├── student_example.py
│   └── teacher_example.py
│
├── docker-compose.yml           # Docker Compose principal
├── docker-compose.dev.yml       # 🆕 Overrides para desarrollo
├── Dockerfile                   # Dockerfile del backend
├── .env.example                 # 🆕 Plantilla de variables de entorno
├── .gitignore
├── requirements.txt             # Dependencias Python
├── pytest.ini                   # Config de pytest
├── Makefile                     # Comandos comunes
├── README.md                    # README principal actualizado
└── LICENSE

```

## 🔄 Cambios Principales

### 1. Backend Simplificado
- ❌ Eliminar: `src/ai_native_mvp/`
- ✅ Crear: `backend/` (directamente)
- Mejor visibilidad y menos anidación

### 2. Documentación Organizada
- ❌ 50+ archivos .md en raíz
- ✅ `docs/` con subcarpetas por categoría
- Fácil navegación y mantenimiento

### 3. DevOps Consolidado
- ✅ `devops/` agrupa: kubernetes, scripts, monitoring, testing
- Separación clara entre código y operaciones

### 4. Frontend Renombrado
- ❌ `frontEnd/` (inconsistente)
- ✅ `frontend/` (lowercase, consistente)

### 5. UAT Renombrado
- ❌ `user-acceptance-testing/` (muy largo)
- ✅ `uat/` (conciso y claro)

## 📦 Archivos a Mover

### Docs → docs/
- Todos los .md de raíz excepto README.md y LICENSE

### Monitoring → devops/monitoring/
- grafana/
- prometheus.yml
- docker-compose.monitoring.yml

### Testing → devops/
- load-testing/
- security-audit/

### Scripts → devops/scripts/
- scripts/

### Kubernetes → devops/kubernetes/
- kubernetes/

## ⚙️ Archivos a Actualizar

1. **README.md** - Actualizar paths y estructura
2. **docker-compose.yml** - Actualizar paths de volúmenes
3. **Dockerfile** - Actualizar COPY paths
4. **pytest.ini** - Actualizar testpaths
5. **Makefile** - Actualizar comandos
6. **.gitignore** - Actualizar patterns

## 🎯 Beneficios

1. ✅ **Claridad**: Menos carpetas en raíz (de 15+ a 8)
2. ✅ **Profesionalismo**: Estructura estándar de la industria
3. ✅ **Mantenibilidad**: Docs organizadas por categoría
4. ✅ **Escalabilidad**: Fácil agregar nuevos módulos
5. ✅ **Onboarding**: Nuevos devs encuentran todo rápido
6. ✅ **Visibilidad**: Backend directamente accesible

## 📝 Orden de Ejecución

1. ✅ Eliminar proveedores OpenAI/Gemini
2. 🔄 Crear estructura de carpetas nueva
3. 🔄 Mover archivos a nueva ubicación
4. 🔄 Actualizar imports en código Python
5. 🔄 Actualizar configuraciones (docker, pytest, etc.)
6. 🔄 Actualizar documentación
7. 🔄 Ejecutar tests para validar
8. 🔄 Commit con mensaje descriptivo
