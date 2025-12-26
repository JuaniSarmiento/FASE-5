"""
Seed script for Exercise Database Migration (FASE 3)

Loads exercises from JSON files and populates the database with:
- Subjects (PROG1-Python, PROG2-Java)
- Exercises
- 4 Hints per exercise (with penalties 5, 10, 15, 20 points)
- Standard Rubrics (3 criteria: Funcionalidad 40%, Calidad 30%, Robustez 30%)
- Tests (visible and hidden)
- Exercise attempts (empty, ready for students)

Usage:
    python -m backend.scripts.seed_exercises
    python -m backend.scripts.seed_exercises --dry-run  # Preview without committing
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent.parent
activia_root = project_root / "activia1-main"
sys.path.insert(0, str(activia_root))

from backend.database.config import get_db_config
from backend.database.models import (
    SubjectDB,
    ExerciseDB,
    ExerciseHintDB,
    ExerciseTestDB,
    ExerciseRubricCriterionDB,
    RubricLevelDB,
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# ==================== STANDARD RUBRICS CONFIGURATION ====================
STANDARD_RUBRIC = {
    "criteria": [
        {
            "name": "Funcionalidad",
            "description": "El código cumple con todos los requisitos y casos de uso especificados",
            "weight": 0.40,
            "display_order": 1,
            "levels": [
                {
                    "level_name": "Excelente",
                    "description": "Cumple todos los requisitos y maneja casos edge correctamente",
                    "min_score": 9.0,
                    "max_score": 10.0,
                    "points": 40
                },
                {
                    "level_name": "Bueno",
                    "description": "Cumple la mayoría de requisitos, puede fallar en casos edge",
                    "min_score": 7.0,
                    "max_score": 8.9,
                    "points": 30
                },
                {
                    "level_name": "Regular",
                    "description": "Cumple requisitos básicos pero con errores en casos normales",
                    "min_score": 5.0,
                    "max_score": 6.9,
                    "points": 20
                },
                {
                    "level_name": "Insuficiente",
                    "description": "No cumple los requisitos mínimos o tiene errores críticos",
                    "min_score": 0.0,
                    "max_score": 4.9,
                    "points": 0
                }
            ]
        },
        {
            "name": "Calidad de Código",
            "description": "Código limpio, legible, siguiendo buenas prácticas y estándares",
            "weight": 0.30,
            "display_order": 2,
            "levels": [
                {
                    "level_name": "Excelente",
                    "description": "Código muy limpio, nombres descriptivos, estructura clara, documentado",
                    "min_score": 9.0,
                    "max_score": 10.0,
                    "points": 30
                },
                {
                    "level_name": "Bueno",
                    "description": "Código legible con nombres adecuados, estructura aceptable",
                    "min_score": 7.0,
                    "max_score": 8.9,
                    "points": 22
                },
                {
                    "level_name": "Regular",
                    "description": "Código funcional pero con nombres genéricos o estructura confusa",
                    "min_score": 5.0,
                    "max_score": 6.9,
                    "points": 15
                },
                {
                    "level_name": "Insuficiente",
                    "description": "Código ilegible, nombres crípticos, muy difícil de mantener",
                    "min_score": 0.0,
                    "max_score": 4.9,
                    "points": 0
                }
            ]
        },
        {
            "name": "Robustez",
            "description": "Manejo de errores, validaciones y casos extremos",
            "weight": 0.30,
            "display_order": 3,
            "levels": [
                {
                    "level_name": "Excelente",
                    "description": "Manejo completo de errores, validaciones exhaustivas, mensajes claros",
                    "min_score": 9.0,
                    "max_score": 10.0,
                    "points": 30
                },
                {
                    "level_name": "Bueno",
                    "description": "Maneja errores principales, validaciones básicas implementadas",
                    "min_score": 7.0,
                    "max_score": 8.9,
                    "points": 22
                },
                {
                    "level_name": "Regular",
                    "description": "Manejo mínimo de errores, falta validación de entradas",
                    "min_score": 5.0,
                    "max_score": 6.9,
                    "points": 15
                },
                {
                    "level_name": "Insuficiente",
                    "description": "Sin manejo de errores, crashea con entradas inesperadas",
                    "min_score": 0.0,
                    "max_score": 4.9,
                    "points": 0
                }
            ]
        }
    ]
}

# ==================== HINT PENALTIES CONFIGURATION ====================
HINT_PENALTIES = [5, 10, 15, 20]  # Points deducted for each hint


class ExerciseSeeder:
    """Seeds exercise database from JSON files"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.db_config = get_db_config()
        self.engine = self.db_config.get_engine()
        self.Session = self.db_config.get_session_factory()
        # Path to exercises is relative to the script location
        self.exercises_dir = Path(__file__).parent.parent / "data" / "exercises"

        # Statistics
        self.stats = {
            "subjects": 0,
            "exercises": 0,
            "hints": 0,
            "tests": 0,
            "criteria": 0,
            "levels": 0
        }

    def run(self):
        """Main seeding process"""
        logger.info("=" * 70)
        logger.info("EXERCISE DATABASE SEED - FASE 3")
        logger.info("=" * 70)

        if self.dry_run:
            logger.warning("DRY RUN MODE - No changes will be committed")

        session = self.Session()

        try:
            # Step 1: Create subjects
            logger.info("\n[1/4] Creating subjects...")
            self.create_subjects(session)

            # Step 2: Load and create exercises
            logger.info("\n[2/4] Loading exercises from JSON files...")
            exercises_data = self.load_all_exercises()
            logger.info(f"Found {len(exercises_data)} exercises in JSON files")

            logger.info("\n[3/4] Creating exercises with hints, tests, and rubrics...")
            self.create_exercises(session, exercises_data)

            # Step 4: Summary
            logger.info("\n[4/4] Summary:")
            logger.info(f"  ✓ Subjects created: {self.stats['subjects']}")
            logger.info(f"  ✓ Exercises created: {self.stats['exercises']}")
            logger.info(f"  ✓ Hints created: {self.stats['hints']}")
            logger.info(f"  ✓ Tests created: {self.stats['tests']}")
            logger.info(f"  ✓ Rubric criteria created: {self.stats['criteria']}")
            logger.info(f"  ✓ Rubric levels created: {self.stats['levels']}")

            if not self.dry_run:
                session.commit()
                logger.info("\n✅ Database seeded successfully!")
            else:
                session.rollback()
                logger.info("\n🔍 DRY RUN completed - no changes committed")

        except Exception as e:
            session.rollback()
            logger.error(f"\n❌ Error during seeding: {e}")
            raise
        finally:
            session.close()

    def create_subjects(self, session):
        """Create subjects: PROG1 (Python) and PROG2 (Java)"""
        subjects = [
            SubjectDB(
                code="PROG1",
                name="Programación 1",
                description="Fundamentos de programación con Python",
                language="python",
                is_active=True
            ),
            SubjectDB(
                code="PROG2",
                name="Programación 2",
                description="Programación orientada a objetos con Java",
                language="java",
                is_active=True
            )
        ]

        for subject in subjects:
            session.add(subject)
            logger.info(f"  + Subject: {subject.code} - {subject.name}")
            self.stats["subjects"] += 1

    def load_all_exercises(self) -> List[Dict[str, Any]]:
        """Load exercises from all JSON files"""
        all_exercises = []

        json_files = [
            "unit1_fundamentals.json",
            "unit2_structures.json",
            "unit3_functions.json",
            "unit4_files.json",
            "unit5_oop.json",
            "unit6_java_fundamentals.json",
            "unit7_springboot.json"
        ]

        for filename in json_files:
            filepath = self.exercises_dir / filename
            if not filepath.exists():
                logger.warning(f"  ⚠ File not found: {filename}")
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    exercises = json.load(f)
                    all_exercises.extend(exercises)
                    logger.info(f"  ✓ Loaded {len(exercises)} exercises from {filename}")
            except Exception as e:
                logger.error(f"  ✗ Error loading {filename}: {e}")

        return all_exercises

    def create_exercises(self, session, exercises_data: List[Dict[str, Any]]):
        """Create exercises with all related data"""

        for ex_data in exercises_data:
            try:
                # Determine subject based on exercise ID or language
                subject_code = self._get_subject_code(ex_data)
                unit_number = self._extract_unit_number(ex_data["id"])

                # Create exercise
                exercise = ExerciseDB(
                    id=ex_data["id"],
                    subject_code=subject_code,
                    unit=unit_number,
                    title=ex_data["meta"]["title"],
                    description=ex_data["content"]["story_markdown"][:500] if "story_markdown" in ex_data["content"] else "",
                    difficulty=ex_data["meta"]["difficulty"],
                    time_min=ex_data["meta"].get("estimated_time_min", 30),  # Changed field name
                    tags=ex_data["meta"]["tags"],
                    language=ex_data["ui_config"].get("editor_language", "python"),
                    mission_markdown=ex_data["content"].get("mission_markdown", ""),
                    story_markdown=ex_data["content"].get("story_markdown", ""),
                    constraints=ex_data["content"].get("constraints", []),
                    starter_code=ex_data.get("starter_code", ""),
                    max_score=100,
                    is_active=True
                )
                session.add(exercise)
                self.stats["exercises"] += 1
                logger.info(f"  ✓ Exercise: {exercise.id} - {exercise.title}")

                # Create 4 hints
                self._create_hints(session, exercise.id, ex_data)

                # Create tests
                self._create_tests(session, exercise.id, ex_data)

                # Create standard rubric
                self._create_rubric(session, exercise.id)

            except Exception as e:
                logger.error(f"  ✗ Error creating exercise {ex_data.get('id', 'UNKNOWN')}: {e}")

    def _create_hints(self, session, exercise_id: str, ex_data: Dict[str, Any]):
        """Generate 4 hints for an exercise"""

        # Generic hints based on difficulty
        difficulty = ex_data["meta"]["difficulty"]

        hint_templates = {
            "Easy": [
                "Lee cuidadosamente los requisitos en la sección 'Tu Misión'. ¿Qué variables necesitas declarar?",
                "Revisa el código inicial (starter_code). ¿Qué partes necesitas completar o modificar?",
                "Piensa en el flujo de datos: entrada → procesamiento → salida. ¿Cuál es cada uno en este ejercicio?",
                "Consulta la documentación oficial de Python sobre el tema principal de este ejercicio. Busca ejemplos similares."
            ],
            "Medium": [
                "Descompón el problema en funciones más pequeñas. ¿Qué responsabilidades tiene cada una?",
                "Revisa las restricciones (constraints). ¿Estás cumpliendo todas las buenas prácticas mencionadas?",
                "Piensa en los casos edge: ¿qué pasa con entradas vacías, negativas o valores extremos?",
                "Usa print() para depurar: imprime valores intermedios y verifica que sean los esperados."
            ],
            "Hard": [
                "Dibuja un diagrama de la estructura de datos o el flujo del algoritmo antes de codificar.",
                "Identifica las estructuras de datos apropiadas (listas, diccionarios, sets, clases). ¿Cuál optimiza tu solución?",
                "Considera la complejidad temporal: ¿tu algoritmo escala bien con datos grandes?",
                "Revisa los principios SOLID o patrones de diseño que apliquen a este problema."
            ]
        }

        hints = hint_templates.get(difficulty, hint_templates["Medium"])

        for i, hint_text in enumerate(hints, start=1):
            hint = ExerciseHintDB(
                id=str(uuid.uuid4()),
                exercise_id=exercise_id,
                hint_number=i,
                title=f"Pista {i}",
                content=hint_text,  # Changed from hint_text to content
                penalty_points=HINT_PENALTIES[i - 1]
            )
            session.add(hint)
            self.stats["hints"] += 1

    def _create_tests(self, session, exercise_id: str, ex_data: Dict[str, Any]):
        """Create tests from JSON data"""

        hidden_tests = ex_data.get("hidden_tests", [])

        # Create visible test (first one is visible)
        if hidden_tests:
            test1 = ExerciseTestDB(
                id=str(uuid.uuid4()),
                exercise_id=exercise_id,
                test_number=1,
                description="Test básico de funcionalidad",
                input=hidden_tests[0].get("input", ""),  # Changed from input_data
                expected=hidden_tests[0].get("expected", ""),  # Changed from expected_output
                is_hidden=False
            )
            session.add(test1)
            self.stats["tests"] += 1

        # Create hidden tests
        for i, test_data in enumerate(hidden_tests[1:], start=2):
            test = ExerciseTestDB(
                id=str(uuid.uuid4()),
                exercise_id=exercise_id,
                test_number=i,
                description=f"Test oculto #{i - 1}",
                input=test_data.get("input", ""),  # Changed from input_data
                expected=test_data.get("expected", ""),  # Changed from expected_output
                is_hidden=True
            )
            session.add(test)
            self.stats["tests"] += 1

    def _create_rubric(self, session, exercise_id: str):
        """Create standard rubric for an exercise"""

        for criterion_data in STANDARD_RUBRIC["criteria"]:
            # Create criterion
            criterion = ExerciseRubricCriterionDB(
                id=str(uuid.uuid4()),
                exercise_id=exercise_id,
                criterion_name=criterion_data["name"],
                description=criterion_data["description"],
                weight=criterion_data["weight"],
                display_order=criterion_data["display_order"]
            )
            session.add(criterion)
            self.stats["criteria"] += 1

            # Create levels for this criterion
            for level_data in criterion_data["levels"]:
                level = RubricLevelDB(
                    id=str(uuid.uuid4()),
                    criterion_id=criterion.id,
                    level_name=level_data["level_name"],
                    description=level_data["description"],
                    min_score=level_data["min_score"],
                    max_score=level_data["max_score"],
                    points=level_data["points"]
                )
                session.add(level)
                self.stats["levels"] += 1

    def _get_subject_code(self, ex_data: Dict[str, Any]) -> str:
        """Determine subject code based on exercise data"""
        exercise_id = ex_data["id"]
        language = ex_data["ui_config"].get("editor_language", "python")

        # Java exercises (U6, U7)
        if exercise_id.startswith("U6-") or exercise_id.startswith("U7-") or language == "java":
            return "PROG2"

        # Python exercises (U1-U5)
        return "PROG1"

    def _extract_unit_number(self, exercise_id: str) -> int:
        """Extract unit number from exercise ID (e.g., 'U1-VAR-01' -> 1)"""
        try:
            return int(exercise_id.split("-")[0][1:])
        except:
            return 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Seed exercise database from JSON files")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without committing")
    args = parser.parse_args()

    seeder = ExerciseSeeder(dry_run=args.dry_run)
    seeder.run()


if __name__ == "__main__":
    main()
