# Usuarios de Prueba y Roles

## Roles del Sistema

El sistema define 3 roles principales (almacenados como JSON array en `UserDB.roles`):

| Rol | Descripción |
|-----|-------------|
| `student` | Estudiante - acceso a sesiones de aprendizaje, simuladores, trazas propias |
| `instructor` | Instructor/Docente - acceso al dashboard, herramientas de docente, evaluaciones |
| `admin` | Administrador - acceso completo, configuración LLM, exportación de datos |

---

## Usuarios UAT (User Acceptance Testing)

Definidos en `uat/setup/create-test-users.py`:

### Estudiantes (5)

| ID | Email | Password | Perfil | Descripción |
|----|-------|----------|--------|-------------|
| E01 | estudiante1@uat.ai-native.edu | `UAT2025_E01!` | AVANZADO | Experiencia previa en programación |
| E02 | estudiante2@uat.ai-native.edu | `UAT2025_E02!` | INTERMEDIO | Confiado pero con lagunas conceptuales |
| E03 | estudiante3@uat.ai-native.edu | `UAT2025_E03!` | INTERMEDIO | Disciplinado y organizado |
| E04 | estudiante4@uat.ai-native.edu | `UAT2025_E04!` | INICIAL | Dificultades, frustración frecuente |
| E05 | estudiante5@uat.ai-native.edu | `UAT2025_E05!` | INTERMEDIO | Curioso y proactivo |

### Instructor (1)

| ID | Email | Password | Rol |
|----|-------|----------|-----|
| INST01 | instructor@uat.ai-native.edu | `UAT2025_INST!` | INSTRUCTOR |

---

## Crear los usuarios

```bash
# Ejecutar script de creación
cd uat/setup
python create-test-users.py

# Dry-run (ver sin crear)
python create-test-users.py --dry-run

# Con URL de base de datos específica
python create-test-users.py --database-url "postgresql://user:pass@localhost/db"
```

---

## Estructura del Modelo UserDB

```python
class UserDB(Base, BaseModel):
    email = Column(String(255), unique=True)      # Login email
    username = Column(String(100), unique=True)   # Username
    hashed_password = Column(String(255))         # Bcrypt hash
    full_name = Column(String(255))               # Nombre completo
    student_id = Column(String(100))              # ID estudiante (opcional)
    roles = Column(JSON, default=list)            # ["student", "instructor", "admin"]
    is_active = Column(Boolean, default=True)     # Cuenta activa
    is_verified = Column(Boolean, default=False)  # Email verificado
    last_login = Column(DateTime)                 # Último acceso
    login_count = Column(Integer, default=0)      # Contador de logins
```

---

## Notas de Seguridad

1. Estas son contraseñas temporales para UAT solamente
2. Los usuarios DEBEN cambiar contraseñas en el primer login
3. Las contraseñas expiran después de 30 días
4. Todas las sesiones serán registradas para análisis UAT