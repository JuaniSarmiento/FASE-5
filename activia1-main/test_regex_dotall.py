"""
Test para verificar que re.DOTALL funciona correctamente
"""
import re

# Simular el output del ejercicio de tabla de multiplicar
output_con_saltos = """Ingrese un número entero: 
5 x 0 = 0
5 x 1 = 5
5 x 2 = 10
5 x 3 = 15
5 x 4 = 20
5 x 5 = 25
5 x 6 = 30
5 x 7 = 35
5 x 8 = 40
5 x 9 = 45
"""

# Pattern del test
pattern = ".*5 x 0 = 0.*5 x 1 = 5.*5 x 9 = 45.*"

print("="*70)
print("TEST DE RE.DOTALL")
print("="*70)

print("\nOutput:")
print(repr(output_con_saltos))

print(f"\nPattern: {pattern}")

print("\n" + "-"*70)
print("SIN re.DOTALL:")
resultado_sin = re.search(pattern, output_con_saltos)
if resultado_sin:
    print("  ✅ Match exitoso")
else:
    print("  ❌ No coincide (porque . no coincide con \\n)")

print("\nCON re.DOTALL:")
resultado_con = re.search(pattern, output_con_saltos, re.DOTALL)
if resultado_con:
    print("  ✅ Match exitoso")
else:
    print("  ❌ No coincide")

print("-"*70)

print("\n" + "="*70)
print("EXPLICACIÓN")
print("="*70)
print("""
El flag re.DOTALL hace que el metacarácter . (punto) coincida con
CUALQUIER carácter, incluyendo saltos de línea (\\n).

Sin re.DOTALL:
  . coincide con cualquier carácter EXCEPTO \\n
  Por eso .* no puede atravesar múltiples líneas

Con re.DOTALL:
  . coincide con cualquier carácter INCLUYENDO \\n
  Por eso .* puede atravesar múltiples líneas

Para ejercicios que generan output multilínea, SIEMPRE usar re.DOTALL
""")
print("="*70)
