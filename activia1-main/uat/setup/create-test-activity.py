#!/usr/bin/env python3
"""
Create Test Activity for UAT - AI-Native MVP

This script creates the "TP1 - Colas Circulares" activity with pedagogical policies.

Usage:
    python create-test-activity.py [--database-url DATABASE_URL]
"""

import sys
import os
import io
import json
from datetime import datetime
from pathlib import Path

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ai_native_mvp.database import get_db_session
from sqlalchemy import text, create_engine


# ============================================================================
# UAT Test Activity: TP1 - Colas Circulares
# ============================================================================

UAT_ACTIVITY = {
    "activity_id": "uat_tp1_colas_circulares",
    "title": "Trabajo Práctico 1 - Colas Circulares",
    "description": """
Implementar una estructura de datos de cola circular (Circular Queue) en Python.

Una cola circular es una estructura FIFO (First In, First Out) que utiliza un arreglo
de tamaño fijo y gestiona los índices de forma circular para reutilizar el espacio
cuando se eliminan elementos.

**Objetivos de aprendizaje**:
1. Comprender el concepto de cola circular vs cola simple
2. Implementar operaciones básicas: enqueue(), dequeue(), peek()
3. Manejar índices circulares con aritmética modular
4. Detectar condiciones de lleno/vacío
5. Escribir tests unitarios para validar la implementación
    """.strip(),
    "instructions": """
## Especificación de la Cola Circular

### Interfaz requerida:
```python
class ColaCircular:
    def __init__(self, capacidad: int):
        # Inicializar cola con capacidad fija
        pass

    def enqueue(self, elemento: Any) -> bool:
        # Insertar elemento al final
        # Retornar True si éxito, False si llena
        pass

    def dequeue(self) -> Any:
        # Remover y retornar elemento del frente
        # Lanzar excepción si vacía
        pass

    def peek(self) -> Any:
        # Retornar elemento del frente sin remover
        # Lanzar excepción si vacía
        pass

    def is_empty(self) -> bool:
        # Retornar True si la cola está vacía
        pass

    def is_full(self) -> bool:
        # Retornar True si la cola está llena
        pass

    def size(self) -> int:
        # Retornar cantidad de elementos actuales
        pass
```

### Casos de prueba mínimos:
1. Crear cola de capacidad 5
2. Insertar 5 elementos (verificar que queda llena)
3. Remover 3 elementos
4. Insertar 3 elementos nuevos (verificar wrap-around)
5. Verificar que peek() retorna el elemento correcto
6. Vaciar la cola completamente
7. Intentar dequeue() en cola vacía (debe lanzar excepción)

### Restricciones:
- NO usar estructuras de Python (list, deque, etc.) - implementar con arreglo puro
- Gestionar índices manualmente con aritmética modular
- Tiempo de todas las operaciones debe ser O(1)
    """.strip(),
    "subject": "Programación II",
    "difficulty": "INTERMEDIO",
    "estimated_duration_minutes": 180,  # 3 horas
    "tags": ["colas", "estructuras-de-datos", "arreglos", "algoritmos"],
    "teacher_id": "INST01",
    "status": "active",
    "pedagogical_policies": {
        "max_help_level": "MEDIO",  # MINIMO, BAJO, MEDIO, ALTO
        "block_complete_solutions": True,  # No dar código completo
        "require_justification": True,  # Pedir justificación de decisiones
        "allow_code_snippets": True,  # Permitir snippets pequeños (< 10 líneas)
        "risk_thresholds": {
            "ai_dependency": 0.60,  # Alertar si AI dependency > 60%
            "lack_of_justification": 3,  # Alertar si 3+ respuestas sin justificación
        },
        "tutor_mode": "SOCRATICO",  # SOCRATICO, EXPLICATIVO, GUIADO
        "enable_simulators": True,  # Permitir acceso a simuladores profesionales
        "evaluation_criteria_weights": {
            "problem_decomposition": 0.25,
            "algorithmic_reasoning": 0.25,
            "data_structure_understanding": 0.20,
            "debugging_capability": 0.15,
            "self_regulation": 0.15,
        },
    },
    "evaluation_criteria": [
        {
            "criterion": "Descomposición de problemas",
            "description": "Capacidad de dividir el problema en subproblemas manejables",
            "weight": 0.25,
        },
        {
            "criterion": "Razonamiento algorítmico",
            "description": "Comprensión de la lógica de operaciones y gestión de índices",
            "weight": 0.25,
        },
        {
            "criterion": "Comprensión de estructuras de datos",
            "description": "Entendimiento del concepto de cola circular vs otras estructuras",
            "weight": 0.20,
        },
        {
            "criterion": "Capacidad de debugging",
            "description": "Habilidad para detectar y corregir errores de forma autónoma",
            "weight": 0.15,
        },
        {
            "criterion": "Autorregulación",
            "description": "Monitoreo metacognitivo y ajuste de estrategias de aprendizaje",
            "weight": 0.15,
        },
    ],
}


# ============================================================================
# Helper Functions
# ============================================================================

def create_activities_table(engine):
    """Create activities table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS activities (
        id VARCHAR(255) PRIMARY KEY,
        activity_id VARCHAR(255) UNIQUE NOT NULL,
        title VARCHAR(500) NOT NULL,
        description TEXT,
        instructions TEXT,
        subject VARCHAR(255),
        difficulty VARCHAR(50),
        estimated_duration_minutes INTEGER,
        tags TEXT,
        teacher_id VARCHAR(255),
        status VARCHAR(50) DEFAULT 'active',
        pedagogical_policies TEXT,
        evaluation_criteria TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_activity_teacher_status ON activities(teacher_id, status);
    CREATE INDEX IF NOT EXISTS idx_activity_status_created ON activities(status, created_at);
    CREATE INDEX IF NOT EXISTS idx_activity_subject_status ON activities(subject, status);
    """

    with engine.connect() as conn:
        statements = [s.strip() for s in create_table_sql.split(';') if s.strip()]
        for statement in statements:
            conn.execute(text(statement))
        conn.commit()


def create_activity(session, activity_data: dict):
    """Create a single activity in the database."""
    # Check if activity already exists
    result = session.execute(
        text("SELECT id FROM activities WHERE activity_id = :activity_id"),
        {"activity_id": activity_data["activity_id"]}
    )
    existing = result.fetchone()

    if existing:
        print(f"⚠️  Activity {activity_data['activity_id']} already exists - updating")
        update_activity(session, activity_data)
        return False

    # Generate ID
    activity_id = f"act_{activity_data['activity_id']}"

    # Insert activity
    insert_sql = """
    INSERT INTO activities (
        id, activity_id, title, description, instructions, subject,
        difficulty, estimated_duration_minutes, tags, teacher_id, status,
        pedagogical_policies, evaluation_criteria, created_at
    ) VALUES (
        :id, :activity_id, :title, :description, :instructions, :subject,
        :difficulty, :estimated_duration_minutes, :tags, :teacher_id, :status,
        :pedagogical_policies, :evaluation_criteria, :created_at
    )
    """

    session.execute(text(insert_sql), {
        "id": activity_id,
        "activity_id": activity_data["activity_id"],
        "title": activity_data["title"],
        "description": activity_data["description"],
        "instructions": activity_data["instructions"],
        "subject": activity_data["subject"],
        "difficulty": activity_data["difficulty"],
        "estimated_duration_minutes": activity_data["estimated_duration_minutes"],
        "tags": json.dumps(activity_data["tags"]),
        "teacher_id": activity_data["teacher_id"],
        "status": activity_data["status"],
        "pedagogical_policies": json.dumps(activity_data["pedagogical_policies"]),
        "evaluation_criteria": json.dumps(activity_data["evaluation_criteria"]),
        "created_at": datetime.utcnow(),
    })

    print(f"✅ Created activity: {activity_data['title']}")
    return True


def update_activity(session, activity_data: dict):
    """Update existing activity."""
    update_sql = """
    UPDATE activities SET
        title = :title,
        description = :description,
        instructions = :instructions,
        subject = :subject,
        difficulty = :difficulty,
        estimated_duration_minutes = :estimated_duration_minutes,
        tags = :tags,
        pedagogical_policies = :pedagogical_policies,
        evaluation_criteria = :evaluation_criteria,
        updated_at = :updated_at
    WHERE activity_id = :activity_id
    """

    session.execute(text(update_sql), {
        "activity_id": activity_data["activity_id"],
        "title": activity_data["title"],
        "description": activity_data["description"],
        "instructions": activity_data["instructions"],
        "subject": activity_data["subject"],
        "difficulty": activity_data["difficulty"],
        "estimated_duration_minutes": activity_data["estimated_duration_minutes"],
        "tags": json.dumps(activity_data["tags"]),
        "pedagogical_policies": json.dumps(activity_data["pedagogical_policies"]),
        "evaluation_criteria": json.dumps(activity_data["evaluation_criteria"]),
        "updated_at": datetime.utcnow(),
    })

    print(f"✅ Updated activity: {activity_data['title']}")


def print_activity_summary(activity: dict):
    """Print summary of created activity."""
    print("\n" + "="*80)
    print("UAT TEST ACTIVITY - SUMMARY")
    print("="*80)

    print(f"\n📚 Activity: {activity['title']}")
    print(f"   ID: {activity['activity_id']}")
    print(f"   Subject: {activity['subject']}")
    print(f"   Difficulty: {activity['difficulty']}")
    print(f"   Duration: {activity['estimated_duration_minutes']} minutes")
    print(f"   Status: {activity['status']}")

    print(f"\n🏷️  Tags: {', '.join(activity['tags'])}")

    print("\n📋 Description:")
    print("   " + "\n   ".join(activity['description'].split('\n')[:3]) + "...")

    print("\n⚙️  Pedagogical Policies:")
    policies = activity['pedagogical_policies']
    print(f"   Max Help Level: {policies['max_help_level']}")
    print(f"   Block Complete Solutions: {policies['block_complete_solutions']}")
    print(f"   Require Justification: {policies['require_justification']}")
    print(f"   Allow Code Snippets: {policies['allow_code_snippets']}")
    print(f"   Tutor Mode: {policies['tutor_mode']}")

    print("\n🎯 Evaluation Criteria:")
    for criterion in activity['evaluation_criteria']:
        print(f"   - {criterion['criterion']} ({criterion['weight']*100:.0f}%)")

    print("\n" + "="*80)


# ============================================================================
# Main Execution
# ============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Create UAT test activity")
    parser.add_argument(
        "--database-url",
        type=str,
        help="Database connection URL (default: from .env or SQLite)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without actually creating activity",
    )

    args = parser.parse_args()

    print("="*80)
    print("UAT ACTIVITY CREATION - AI-Native MVP")
    print("="*80)

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No activity will be created\n")
        print_activity_summary(UAT_ACTIVITY)
        print("\n✅ Dry run complete - no changes made")
        return

    # Initialize database
    try:
        if args.database_url:
            from src.ai_native_mvp.database.config import init_database
            init_database(database_url=args.database_url)
            engine = create_engine(args.database_url)
        else:
            from src.ai_native_mvp.database.config import get_db_config, init_database
            init_database()
            config = get_db_config()
            engine = config.get_engine()

        print(f"\n✅ Database connection established")

    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        sys.exit(1)

    # Create activities table if it doesn't exist
    try:
        print("\n📋 Creating activities table (if not exists)...")
        create_activities_table(engine)
        print("✅ Activities table ready")
    except Exception as e:
        print(f"❌ Failed to create activities table: {e}")
        sys.exit(1)

    # Create activity
    with get_db_session() as session:
        print("\n📚 Creating test activity...")
        create_activity(session, UAT_ACTIVITY)
        session.commit()

    # Print summary
    print_activity_summary(UAT_ACTIVITY)

    # Verify activity was created
    with get_db_session() as session:
        result = session.execute(
            text("SELECT COUNT(*) FROM activities WHERE activity_id = :activity_id"),
            {"activity_id": UAT_ACTIVITY["activity_id"]}
        )
        count = result.scalar()
        print(f"\n✅ Verification: Activity exists in database (count: {count})")

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Verify activity is visible in frontend")
    print("2. Test session creation with this activity")
    print("3. Validate pedagogical policies are enforced")
    print("4. Create sample prompts for students to test")
    print("="*80)


if __name__ == "__main__":
    main()