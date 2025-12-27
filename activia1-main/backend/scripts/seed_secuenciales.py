"""
Seed script para Ejercicios de Estructuras Secuenciales en Python

Carga 10 ejercicios de programación secuencial con:
- Consignas completas
- 4 pistas graduales por ejercicio (penalizaciones: 5, 10, 15, 20 pts)
- 3-5 tests automáticos por ejercicio (visibles y ocultos)
- Rúbricas estándar

Basado en los archivos:
- SecuencialesCo.txt (soluciones)
- PistasSecuenciales.txt (pistas)
- rubricaSecuenciales.pdf (criterios de evaluación)

Usage:
    cd activia1-main
    python -m backend.scripts.seed_secuenciales
    python -m backend.scripts.seed_secuenciales --dry-run  # Preview sin commit
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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


# ============================================================================
# CONFIGURACIÓN DE EJERCICIOS SECUENCIALES
# ============================================================================

EJERCICIOS_SECUENCIALES = [
    {
        "id": "SEC-01",
        "title": "Hola Mundo",
        "difficulty": "Easy",
        "time_min": 5,
        "max_score": 12,
        "mission_markdown": """# Ejercicio 1: Hola Mundo

## Objetivo
Crear un programa que imprima por pantalla el mensaje: "Hola Mundo!".

## Instrucciones
- Utiliza la función `print()` para mostrar el mensaje
- El mensaje debe ser exactamente: "Hola Mundo!" (con signo de exclamación)

## Ejemplo de salida esperada
```
Hola Mundo!
```
""",
        "starter_code": "# Escribe tu código aquí\n",
        "solution_code": 'print("Hola Mundo!")',
        "tags": ["print", "strings", "fundamentos"],
        "learning_objectives": ["Usar la función print()", "Sintaxis básica de Python", "Strings con comillas"]
    },
    {
        "id": "SEC-02",
        "title": "Saludo Personalizado",
        "difficulty": "Easy",
        "time_min": 10,
        "max_score": 16,
        "mission_markdown": """# Ejercicio 2: Saludo Personalizado

## Objetivo
Crear un programa que pida al usuario su nombre e imprima por pantalla un saludo usando el nombre ingresado.

## Instrucciones
- Usa `input()` para pedir el nombre al usuario
- Guarda el nombre en una variable
- Imprime un saludo personalizado usando f-strings

## Ejemplo
Si el usuario ingresa "Marcos", el programa debe imprimir:
```
Hola Marcos!
```

## Consejo
Utiliza f-strings para combinar texto y variables: `print(f"Hola {variable}!")`
""",
        "starter_code": "# Escribe tu código aquí\n",
        "solution_code": """nombre = input("Por favor, ingrese su nombre: ")
print(f"Hola {nombre}!")""",
        "tags": ["input", "variables", "f-strings"],
        "learning_objectives": ["Usar input()", "Almacenar datos en variables", "Formatear strings con f-strings"]
    },
    {
        "id": "SEC-03",
        "title": "Datos Personales",
        "difficulty": "Easy",
        "time_min": 15,
        "max_score": 16,
        "mission_markdown": """# Ejercicio 3: Datos Personales

## Objetivo
Crear un programa que pida al usuario su nombre, apellido, edad y lugar de residencia e imprima por pantalla una oración con los datos ingresados.

## Instrucciones
- Solicita 4 datos al usuario: nombre, apellido, edad, lugar de residencia
- Guarda cada dato en una variable diferente
- Imprime una oración que integre todos los datos

## Ejemplo
Si el usuario ingresa "Marcos", "Pérez", "30" y "Argentina", el programa debe imprimir:
```
Soy Marcos Pérez, tengo 30 años y vivo en Argentina.
```

## Consejo
Usa f-strings para combinar múltiples variables en una sola oración.
""",
        "starter_code": "# Escribe tu código aquí\n",
        "solution_code": """nombre = input("Por favor, ingrese su nombre: ")
apellido = input("Por favor, ingrese su apellido: ")
edad = input("Por favor, ingrese su edad: ")
lugar_de_residencia = input("Por favor, ingrese su lugar de residencia: ")
print(f"Soy {nombre} {apellido}, tengo {edad} años y vivo en {lugar_de_residencia}.")""",
        "tags": ["input", "variables", "f-strings", "concatenacion"],
        "learning_objectives": ["Solicitar múltiples datos", "Usar variables descriptivas", "Formatear oraciones complejas"]
    },
    {
        "id": "SEC-04",
        "title": "Área y Perímetro de un Círculo",
        "difficulty": "Medium",
        "time_min": 20,
        "max_score": 24,
        "mission_markdown": """# Ejercicio 4: Área y Perímetro de un Círculo

## Objetivo
Crear un programa que pida al usuario el radio de un círculo e imprima por pantalla su área y su perímetro.

## Fórmulas
- **Área del círculo:** π * r²
- **Perímetro (circunferencia):** 2 * π * r

## Instrucciones
- Importa la librería `math` para usar `math.pi`
- Solicita el radio del círculo al usuario
- Convierte el input a `float` para permitir decimales
- Calcula el área y el perímetro
- Usa `round(resultado, 2)` para redondear a 2 decimales

## Ejemplo
Si el usuario ingresa radio = 5:
```
El área del círculo es de 78.54 y el perímetro es de 31.42.
```

## Consejo
Para elevar al cuadrado usa el operador `**`: `radio ** 2`
""",
        "starter_code": "import math\n\n# Escribe tu código aquí\n",
        "solution_code": """import math

radio_circulo = float(input("Por favor, ingrese el radio del círculo: "))
area_circulo = round(math.pi * (radio_circulo ** 2), 2)
perimetro_circulo = round(2 * math.pi * radio_circulo, 2)
print(f"El área del círculo es de {area_circulo} y el perímetro es de {perimetro_circulo}.")""",
        "tags": ["math", "calculos", "float", "round"],
        "learning_objectives": ["Importar librerías", "Usar constantes matemáticas", "Realizar cálculos con fórmulas", "Redondear resultados"]
    },
    {
        "id": "SEC-05",
        "title": "Conversión de Segundos a Horas",
        "difficulty": "Easy",
        "time_min": 10,
        "max_score": 20,
        "mission_markdown": """# Ejercicio 5: Conversión de Segundos a Horas

## Objetivo
Crear un programa que pida al usuario una cantidad de segundos e imprima por pantalla a cuántas horas equivale.

## Fórmula
- 1 hora = 3600 segundos
- Para convertir: horas = segundos / 3600

## Instrucciones
- Solicita la cantidad de segundos al usuario
- Convierte a `float` para permitir decimales
- Divide entre 3600 para obtener las horas
- Redondea a 2 decimales

## Ejemplo
Si el usuario ingresa 7200 segundos:
```
El equivalente a 7200.0 segundos son 2.0 horas.
```
""",
        "starter_code": "# Escribe tu código aquí\n",
        "solution_code": """cantidad_segundos = float(input("Por favor, ingrese la cantidad de segundos a convertir: "))
cantidad_horas = round(cantidad_segundos / 3600, 2)
print(f"El equivalente a {cantidad_segundos} segundos son {cantidad_horas} horas.")""",
        "tags": ["conversiones", "aritmetica", "division"],
        "learning_objectives": ["Realizar conversiones de unidades", "División en Python", "Trabajar con decimales"]
    },
    {
        "id": "SEC-06",
        "title": "Tabla de Multiplicar",
        "difficulty": "Medium",
        "time_min": 15,
        "max_score": 20,
        "mission_markdown": """# Ejercicio 6: Tabla de Multiplicar

## Objetivo
Crear un programa que pida al usuario un número entero e imprima por pantalla la tabla de multiplicar de dicho número (del 0 al 9).

## Ejemplo
Si el usuario ingresa 5, el programa debe mostrar:
```
5 x 0 = 0
5 x 1 = 5
5 x 2 = 10
5 x 3 = 15
...
5 x 9 = 45
```

## Instrucciones
- Solicita un número entero (usa `int()` para convertir)
- Usa un string multilínea (triple comillas) para mostrar toda la tabla
- Dentro del f-string, realiza las multiplicaciones directamente

## Consejo
Puedes usar `print(f\"\"\"...múltiples líneas...\"\"\")` para imprimir varias líneas a la vez.
""",
        "starter_code": "# Escribe tu código aquí\n",
        "solution_code": """numero_a_multiplicar = int(input("Por favor, ingrese un número entero: "))
print(f\"\"\"
{numero_a_multiplicar} x 0 = {numero_a_multiplicar * 0}
{numero_a_multiplicar} x 1 = {numero_a_multiplicar * 1}
{numero_a_multiplicar} x 2 = {numero_a_multiplicar * 2}
{numero_a_multiplicar} x 3 = {numero_a_multiplicar * 3}
{numero_a_multiplicar} x 4 = {numero_a_multiplicar * 4}
{numero_a_multiplicar} x 5 = {numero_a_multiplicar * 5}
{numero_a_multiplicar} x 6 = {numero_a_multiplicar * 6}
{numero_a_multiplicar} x 7 = {numero_a_multiplicar * 7}
{numero_a_multiplicar} x 8 = {numero_a_multiplicar * 8}
{numero_a_multiplicar} x 9 = {numero_a_multiplicar * 9}
\"\"\")""",
        "tags": ["multiplicacion", "int", "format", "multiline"],
        "learning_objectives": ["Convertir a enteros", "Strings multilínea", "Operaciones dentro de f-strings"]
    },
    {
        "id": "SEC-07",
        "title": "Operaciones Aritméticas Básicas",
        "difficulty": "Easy",
        "time_min": 15,
        "max_score": 28,
        "mission_markdown": """# Ejercicio 7: Operaciones Aritméticas Básicas

## Objetivo
Crear un programa que pida al usuario dos números distintos de 0 y muestre por pantalla el resultado de sumarlos, restarlos, multiplicarlos y dividirlos.

## Instrucciones
- Solicita dos números (pueden ser decimales, usa `float()`)
- Realiza las 4 operaciones aritméticas básicas
- Muestra los resultados claramente

## Operadores en Python
- Suma: `+`
- Resta: `-`
- Multiplicación: `*`
- División: `/`

## Ejemplo
Si el usuario ingresa 10 y 5:
```
Resultado de la suma: 15.0
Resultado de la resta: 5.0
Resultado de la multiplicación: 50.0
Resultado de la división: 2.0
```

## Consejo
Usa `round()` en la división para evitar muchos decimales.
""",
        "starter_code": "# Escribe tu código aquí\n",
        "solution_code": """numero_a = float(input("Por favor, ingrese un número distinto de 0: "))
numero_b = float(input("Por favor, ingrese otro número distinto de 0: "))

suma_a_b = numero_a + numero_b
resta_a_b = numero_a - numero_b
multiplicacion_a_b = numero_a * numero_b
division_a_b = round(numero_a / numero_b, 2)

print(f\"\"\"
Resultado de la suma: {suma_a_b}
Resultado de la resta: {resta_a_b}
Resultado de la multiplicación: {multiplicacion_a_b}
Resultado de la división: {division_a_b}
\"\"\")""",
        "tags": ["aritmetica", "operadores", "matematica"],
        "learning_objectives": ["Operadores aritméticos", "Almacenar resultados en variables", "Formatear múltiples resultados"]
    },
    {
        "id": "SEC-08",
        "title": "Índice de Masa Corporal (IMC)",
        "difficulty": "Medium",
        "time_min": 15,
        "max_score": 24,
        "mission_markdown": """# Ejercicio 8: Índice de Masa Corporal (IMC)

## Objetivo
Crear un programa que pida al usuario su peso (en kilogramos) y su altura (en metros) e imprima por pantalla su Índice de Masa Corporal (IMC).

## Fórmula del IMC
- **IMC = peso / altura²**

## Clasificación del IMC
- Menor a 18.5: Bajo peso
- 18.5 a 24.9: Peso normal
- 25.0 a 29.9: Sobrepeso
- 30.0 o más: Obesidad

## Instrucciones
- Solicita peso en kilogramos
- Solicita altura en metros
- Calcula el IMC usando la fórmula
- Redondea a 2 decimales

## Ejemplo
Si el usuario ingresa peso=70kg y altura=1.75m:
```
Su IMC es de: 22.86.
```
""",
        "starter_code": "# Escribe tu código aquí\n",
        "solution_code": """peso = float(input("Por favor, ingrese su peso en kilogramos: "))
altura = float(input("Por favor, ingrese su altura en metros: "))
imc = round(peso / altura ** 2, 2)
print(f"Su IMC es de: {imc}.")""",
        "tags": ["calculos", "salud", "formula", "potencia"],
        "learning_objectives": ["Aplicar fórmulas matemáticas", "Elevar al cuadrado", "Trabajar con datos reales"]
    },
    {
        "id": "SEC-09",
        "title": "Conversión Celsius a Fahrenheit",
        "difficulty": "Easy",
        "time_min": 10,
        "max_score": 20,
        "mission_markdown": """# Ejercicio 9: Conversión de Temperatura (Celsius a Fahrenheit)

## Objetivo
Crear un programa que pida al usuario una temperatura en grados Celsius e imprima por pantalla su equivalente en grados Fahrenheit.

## Fórmula de conversión
- **°F = (9/5) * °C + 32**
- También puede escribirse como: **°F = 1.8 * °C + 32**

## Ejemplos de conversión
- 0°C = 32°F (punto de congelación del agua)
- 100°C = 212°F (punto de ebullición del agua)
- 37°C = 98.6°F (temperatura corporal promedio)

## Instrucciones
- Solicita temperatura en Celsius
- Aplica la fórmula de conversión
- Redondea a 2 decimales
- Muestra ambas temperaturas (original y convertida)
""",
        "starter_code": "# Escribe tu código aquí\n",
        "solution_code": """temperatura_celsius = float(input("Por favor, ingrese una temperatura en °C: "))
temperatura_fahrenheit = round((9/5) * temperatura_celsius + 32, 2)
print(f"{temperatura_celsius} °C equivalen a {temperatura_fahrenheit} °F.")""",
        "tags": ["conversiones", "temperatura", "formula"],
        "learning_objectives": ["Aplicar fórmulas de conversión", "Orden de operaciones", "Presentar resultados con unidades"]
    },
    {
        "id": "SEC-10",
        "title": "Promedio de Tres Números",
        "difficulty": "Easy",
        "time_min": 10,
        "max_score": 24,
        "mission_markdown": """# Ejercicio 10: Promedio de Tres Números

## Objetivo
Crear un programa que pida al usuario 3 números e imprima por pantalla el promedio (media aritmética) de dichos números.

## Fórmula del promedio
- **Promedio = (n1 + n2 + n3) / 3**

## Instrucciones
- Solicita 3 números al usuario (usa nombres descriptivos: primero, segundo, tercero)
- Suma los 3 números
- Divide la suma entre 3
- Redondea a 2 decimales

## Ejemplo
Si el usuario ingresa 10, 20 y 30:
```
El promedio de los números ingresados es 20.0.
```
""",
        "starter_code": "# Escribe tu código aquí\n",
        "solution_code": """numero_a = float(input("Por favor, ingrese el primer número: "))
numero_b = float(input("Por favor, ingrese el segundo número: "))
numero_c = float(input("Por favor, ingrese el tercer número: "))

suma_a_b_c = numero_a + numero_b + numero_c
promedio_a_b_c = round(suma_a_b_c / 3, 2)
print(f"El promedio de los números ingresados es {promedio_a_b_c}.")""",
        "tags": ["promedio", "media", "aritmetica"],
        "learning_objectives": ["Calcular promedios", "Dividir entre cantidad de valores", "Presentar estadísticas básicas"]
    }
]


# ============================================================================
# PISTAS POR EJERCICIO (4 pistas graduales con penalizaciones)
# ============================================================================

PISTAS_SECUENCIALES = {
    "SEC-01": [
        {
            "hint_number": 1,
            "title": "Función para mostrar texto",
            "content": "En Python existe una función incorporada que permite mostrar texto en pantalla. Su nombre en inglés significa 'imprimir'.",
            "penalty_points": 5
        },
        {
            "hint_number": 2,
            "title": "La función print()",
            "content": "La función para mostrar texto se llama print(). Todo lo que quieras mostrar debe ir dentro de los paréntesis.",
            "penalty_points": 10
        },
        {
            "hint_number": 3,
            "title": "Texto entre comillas",
            "content": "Los textos (cadenas de caracteres) en Python deben ir entre comillas, pueden ser comillas dobles \" \" o simples ' '.",
            "penalty_points": 15
        },
        {
            "hint_number": 4,
            "title": "Estructura completa",
            "content": "La estructura básica es: print(\"texto que quieres mostrar\"). Recuerda incluir el signo de exclamación en el mensaje.",
            "penalty_points": 20
        }
    ],
    "SEC-02": [
        {
            "hint_number": 1,
            "title": "Función para capturar entrada",
            "content": "Para pedirle datos al usuario necesitas una función que 'capture' lo que escribe. En Python esta función se llama input().",
            "penalty_points": 5
        },
        {
            "hint_number": 2,
            "title": "Guardar en variable",
            "content": "Lo que el usuario escriba debe guardarse en algún lugar para usarlo después. Usa una variable: nombre_variable = input(\"mensaje para el usuario\")",
            "penalty_points": 10
        },
        {
            "hint_number": 3,
            "title": "Combinar texto con variables",
            "content": "Para combinar texto fijo con el valor de una variable, puedes usar f-strings. Un f-string se escribe así: f\"texto {variable} más texto\"",
            "penalty_points": 15
        },
        {
            "hint_number": 4,
            "title": "Solución paso a paso",
            "content": "Primero guarda el nombre: nombre = input(\"...\"). Luego imprime el saludo: print(f\"Hola {nombre}!\")",
            "penalty_points": 20
        }
    ],
    "SEC-03": [
        {
            "hint_number": 1,
            "title": "Múltiples inputs",
            "content": "Necesitarás usar input() cuatro veces, una para cada dato que pides. Cada dato debe guardarse en una variable diferente.",
            "penalty_points": 5
        },
        {
            "hint_number": 2,
            "title": "Nombres descriptivos",
            "content": "Usa nombres de variables descriptivos que indiquen qué contienen: nombre, apellido, edad, lugar_de_residencia (o similar).",
            "penalty_points": 10
        },
        {
            "hint_number": 3,
            "title": "Múltiples variables en f-string",
            "content": "Puedes incluir múltiples variables dentro de un mismo f-string. Ejemplo: f\"Me llamo {var1} y tengo {var2}\"",
            "penalty_points": 15
        },
        {
            "hint_number": 4,
            "title": "Estructura del código",
            "content": "Estructura tu código así: 1) Cuatro líneas de input() guardando en variables, 2) Un print() con f-string que incluya las 4 variables en la oración",
            "penalty_points": 20
        }
    ],
    "SEC-04": [
        {
            "hint_number": 1,
            "title": "Importar math para pi",
            "content": "El valor de π (pi) está disponible en la librería math. Primero debes importarla: import math. Luego usas: math.pi",
            "penalty_points": 5
        },
        {
            "hint_number": 2,
            "title": "Convertir a float",
            "content": "El input() siempre devuelve texto (string). Para hacer cálculos matemáticos debes convertirlo a número decimal: float(input(\"...\"))",
            "penalty_points": 10
        },
        {
            "hint_number": 3,
            "title": "Elevar al cuadrado",
            "content": "Para elevar al cuadrado (r²) en Python usas el operador **. Ejemplo: radio ** 2 significa radio elevado al cuadrado",
            "penalty_points": 15
        },
        {
            "hint_number": 4,
            "title": "Redondear resultados",
            "content": "Usa round(resultado, 2) para redondear a 2 decimales. Estructura: área = round(math.pi * radio ** 2, 2). Luego calcula el perímetro de forma similar con su fórmula.",
            "penalty_points": 20
        }
    ],
    "SEC-05": [
        {
            "hint_number": 1,
            "title": "Factor de conversión",
            "content": "Si 1 hora tiene 3600 segundos, para convertir segundos a horas debes dividir la cantidad de segundos entre 3600.",
            "penalty_points": 5
        },
        {
            "hint_number": 2,
            "title": "Convertir a número",
            "content": "Recuerda convertir el input a número para poder hacer la división: segundos = float(input(\"...\"))",
            "penalty_points": 10
        },
        {
            "hint_number": 3,
            "title": "Operación de división",
            "content": "La operación de división en Python se hace con /. Ejemplo: horas = segundos / 3600",
            "penalty_points": 15
        },
        {
            "hint_number": 4,
            "title": "Redondear y mostrar",
            "content": "Usa round() para redondear el resultado a 2 decimales. En el mensaje final muestra tanto los segundos ingresados como las horas calculadas.",
            "penalty_points": 20
        }
    ],
    "SEC-06": [
        {
            "hint_number": 1,
            "title": "Convertir a entero",
            "content": "Para este ejercicio necesitas un número entero, no decimal. Usa int() en lugar de float(): numero = int(input(\"...\"))",
            "penalty_points": 5
        },
        {
            "hint_number": 2,
            "title": "String multilínea",
            "content": "Puedes usar un string multilínea con triple comillas para mostrar varias líneas a la vez. Se escribe: print(f\"\"\"línea1\\nlínea2\\nlínea3\"\"\")",
            "penalty_points": 10
        },
        {
            "hint_number": 3,
            "title": "Operaciones en f-string",
            "content": "Dentro del f-string puedes hacer operaciones matemáticas directamente: {numero * 0}, {numero * 1}, {numero * 2}, etc.",
            "penalty_points": 15
        },
        {
            "hint_number": 4,
            "title": "Formato de las líneas",
            "content": "Necesitas 10 líneas (del 0 al 9). Cada línea tiene el formato: {numero} x {multiplicador} = {numero * multiplicador}. Donde multiplicador va de 0 a 9.",
            "penalty_points": 20
        }
    ],
    "SEC-07": [
        {
            "hint_number": 1,
            "title": "Dos inputs",
            "content": "Necesitas pedir dos números al usuario, cada uno en su propia variable. Usa float() porque los números pueden ser decimales.",
            "penalty_points": 5
        },
        {
            "hint_number": 2,
            "title": "Operadores aritméticos",
            "content": "Los operadores aritméticos en Python son: Suma: +, Resta: -, Multiplicación: *, División: /",
            "penalty_points": 10
        },
        {
            "hint_number": 3,
            "title": "Guardar resultados",
            "content": "Puedes guardar cada resultado en una variable antes de imprimirlo: suma = numero_a + numero_b, resta = numero_a - numero_b (y así con las demás operaciones)",
            "penalty_points": 15
        },
        {
            "hint_number": 4,
            "title": "Mostrar resultados",
            "content": "Usa round() en la división para evitar muchos decimales. Muestra los 4 resultados, puedes usar un string multilínea o 4 print() separados.",
            "penalty_points": 20
        }
    ],
    "SEC-08": [
        {
            "hint_number": 1,
            "title": "Dos inputs necesarios",
            "content": "Necesitas pedir dos datos: peso y altura. Ambos deben convertirse a float para hacer cálculos.",
            "penalty_points": 5
        },
        {
            "hint_number": 2,
            "title": "Mensajes claros",
            "content": "En los mensajes de input() es buena práctica indicar las unidades: \"Ingrese su peso en kilogramos: \" y \"Ingrese su altura en metros: \"",
            "penalty_points": 10
        },
        {
            "hint_number": 3,
            "title": "Fórmula del IMC",
            "content": "Para elevar la altura al cuadrado usa: altura ** 2. La fórmula completa es: imc = peso / (altura ** 2)",
            "penalty_points": 15
        },
        {
            "hint_number": 4,
            "title": "Redondear resultado",
            "content": "Redondea el IMC a 2 decimales con round(). El resultado típico está entre 15 y 40 aproximadamente.",
            "penalty_points": 20
        }
    ],
    "SEC-09": [
        {
            "hint_number": 1,
            "title": "Solicitar temperatura",
            "content": "Pide la temperatura en Celsius y conviértela a float para poder calcular: temperatura_celsius = float(input(\"...\"))",
            "penalty_points": 5
        },
        {
            "hint_number": 2,
            "title": "Dos partes de la fórmula",
            "content": "La fórmula tiene dos partes: primero multiplicas por (9/5) o por 1.8, luego sumas 32 al resultado.",
            "penalty_points": 10
        },
        {
            "hint_number": 3,
            "title": "Escribir la fórmula",
            "content": "En Python la fórmula se escribe: (9/5) * celsius + 32. También puedes escribirla como: 1.8 * celsius + 32",
            "penalty_points": 15
        },
        {
            "hint_number": 4,
            "title": "Guardar y mostrar",
            "content": "Guarda el resultado en una variable, redondea a 2 decimales, y muestra ambas temperaturas: la original en °C y la convertida en °F.",
            "penalty_points": 20
        }
    ],
    "SEC-10": [
        {
            "hint_number": 1,
            "title": "Tres inputs",
            "content": "Necesitas pedir 3 números al usuario, cada uno guardado en su variable. Usa float() para permitir números decimales.",
            "penalty_points": 5
        },
        {
            "hint_number": 2,
            "title": "Cálculo del promedio",
            "content": "El promedio se calcula sumando todos los valores y dividiendo entre la cantidad de valores. En este caso: suma / 3",
            "penalty_points": 10
        },
        {
            "hint_number": 3,
            "title": "Sumar primero",
            "content": "Puedes calcular la suma primero: suma = num1 + num2 + num3. Y luego el promedio: promedio = suma / 3",
            "penalty_points": 15
        },
        {
            "hint_number": 4,
            "title": "Redondear y mostrar",
            "content": "Redondea el promedio a 2 decimales con round(). Muestra el resultado con un mensaje claro que indique qué representa el número.",
            "penalty_points": 20
        }
    ]
}


# ============================================================================
# TESTS AUTOMÁTICOS POR EJERCICIO
# ============================================================================

TESTS_SECUENCIALES = {
    "SEC-01": [
        {
            "test_number": 1,
            "description": "Verifica que imprime 'Hola Mundo!' exactamente",
            "input": "",
            "expected": "Hola Mundo!",
            "is_hidden": False,
            "timeout_seconds": 5
        }
    ],
    "SEC-02": [
        {
            "test_number": 1,
            "description": "Verifica saludo con nombre 'Marcos'",
            "input": "Marcos\n",
            "expected": ".*Hola Marcos.*",
            "is_hidden": False,
            "timeout_seconds": 5
        },
        {
            "test_number": 2,
            "description": "Verifica saludo con nombre 'Ana'",
            "input": "Ana\n",
            "expected": ".*Hola Ana.*",
            "is_hidden": True,
            "timeout_seconds": 5
        },
        {
            "test_number": 3,
            "description": "Verifica saludo con nombre 'Pedro'",
            "input": "Pedro\n",
            "expected": ".*Hola Pedro.*",
            "is_hidden": True,
            "timeout_seconds": 5
        }
    ],
    "SEC-03": [
        {
            "test_number": 1,
            "description": "Verifica oración con datos completos",
            "input": "Juan\nPerez\n25\nArgentina\n",
            "expected": ".*Soy Juan Perez.*25.*Argentina.*",
            "is_hidden": False,
            "timeout_seconds": 5
        },
        {
            "test_number": 2,
            "description": "Verifica oración con otros datos",
            "input": "Maria\nGomez\n30\nEspaña\n",
            "expected": ".*Soy Maria Gomez.*30.*España.*",
            "is_hidden": True,
            "timeout_seconds": 5
        }
    ],
    "SEC-04": [
        {
            "test_number": 1,
            "description": "Verifica área y perímetro con radio 5",
            "input": "5\n",
            "expected": ".*78\\.5.*31\\.4.*",
            "is_hidden": False,
            "timeout_seconds": 5
        },
        {
            "test_number": 2,
            "description": "Verifica área y perímetro con radio 10",
            "input": "10\n",
            "expected": ".*314\\..*62\\.8.*",
            "is_hidden": True,
            "timeout_seconds": 5
        },
        {
            "test_number": 3,
            "description": "Verifica área y perímetro con radio 2.5",
            "input": "2.5\n",
            "expected": ".*19\\.6.*15\\.7.*",
            "is_hidden": True,
            "timeout_seconds": 5
        }
    ],
    "SEC-05": [
        {
            "test_number": 1,
            "description": "Verifica conversión de 3600 segundos",
            "input": "3600\n",
            "expected": ".*1\\.0.*hora.*",
            "is_hidden": False,
            "timeout_seconds": 5
        },
        {
            "test_number": 2,
            "description": "Verifica conversión de 7200 segundos",
            "input": "7200\n",
            "expected": ".*2\\.0.*hora.*",
            "is_hidden": True,
            "timeout_seconds": 5
        },
        {
            "test_number": 3,
            "description": "Verifica conversión de 1800 segundos",
            "input": "1800\n",
            "expected": ".*0\\.5.*hora.*",
            "is_hidden": True,
            "timeout_seconds": 5
        }
    ],
    "SEC-06": [
        {
            "test_number": 1,
            "description": "Verifica tabla del 5 completa",
            "input": "5\n",
            "expected": ".*5 x 0 = 0.*5 x 1 = 5.*5 x 9 = 45.*",
            "is_hidden": False,
            "timeout_seconds": 5
        },
        {
            "test_number": 2,
            "description": "Verifica tabla del 3",
            "input": "3\n",
            "expected": ".*3 x 0 = 0.*3 x 5 = 15.*3 x 9 = 27.*",
            "is_hidden": True,
            "timeout_seconds": 5
        }
    ],
    "SEC-07": [
        {
            "test_number": 1,
            "description": "Verifica operaciones con 10 y 5",
            "input": "10\n5\n",
            "expected": ".*15.*5.*50.*2.*",
            "is_hidden": False,
            "timeout_seconds": 5
        },
        {
            "test_number": 2,
            "description": "Verifica operaciones con 20 y 4",
            "input": "20\n4\n",
            "expected": ".*24.*16.*80.*5.*",
            "is_hidden": True,
            "timeout_seconds": 5
        }
    ],
    "SEC-08": [
        {
            "test_number": 1,
            "description": "Verifica IMC con peso 70kg y altura 1.75m",
            "input": "70\n1.75\n",
            "expected": ".*22\\.8.*",
            "is_hidden": False,
            "timeout_seconds": 5
        },
        {
            "test_number": 2,
            "description": "Verifica IMC con peso 80kg y altura 1.80m",
            "input": "80\n1.80\n",
            "expected": ".*24\\.6.*",
            "is_hidden": True,
            "timeout_seconds": 5
        }
    ],
    "SEC-09": [
        {
            "test_number": 1,
            "description": "Verifica conversión de 0°C a 32°F",
            "input": "0\n",
            "expected": ".*32.*",
            "is_hidden": False,
            "timeout_seconds": 5
        },
        {
            "test_number": 2,
            "description": "Verifica conversión de 100°C a 212°F",
            "input": "100\n",
            "expected": ".*212.*",
            "is_hidden": True,
            "timeout_seconds": 5
        },
        {
            "test_number": 3,
            "description": "Verifica conversión de 37°C a 98.6°F",
            "input": "37\n",
            "expected": ".*98\\.6.*",
            "is_hidden": True,
            "timeout_seconds": 5
        }
    ],
    "SEC-10": [
        {
            "test_number": 1,
            "description": "Verifica promedio de 10, 20, 30",
            "input": "10\n20\n30\n",
            "expected": ".*20.*",
            "is_hidden": False,
            "timeout_seconds": 5
        },
        {
            "test_number": 2,
            "description": "Verifica promedio de 5, 10, 15",
            "input": "5\n10\n15\n",
            "expected": ".*10.*",
            "is_hidden": True,
            "timeout_seconds": 5
        }
    ]
}


# ============================================================================
# SEEDER CLASS
# ============================================================================

class SecuencialesSeeder:
    """Seeds Secuenciales exercises into database"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.db_config = get_db_config()
        self.engine = self.db_config.get_engine()
        self.Session = self.db_config.get_session_factory()

        # Statistics
        self.stats = {
            "subjects": 0,
            "exercises": 0,
            "hints": 0,
            "tests": 0
        }

    def run(self):
        """Main seeding process"""
        logger.info("=" * 70)
        logger.info("EJERCICIOS SECUENCIALES - SEED")
        logger.info("=" * 70)

        if self.dry_run:
            logger.warning("🔸 DRY RUN MODE - No se guardarán cambios")

        session = self.Session()

        try:
            # Step 1: Ensure PROG1 subject exists
            logger.info("\n[1/4] Verificando subject PROG1...")
            self.ensure_subject_exists(session)

            # Step 2: Create exercises
            logger.info("\n[2/4] Creando 10 ejercicios secuenciales...")
            self.create_exercises(session)

            # Step 3: Create hints
            logger.info("\n[3/4] Creando 40 pistas (4 por ejercicio)...")
            self.create_hints(session)

            # Step 4: Create tests
            logger.info("\n[4/4] Creando tests automáticos...")
            self.create_tests(session)

            # Commit if not dry run
            if not self.dry_run:
                session.commit()
                logger.info("\n✅ SEED COMPLETADO - Cambios guardados en la base de datos")
            else:
                session.rollback()
                logger.info("\n🔸 DRY RUN COMPLETADO - No se guardaron cambios")

            # Print statistics
            self.print_statistics()

        except Exception as e:
            session.rollback()
            logger.error(f"\n❌ ERROR durante el seed: {e}", exc_info=True)
            raise
        finally:
            session.close()

    def ensure_subject_exists(self, session):
        """Ensure PROG1 subject exists"""
        subject = session.query(SubjectDB).filter(SubjectDB.code == "PROG1").first()

        if not subject:
            subject = SubjectDB(
                code="PROG1",
                name="Programación 1",
                language="python",
                total_units=7,
                is_active=True
            )
            session.add(subject)
            logger.info("✓ Subject PROG1 creado")
            self.stats["subjects"] += 1
        else:
            logger.info("✓ Subject PROG1 ya existe")

    def create_exercises(self, session):
        """Create exercises from EJERCICIOS_SECUENCIALES"""
        for exercise_data in EJERCICIOS_SECUENCIALES:
            # Check if exercise already exists
            existing = session.query(ExerciseDB).filter(ExerciseDB.id == exercise_data["id"]).first()
            if existing:
                logger.info(f"  ⏭ {exercise_data['id']} ya existe - SKIP")
                continue

            # Create exercise
            exercise = ExerciseDB(
                id=exercise_data["id"],
                subject_code="PROG1",
                title=exercise_data["title"],
                description=exercise_data["mission_markdown"][:200],  # Short description
                difficulty=exercise_data["difficulty"],
                time_min=exercise_data["time_min"],
                unit=1,  # Secuenciales = Unit 1
                language="python",
                mission_markdown=exercise_data["mission_markdown"],
                story_markdown=None,  # No story for now
                constraints=[],
                starter_code=exercise_data["starter_code"],
                solution_code=exercise_data["solution_code"],
                tags=exercise_data["tags"],
                learning_objectives=exercise_data["learning_objectives"],
                max_score=exercise_data["max_score"],
                version=1,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            session.add(exercise)
            logger.info(f"  ✓ {exercise.id}: {exercise.title} ({exercise.max_score} pts)")
            self.stats["exercises"] += 1

    def create_hints(self, session):
        """Create hints from PISTAS_SECUENCIALES"""
        for exercise_id, hints in PISTAS_SECUENCIALES.items():
            for hint_data in hints:
                # Check if hint already exists
                existing = session.query(ExerciseHintDB).filter(
                    ExerciseHintDB.exercise_id == exercise_id,
                    ExerciseHintDB.hint_number == hint_data["hint_number"]
                ).first()

                if existing:
                    continue

                # Create hint
                hint = ExerciseHintDB(
                    id=str(uuid.uuid4()),
                    exercise_id=exercise_id,
                    hint_number=hint_data["hint_number"],
                    title=hint_data["title"],
                    content=hint_data["content"],
                    penalty_points=hint_data["penalty_points"]
                )

                session.add(hint)
                self.stats["hints"] += 1

        logger.info(f"  ✓ {self.stats['hints']} pistas creadas")

    def create_tests(self, session):
        """Create tests from TESTS_SECUENCIALES"""
        for exercise_id, tests in TESTS_SECUENCIALES.items():
            for test_data in tests:
                # Check if test already exists
                existing = session.query(ExerciseTestDB).filter(
                    ExerciseTestDB.exercise_id == exercise_id,
                    ExerciseTestDB.test_number == test_data["test_number"]
                ).first()

                if existing:
                    continue

                # Create test
                test = ExerciseTestDB(
                    id=str(uuid.uuid4()),
                    exercise_id=exercise_id,
                    test_number=test_data["test_number"],
                    description=test_data["description"],
                    input=test_data["input"],
                    expected=test_data["expected"],
                    is_hidden=test_data["is_hidden"],
                    timeout_seconds=test_data["timeout_seconds"]
                )

                session.add(test)
                self.stats["tests"] += 1

        logger.info(f"  ✓ {self.stats['tests']} tests creados")

    def print_statistics(self):
        """Print seeding statistics"""
        logger.info("\n" + "=" * 70)
        logger.info("ESTADÍSTICAS DEL SEED")
        logger.info("=" * 70)
        logger.info(f"Subjects verificados:  {self.stats['subjects']}")
        logger.info(f"Ejercicios creados:    {self.stats['exercises']}")
        logger.info(f"Pistas creadas:        {self.stats['hints']}")
        logger.info(f"Tests creados:         {self.stats['tests']}")
        logger.info("=" * 70)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed Ejercicios Secuenciales")
    parser.add_argument("--dry-run", action="store_true", help="Preview sin guardar cambios")
    args = parser.parse_args()

    seeder = SecuencialesSeeder(dry_run=args.dry_run)
    seeder.run()

