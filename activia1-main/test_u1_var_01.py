"""
Test para verificar que el ejercicio U1-VAR-01 funciona correctamente
"""

print("="*80)
print("TEST: Ejercicio U1-VAR-01 - Variables y Tipos de Datos")
print("="*80)

# Según el enunciado:
# - Enero: $12,500
# - Febrero: $15,300
# - Marzo: $14,800

print("\n📋 Valores esperados según el enunciado:")
print("   Enero: $12,500")
print("   Febrero: $15,300")
print("   Marzo: $14,800")
print("   Total esperado: $42,600")
print("   Promedio esperado: $14,200.00")

print("\n" + "-"*80)
print("Probando tu código:")
print("-"*80)

# TU CÓDIGO ACTUAL (con valores incorrectos)
ventas_enero = 200
ventas_febrero = 300
ventas_marzo = 500

total = ventas_enero + ventas_febrero + ventas_marzo
promedio = total / 3

print(f"\n❌ CON TUS VALORES:")
print(f"   ventas_enero = {ventas_enero}")
print(f"   ventas_febrero = {ventas_febrero}")
print(f"   ventas_marzo = {ventas_marzo}")
print(f"   total = {total}")
print(f"   promedio = {promedio:.2f}")
print(f"\n   Test: total == 42600 and promedio == 14200.00")
print(f"   Resultado: {total == 42600 and promedio == 14200.00} ❌")

print("\n" + "-"*80)

# CÓDIGO CORRECTO (con valores del enunciado)
ventas_enero = 12500
ventas_febrero = 15300
ventas_marzo = 14800

total = ventas_enero + ventas_febrero + ventas_marzo
promedio = total / 3

print(f"\n✅ CON LOS VALORES CORRECTOS DEL ENUNCIADO:")
print(f"   ventas_enero = {ventas_enero}")
print(f"   ventas_febrero = {ventas_febrero}")
print(f"   ventas_marzo = {ventas_marzo}")
print(f"   total = {total}")
print(f"   promedio = {promedio:.2f}")
print(f"\n   Test: total == 42600 and promedio == 14200.00")
print(f"   Resultado: {total == 42600 and promedio == 14200.00} ✅")

print("\n" + "="*80)
print("📝 SOLUCIÓN CORRECTA:")
print("="*80)
print("""
# NO TOCAR ESTAS LÍNEAS
# Ejercicio: Variables y Tipos de Datos

# TODO: Declara las variables de ventas mensuales
ventas_enero = 12500     # $12,500
ventas_febrero = 15300   # $15,300
ventas_marzo = 14800     # $14,800

# TODO: Calcula el total y el promedio
total = ventas_enero + ventas_febrero + ventas_marzo
promedio = total / 3

# TODO: Imprime los resultados
print(f"Total trimestre: ${total}")
print(f"Promedio mensual: ${promedio:.2f}")
""")
print("="*80)
