"""
Script rápido para demostrar el filtrado del Entrenador Digital
"""

from backend.data.exercises.loader import ExerciseLoader

loader = ExerciseLoader()

print("=" * 80)
print("🎯 ENTRENADOR DIGITAL - FILTROS EN ACCIÓN")
print("=" * 80)

# Estadísticas generales
stats = loader.get_stats()
print(f"\n📊 ESTADÍSTICAS GENERALES:")
print(f"   Total ejercicios: {stats['total_exercises']}")
print(f"   Por lenguaje: Python={stats['by_language']['python']}, Java={stats['by_language']['java']}")
print(f"   Por framework: Spring Boot={stats['by_framework']['spring-boot']}")
print(f"   Tiempo total: {stats['total_time_hours']:.1f} horas")

# Filtro 1: Ejercicios de Java
print(f"\n🔵 EJERCICIOS DE JAVA:")
java_ex = loader.search(language='java')
for ex in java_ex:
    print(f"   - {ex['id']}: {ex['meta']['title']} ({ex['meta']['difficulty']})")

# Filtro 2: Ejercicios de Spring Boot
print(f"\n🍃 EJERCICIOS DE SPRING BOOT:")
spring_ex = loader.search(framework='spring-boot')
for ex in spring_ex:
    print(f"   - {ex['id']}: {ex['meta']['title']} ({ex['meta']['difficulty']})")

# Filtro 3: Ejercicios difíciles
print(f"\n🔥 EJERCICIOS DIFÍCILES (Hard):")
hard_ex = loader.search(difficulty='Hard')
for ex in hard_ex:
    lang = ex['meta'].get('language', 'python')
    print(f"   - {ex['id']}: {ex['meta']['title']} [{lang.upper()}]")

# Filtro 4: Ejercicios fáciles de Java
print(f"\n✅ EJERCICIOS FÁCILES DE JAVA:")
easy_java = loader.search(language='java', difficulty='Easy')
for ex in easy_java:
    print(f"   - {ex['id']}: {ex['meta']['title']}")

print("\n" + "=" * 80)
print("✅ Sistema de filtrado funcionando perfectamente")
print("=" * 80)
