"""
Script para inicializar los 10 ejercicios de Python en la base de datos
"""
from sqlalchemy.orm import Session
from backend.database.config import SessionLocal
from backend.models.exercise import Exercise
import json


def create_exercises(db: Session):
    """Crea 10 ejercicios de Python progresivos"""
    
    exercises_data = [
        {
            "title": "Nivel 1: Suma de Dos Números",
            "description": "Escribe una función llamada 'sumar' que reciba dos números y devuelva su suma. Imprime el resultado.",
            "difficulty_level": 1,
            "starter_code": "def sumar(a, b):\n    # Tu código aquí\n    pass\n\n# Prueba tu función\nresultado = sumar(5, 3)\nprint(resultado)",
            "test_cases": [
                {"input": "", "expected_output": "8"},
                {"input": "", "expected_output": "8"},
            ],
            "hints": ["Usa el operador +", "Retorna el resultado con 'return'"],
            "max_score": 10.0,
            "time_limit_seconds": 60
        },
        {
            "title": "Nivel 2: Número Par o Impar",
            "description": "Escribe una función 'es_par' que reciba un número y devuelva True si es par, False si es impar. Imprime el resultado para el número 10.",
            "difficulty_level": 2,
            "starter_code": "def es_par(numero):\n    # Tu código aquí\n    pass\n\nprint(es_par(10))",
            "test_cases": [
                {"input": "", "expected_output": "True"},
            ],
            "hints": ["Usa el operador módulo %", "Un número es par si numero % 2 == 0"],
            "max_score": 10.0,
            "time_limit_seconds": 90
        },
        {
            "title": "Nivel 3: Factorial de un Número",
            "description": "Implementa una función 'factorial' que calcule el factorial de un número entero positivo. Imprime factorial(5).",
            "difficulty_level": 3,
            "starter_code": "def factorial(n):\n    # Tu código aquí\n    pass\n\nprint(factorial(5))",
            "test_cases": [
                {"input": "", "expected_output": "120"},
            ],
            "hints": ["Usa un bucle for o recursión", "5! = 5 * 4 * 3 * 2 * 1 = 120"],
            "max_score": 10.0,
            "time_limit_seconds": 120
        },
        {
            "title": "Nivel 4: Invertir una Cadena",
            "description": "Crea una función 'invertir_cadena' que reciba un string y devuelva el string invertido. Imprime invertir_cadena('Python').",
            "difficulty_level": 4,
            "starter_code": "def invertir_cadena(texto):\n    # Tu código aquí\n    pass\n\nprint(invertir_cadena('Python'))",
            "test_cases": [
                {"input": "", "expected_output": "nohtyP"},
            ],
            "hints": ["Usa slicing [::-1]", "O recorre el string en reversa"],
            "max_score": 10.0,
            "time_limit_seconds": 120
        },
        {
            "title": "Nivel 5: Fibonacci",
            "description": "Escribe una función 'fibonacci' que genere los primeros n números de la secuencia de Fibonacci. Imprime fibonacci(10) como lista.",
            "difficulty_level": 5,
            "starter_code": "def fibonacci(n):\n    # Tu código aquí\n    pass\n\nprint(fibonacci(10))",
            "test_cases": [
                {"input": "", "expected_output": "[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]"},
            ],
            "hints": ["Usa una lista para guardar los números", "Cada número es la suma de los dos anteriores"],
            "max_score": 10.0,
            "time_limit_seconds": 180
        },
        {
            "title": "Nivel 6: Palíndromo",
            "description": "Implementa 'es_palindromo' que determine si una palabra es un palíndromo (se lee igual al derecho y al revés). Imprime es_palindromo('radar').",
            "difficulty_level": 6,
            "starter_code": "def es_palindromo(palabra):\n    # Tu código aquí\n    pass\n\nprint(es_palindromo('radar'))",
            "test_cases": [
                {"input": "", "expected_output": "True"},
            ],
            "hints": ["Compara la palabra con su reverso", "Ignora mayúsculas/minúsculas con .lower()"],
            "max_score": 10.0,
            "time_limit_seconds": 180
        },
        {
            "title": "Nivel 7: Ordenamiento Burbuja",
            "description": "Implementa el algoritmo de ordenamiento burbuja. La función 'bubble_sort' debe recibir una lista y devolverla ordenada. Imprime bubble_sort([64, 34, 25, 12, 22, 11, 90]).",
            "difficulty_level": 7,
            "starter_code": "def bubble_sort(lista):\n    # Tu código aquí\n    pass\n\nprint(bubble_sort([64, 34, 25, 12, 22, 11, 90]))",
            "test_cases": [
                {"input": "", "expected_output": "[11, 12, 22, 25, 34, 64, 90]"},
            ],
            "hints": ["Usa dos bucles anidados", "Compara e intercambia elementos adyacentes"],
            "max_score": 10.0,
            "time_limit_seconds": 240
        },
        {
            "title": "Nivel 8: Búsqueda Binaria",
            "description": "Implementa búsqueda binaria. La función 'busqueda_binaria' debe recibir una lista ordenada y un valor, y devolver el índice del valor (o -1 si no existe). Imprime busqueda_binaria([1, 3, 5, 7, 9, 11, 13, 15], 7).",
            "difficulty_level": 8,
            "starter_code": "def busqueda_binaria(lista, valor):\n    # Tu código aquí\n    pass\n\nprint(busqueda_binaria([1, 3, 5, 7, 9, 11, 13, 15], 7))",
            "test_cases": [
                {"input": "", "expected_output": "3"},
            ],
            "hints": ["Divide la lista a la mitad en cada paso", "Compara el valor con el elemento del medio"],
            "max_score": 10.0,
            "time_limit_seconds": 300
        },
        {
            "title": "Nivel 9: Generador de Números Primos",
            "description": "Crea una función 'primos_hasta' que genere todos los números primos menores o iguales a n. Imprime primos_hasta(20) como lista.",
            "difficulty_level": 9,
            "starter_code": "def primos_hasta(n):\n    # Tu código aquí\n    pass\n\nprint(primos_hasta(20))",
            "test_cases": [
                {"input": "", "expected_output": "[2, 3, 5, 7, 11, 13, 17, 19]"},
            ],
            "hints": ["Un número primo solo es divisible por 1 y por sí mismo", "Usa la Criba de Eratóstenes para eficiencia"],
            "max_score": 10.0,
            "time_limit_seconds": 300
        },
        {
            "title": "Nivel 10: Algoritmo de Dijkstra Simplificado",
            "description": "Implementa una versión simplificada del algoritmo de Dijkstra. Dado un grafo representado como diccionario de adyacencias con pesos, encuentra el camino más corto desde 'A' hasta 'D'. Imprime la distancia mínima. Grafo: {'A': {'B': 1, 'C': 4}, 'B': {'C': 2, 'D': 5}, 'C': {'D': 1}, 'D': {}}",
            "difficulty_level": 10,
            "starter_code": "def dijkstra(grafo, inicio, fin):\n    # Tu código aquí\n    pass\n\ngrafo = {'A': {'B': 1, 'C': 4}, 'B': {'C': 2, 'D': 5}, 'C': {'D': 1}, 'D': {}}\nprint(dijkstra(grafo, 'A', 'D'))",
            "test_cases": [
                {"input": "", "expected_output": "4"},
            ],
            "hints": ["Usa una cola de prioridad o un conjunto para nodos visitados", "Actualiza distancias mientras exploras nodos"],
            "max_score": 10.0,
            "time_limit_seconds": 360
        }
    ]
    
    # Eliminar ejercicios existentes (solo para inicialización limpia)
    db.query(Exercise).delete()
    db.commit()
    
    # Crear ejercicios
    for ex_data in exercises_data:
        exercise = Exercise(**ex_data)
        db.add(exercise)
    
    db.commit()
    print(f"✅ {len(exercises_data)} ejercicios creados exitosamente")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_exercises(db)
    finally:
        db.close()
