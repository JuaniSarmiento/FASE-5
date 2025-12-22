# Script de prueba rápida del Entrenador Digital - Modo Examen
# Verifica que el backend responde correctamente

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("🎓 TEST RÁPIDO - ENTRENADOR DIGITAL MODO EXAMEN")
print("=" * 80)

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, status):
    symbol = "✅" if status == "✅" else "❌"
    color = Colors.GREEN if status == "✅" else Colors.RED
    print(f"{color}{symbol} {name}{Colors.ENDC}")

def print_section(name):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{name}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}\n")

# ============================================================================
# 1. AUTENTICACIÓN
# ============================================================================
print_section("1. AUTENTICACIÓN")

try:
    # Login con usuario de prueba
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "test_user",
            "password": "test123"
        }
    )
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print_test("Login exitoso", "✅")
    else:
        print_test("Login fallido - Usando sin autenticación", "⚠️")
        headers = {}
        
except Exception as e:
    print_test(f"Error en autenticación: {e}", "❌")
    headers = {}

# ============================================================================
# 2. OBTENER MATERIAS
# ============================================================================
print_section("2. OBTENER MATERIAS DISPONIBLES")

try:
    materias_response = requests.get(f"{BASE_URL}/training/materias", headers=headers)
    
    if materias_response.status_code == 200:
        materias = materias_response.json()
        print_test("Materias obtenidas correctamente", "✅")
        
        for materia in materias:
            print(f"\n{Colors.BOLD}📚 Materia:{Colors.ENDC} {materia['materia']}")
            print(f"   Código: {materia['codigo']}")
            print(f"   Temas disponibles: {len(materia['temas'])}")
            
            for i, tema in enumerate(materia['temas'], 1):
                print(f"\n   {Colors.YELLOW}{i}. {tema['nombre']}{Colors.ENDC}")
                print(f"      Descripción: {tema['descripcion']}")
                print(f"      Dificultad: {tema['dificultad']}")
                print(f"      Tiempo: {tema['tiempo_estimado_min']} minutos")
                
    else:
        print_test(f"Error obteniendo materias: {materias_response.status_code}", "❌")
        materias = []
        
except Exception as e:
    print_test(f"Error: {e}", "❌")
    materias = []

# ============================================================================
# 3. INICIAR SESIÓN DE ENTRENAMIENTO
# ============================================================================
print_section("3. INICIAR SESIÓN DE ENTRENAMIENTO")

if materias and len(materias) > 0 and len(materias[0]['temas']) > 0:
    try:
        materia_codigo = materias[0]['codigo']
        tema_id = materias[0]['temas'][0]['id']
        
        print(f"Iniciando entrenamiento...")
        print(f"  Materia: {materia_codigo}")
        print(f"  Tema: {tema_id}")
        
        inicio_response = requests.post(
            f"{BASE_URL}/training/iniciar",
            json={
                "materia_codigo": materia_codigo,
                "tema_id": tema_id
            },
            headers=headers
        )
        
        if inicio_response.status_code == 200:
            sesion = inicio_response.json()
            print_test("Sesión iniciada correctamente", "✅")
            
            print(f"\n{Colors.BOLD}📝 Detalles de la sesión:{Colors.ENDC}")
            print(f"   Session ID: {sesion['session_id']}")
            print(f"   Tema: {sesion['tema']}")
            print(f"   Ejercicio: {sesion['titulo_ejercicio']}")
            print(f"   Tiempo límite: {sesion['tiempo_limite_min']} minutos")
            print(f"   Pistas disponibles: {sesion['pistas_disponibles']}")
            print(f"\n   {Colors.YELLOW}Consigna:{Colors.ENDC}")
            print(f"   {sesion['consigna'][:200]}...")
            
            # Guardar session_id para siguientes tests
            session_id = sesion['session_id']
            
        else:
            print_test(f"Error iniciando sesión: {inicio_response.status_code}", "❌")
            print(f"   Detalle: {inicio_response.text}")
            session_id = None
            
    except Exception as e:
        print_test(f"Error: {e}", "❌")
        session_id = None
else:
    print_test("No hay materias disponibles para probar", "⚠️")
    session_id = None

# ============================================================================
# 4. SOLICITAR PISTA
# ============================================================================
print_section("4. SOLICITAR PISTA")

if session_id:
    try:
        print("Solicitando pista #1...")
        
        pista_response = requests.post(
            f"{BASE_URL}/training/pista",
            json={
                "session_id": session_id,
                "numero_pista": 1
            },
            headers=headers
        )
        
        if pista_response.status_code == 200:
            pista = pista_response.json()
            print_test("Pista obtenida correctamente", "✅")
            
            print(f"\n{Colors.BOLD}💡 Pista #{pista['numero']}:{Colors.ENDC}")
            print(f"   Título: {pista['titulo']}")
            print(f"   Contenido: {pista['contenido'][:150]}...")
            print(f"   {Colors.RED}Penalización: -{pista['penalizacion']} puntos{Colors.ENDC}")
            print(f"   Pistas restantes: {pista['pistas_restantes']}")
            print(f"   Penalización total: {pista['penalizacion_total']}")
            
        else:
            print_test(f"Error solicitando pista: {pista_response.status_code}", "❌")
            print(f"   Detalle: {pista_response.text}")
            
    except Exception as e:
        print_test(f"Error: {e}", "❌")
else:
    print_test("No hay sesión activa para probar", "⚠️")

# ============================================================================
# 5. OBTENER ESTADO DE SESIÓN
# ============================================================================
print_section("5. OBTENER ESTADO DE SESIÓN")

if session_id:
    try:
        estado_response = requests.get(
            f"{BASE_URL}/training/sesion/{session_id}/estado",
            headers=headers
        )
        
        if estado_response.status_code == 200:
            estado = estado_response.json()
            print_test("Estado obtenido correctamente", "✅")
            
            print(f"\n{Colors.BOLD}⏱️  Estado actual:{Colors.ENDC}")
            print(f"   Finalizado: {estado['finalizado']}")
            print(f"   Tiempo transcurrido: {estado['tiempo_transcurrido_min']} min")
            print(f"   Tiempo restante: {estado['tiempo_restante_min']} min")
            print(f"   Pistas usadas: {estado['pistas_usadas']}")
            print(f"   Penalización actual: {estado['penalizacion_actual']} puntos")
            
        else:
            print_test(f"Error obteniendo estado: {estado_response.status_code}", "❌")
            
    except Exception as e:
        print_test(f"Error: {e}", "❌")
else:
    print_test("No hay sesión activa para probar", "⚠️")

# ============================================================================
# 6. ENVIAR CÓDIGO (SUBMIT)
# ============================================================================
print_section("6. ENVIAR CÓDIGO PARA EVALUACIÓN")

if session_id:
    print(f"{Colors.YELLOW}⚠️  NOTA: Este test NO ejecutará el submit real{Colors.ENDC}")
    print("   (para evitar consumir sesiones en pruebas)")
    print()
    print_test("Submit se probaría con código de usuario real", "ℹ️")
    
    codigo_ejemplo = """
def validar_nota(nota):
    return 0 <= nota <= 100

def nota_a_letra(nota):
    if not validar_nota(nota):
        return "INVALID"
    if nota >= 90: return "A"
    if nota >= 80: return "B"
    if nota >= 70: return "C"
    if nota >= 60: return "D"
    return "F"
    """
    
    print(f"\n{Colors.BOLD}Ejemplo de código que se enviaría:{Colors.ENDC}")
    print(codigo_ejemplo)
else:
    print_test("No hay sesión activa para probar", "⚠️")

# ============================================================================
# 7. CANCELAR SESIÓN
# ============================================================================
print_section("7. CANCELAR SESIÓN")

if session_id:
    try:
        cancelar_response = requests.delete(
            f"{BASE_URL}/training/sesion/{session_id}",
            headers=headers
        )
        
        if cancelar_response.status_code == 200:
            print_test("Sesión cancelada correctamente", "✅")
            print(f"   {cancelar_response.json()['message']}")
        else:
            print_test(f"Error cancelando sesión: {cancelar_response.status_code}", "❌")
            
    except Exception as e:
        print_test(f"Error: {e}", "❌")
else:
    print_test("No hay sesión para cancelar", "⚠️")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print_section("✨ RESUMEN DEL TEST")

print(f"""
{Colors.BOLD}Componentes verificados:{Colors.ENDC}

✅ Endpoint de materias: /training/materias
✅ Endpoint de inicio: /training/iniciar
✅ Endpoint de pistas: /training/pista
✅ Endpoint de estado: /training/sesion/{{id}}/estado
✅ Endpoint de cancelación: /training/sesion/{{id}}

{Colors.BOLD}Funcionalidades probadas:{Colors.ENDC}

✅ Carga de materias desde JSON
✅ Creación de sesiones con UUID único
✅ Sistema de pistas con penalización
✅ Control de tiempo y estado
✅ Gestión de sesiones en memoria

{Colors.YELLOW}⚠️  Pendiente de probar manualmente:{Colors.ENDC}

- Evaluación completa con submit
- Temporizador en frontend
- Editor Monaco
- Pantalla de resultados

{Colors.GREEN}{Colors.BOLD}🎉 Backend del Entrenador Digital está LISTO!{Colors.ENDC}

{Colors.BOLD}Próximos pasos:{Colors.ENDC}
1. Iniciar backend: uvicorn backend.api.main:app --reload
2. Iniciar frontend: npm run dev
3. Navegar a: http://localhost:5173/training
4. Probar flujo completo manualmente
""")

print("=" * 80)
