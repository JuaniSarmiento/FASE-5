"""
Script de utilidad para cargar ejercicios desde archivos JSON.

Este módulo proporciona funciones para:
1. Cargar ejercicios individuales por ID
2. Cargar todos los ejercicios de una unidad
3. Listar todos los ejercicios disponibles
4. Filtrar ejercicios por dificultad, tags, etc.

Uso:
    from backend.data.exercises.loader import ExerciseLoader
    
    loader = ExerciseLoader()
    exercise = loader.get_by_id("U1-VAR-01")
    all_exercises = loader.get_all()
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any


class ExerciseLoader:
    """Carga y gestiona ejercicios desde archivos JSON."""
    
    EXERCISES_DIR = Path(__file__).parent
    UNITS = [
        "unit1_fundamentals.json",
        "unit2_structures.json",
        "unit3_functions.json",
        "unit4_files.json",
        "unit5_oop.json",
        "unit6_java_fundamentals.json",
        "unit7_springboot.json",
    ]
    
    def __init__(self):
        """Inicializa el loader."""
        self._cache: Dict[str, Any] = {}
        self._load_all_exercises()
    
    def _load_all_exercises(self) -> None:
        """Carga todos los ejercicios en el caché."""
        for unit_file in self.UNITS:
            file_path = self.EXERCISES_DIR / unit_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    exercises = json.load(f)
                    for exercise in exercises:
                        self._cache[exercise['id']] = exercise
    
    def get_by_id(self, exercise_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un ejercicio por su ID.
        
        Args:
            exercise_id: ID del ejercicio (ej: "U1-VAR-01")
        
        Returns:
            Diccionario con el ejercicio o None si no existe
        """
        return self._cache.get(exercise_id)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los ejercicios.
        
        Returns:
            Lista de todos los ejercicios
        """
        return list(self._cache.values())
    
    def get_by_unit(self, unit: int) -> List[Dict[str, Any]]:
        """
        Obtiene ejercicios de una unidad específica.
        
        Args:
            unit: Número de unidad (1-5)
        
        Returns:
            Lista de ejercicios de esa unidad
        """
        unit_prefix = f"U{unit}-"
        return [
            ex for ex in self._cache.values()
            if ex['id'].startswith(unit_prefix)
        ]
    
    def get_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """
        Filtra ejercicios por dificultad.
        
        Args:
            difficulty: "Easy", "Medium", o "Hard"
        
        Returns:
            Lista de ejercicios con esa dificultad
        """
        return [
            ex for ex in self._cache.values()
            if ex['meta']['difficulty'] == difficulty
        ]
    
    def get_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """
        Filtra ejercicios por tag.
        
        Args:
            tag: Tag a buscar (ej: "CSV", "POO")
        
        Returns:
            Lista de ejercicios con ese tag
        """
        return [
            ex for ex in self._cache.values()
            if tag in ex['meta']['tags']
        ]
    
    def search(
        self,
        difficulty: Optional[str] = None,
        tags: Optional[List[str]] = None,
        unit: Optional[int] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda avanzada de ejercicios.
        
        Args:
            difficulty: Filtrar por dificultad ("Easy", "Medium", "Hard")
            tags: Lista de tags (OR logic)
            unit: Filtrar por unidad (1-7)
            language: Filtrar por lenguaje ("python", "java")
            framework: Filtrar por framework ("spring-boot")
        
        Returns:
            Lista de ejercicios que cumplen los criterios
        """
        results = self.get_all()
        
        if difficulty:
            results = [ex for ex in results if ex['meta']['difficulty'] == difficulty]
        
        if tags:
            results = [
                ex for ex in results
                if any(tag in ex['meta']['tags'] for tag in tags)
            ]
        
        if unit:
            results = [ex for ex in results if ex['id'].startswith(f"U{unit}-")]
        
        if language:
            results = [
                ex for ex in results
                if ex['meta'].get('language', 'python') == language
            ]
        
        if framework:
            results = [
                ex for ex in results
                if ex['meta'].get('framework') == framework
            ]
        
        if language:
            results = [
                ex for ex in results
                if ex['ui_config']['editor_language'] == language
            ]
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de los ejercicios.
        
        Returns:
            Diccionario con estadísticas
        """
        exercises = self.get_all()
        
        difficulty_counts = {
            'Easy': 0,
            'Medium': 0,
            'Hard': 0,
        }
        
        language_counts = {}
        framework_counts = {}
        total_time = 0
        all_tags = set()
        
        for ex in exercises:
            difficulty_counts[ex['meta']['difficulty']] += 1
            total_time += ex['meta']['estimated_time_min']
            all_tags.update(ex['meta']['tags'])
            
            # Conteo por lenguaje
            lang = ex['meta'].get('language', 'python')
            language_counts[lang] = language_counts.get(lang, 0) + 1
            
            # Conteo por framework
            fw = ex['meta'].get('framework')
            if fw:
                framework_counts[fw] = framework_counts.get(fw, 0) + 1
        
        return {
            'total_exercises': len(exercises),
            'by_difficulty': difficulty_counts,
            'by_language': language_counts,
            'by_framework': framework_counts,
            'total_time_min': total_time,
            'total_time_hours': round(total_time / 60, 1),
            'unique_tags': len(all_tags),
            'tags': sorted(list(all_tags)),
            'units': len(self.UNITS),
        }
    
    def get_available_filters(self) -> Dict[str, List[str]]:
        """
        Obtiene los valores disponibles para cada filtro.
        
        Returns:
            Diccionario con listas de valores disponibles
        """
        exercises = self.get_all()
        
        difficulties = set()
        languages = set()
        frameworks = set()
        tags = set()
        units = set()
        
        for ex in exercises:
            difficulties.add(ex['meta']['difficulty'])
            languages.add(ex['meta'].get('language', 'python'))
            tags.update(ex['meta']['tags'])
            
            fw = ex['meta'].get('framework')
            if fw:
                frameworks.add(fw)
            
            # Extraer número de unidad del ID (ej: "U1-VAR-01" -> 1)
            unit_num = int(ex['id'].split('-')[0][1:])
            units.add(unit_num)
        
        return {
            'difficulties': sorted(list(difficulties)),
            'languages': sorted(list(languages)),
            'frameworks': sorted(list(frameworks)),
            'tags': sorted(list(tags)),
            'units': sorted(list(units)),
        }


# Instancia global para uso directo
exercise_loader = ExerciseLoader()


# Funciones de conveniencia
def get_exercise(exercise_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene un ejercicio por ID."""
    return exercise_loader.get_by_id(exercise_id)


def list_exercises(**filters) -> List[Dict[str, Any]]:
    """Lista ejercicios con filtros opcionales."""
    if not filters:
        return exercise_loader.get_all()
    return exercise_loader.search(**filters)


def get_exercise_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de ejercicios."""
    return exercise_loader.get_stats()


# Script de prueba
if __name__ == "__main__":
    print("=== Sistema de Ejercicios ===\n")
    
    # Estadísticas
    stats = get_exercise_stats()
    print(f"Total de ejercicios: {stats['total_exercises']}")
    print(f"Tiempo total: {stats['total_time_hours']} horas")
    print(f"\nPor dificultad:")
    for diff, count in stats['by_difficulty'].items():
        print(f"  {diff}: {count}")
    
    print(f"\nTags únicos: {', '.join(stats['tags'])}")
    
    # Ejemplo: Obtener ejercicio específico
    print("\n=== Ejercicio U1-VAR-01 ===")
    exercise = get_exercise("U1-VAR-01")
    if exercise:
        print(f"Título: {exercise['meta']['title']}")
        print(f"Dificultad: {exercise['meta']['difficulty']}")
        print(f"Tiempo: {exercise['meta']['estimated_time_min']} min")
        print(f"Tags: {', '.join(exercise['meta']['tags'])}")
    
    # Ejemplo: Filtrar por dificultad
    print("\n=== Ejercicios Hard ===")
    hard_exercises = list_exercises(difficulty="Hard")
    for ex in hard_exercises:
        print(f"  - {ex['id']}: {ex['meta']['title']}")
    
    # Ejemplo: Filtrar por tag
    print("\n=== Ejercicios de POO ===")
    oop_exercises = list_exercises(tags=["POO"])
    for ex in oop_exercises:
        print(f"  - {ex['id']}: {ex['meta']['title']}")
