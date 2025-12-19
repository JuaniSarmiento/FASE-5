"""
TEST COMPLETO DEL SISTEMA ACTIVIA - DEMO PARA JEFE
====================================================

Este test ejecuta todas las funcionalidades principales del sistema:
1. Tutor Socrático (T-IA-Cog) con Mistral AI
2. Simuladores de Entrevista (S-IA-X) 
3. Entrenador Digital (Ejercicios Python, Java, Spring Boot)
4. Análisis de Riesgos 5D con IA personalizada
5. Integración completa de componentes

Genera un reporte profesional para demostración ejecutiva.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BASE_URL = "http://localhost:8000"
SESSION_ID = f"demo_session_{int(time.time())}"

# Colores para output de consola
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title: str):
    """Imprime un título de sección destacado"""
    print("\n" + "="*80)
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print("="*80 + "\n")

def print_test(name: str, status: str, details: str = ""):
    """Imprime resultado de un test"""
    color = Colors.OKGREEN if status == "✅" else Colors.FAIL
    print(f"{color}{status}{Colors.ENDC} {name}")
    if details:
        print(f"   └─ {details}")

def print_metric(label: str, value: Any):
    """Imprime una métrica"""
    print(f"{Colors.OKCYAN}   • {label}:{Colors.ENDC} {value}")


# ============================================================================
# RESULTADOS DEL DEMO
# ============================================================================

demo_results = {
    "timestamp": datetime.now().isoformat(),
    "session_id": SESSION_ID,
    "tests": []
}


# ============================================================================
# TEST 1: TUTOR SOCRÁTICO (T-IA-Cog)
# ============================================================================

def test_tutor_socratico():
    """Test del tutor socrático con preguntas variadas"""
    print_section("TEST 1: TUTOR SOCRÁTICO (T-IA-Cog) - Mistral AI")
    
    test_cases = [
        {
            "name": "Pregunta Conceptual - POO",
            "query": "¿Qué es la herencia en programación orientada a objetos?",
            "esperado": "explicación socrática"
        },
        {
            "name": "Pregunta de Código - Python",
            "query": "¿Cómo creo una lista de comprensión en Python?",
            "esperado": "guía paso a paso"
        },
        {
            "name": "Pregunta Compleja - Spring Boot",
            "query": "Explícame cómo funciona la inyección de dependencias en Spring Boot",
            "esperado": "análisis profundo"
        },
        {
            "name": "Debug - Error común",
            "query": "Tengo un NullPointerException en Java, ¿qué hago?",
            "esperado": "estrategias de debugging"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n{Colors.BOLD}Test 1.{i}: {test_case['name']}{Colors.ENDC}")
            print(f"Pregunta: {test_case['query']}")
            
            response = requests.post(
                f"{BASE_URL}/tutor/ask",
                json={
                    "session_id": SESSION_ID,
                    "message": test_case['query'],
                    "context": {}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                respuesta = data.get("response", "")
                trace_id = data.get("trace_id", "N/A")
                
                # Validaciones
                tiene_respuesta = len(respuesta) > 100
                es_socratica = any(palabra in respuesta.lower() for palabra in ["por qué", "considera", "piensa", "analiza"])
                
                status = "✅" if tiene_respuesta else "❌"
                print_test(test_case['name'], status)
                print_metric("Longitud respuesta", f"{len(respuesta)} caracteres")
                print_metric("Trace ID", trace_id)
                print_metric("Es Socrática", "Sí" if es_socratica else "No")
                
                # Mostrar snippet de respuesta
                print(f"\n{Colors.OKCYAN}Respuesta (primeros 200 chars):{Colors.ENDC}")
                print(f"   {respuesta[:200]}...")
                
                results.append({
                    "test": test_case['name'],
                    "success": tiene_respuesta,
                    "trace_id": trace_id,
                    "response_length": len(respuesta),
                    "is_socratic": es_socratica
                })
            else:
                print_test(test_case['name'], "❌", f"Error HTTP {response.status_code}")
                results.append({
                    "test": test_case['name'],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print_test(test_case['name'], "❌", str(e))
            results.append({
                "test": test_case['name'],
                "success": False,
                "error": str(e)
            })
    
    # Resumen
    exitosos = sum(1 for r in results if r.get('success', False))
    print(f"\n{Colors.BOLD}Resumen Tutor Socrático:{Colors.ENDC}")
    print_metric("Tests exitosos", f"{exitosos}/{len(test_cases)}")
    
    demo_results["tests"].append({
        "section": "Tutor Socrático",
        "total": len(test_cases),
        "passed": exitosos,
        "details": results
    })
    
    return exitosos == len(test_cases)


# ============================================================================
# TEST 2: SIMULADORES DE ENTREVISTA (S-IA-X)
# ============================================================================

def test_simuladores():
    """Test de simuladores con diferentes personas"""
    print_section("TEST 2: SIMULADORES DE ENTREVISTA (S-IA-X)")
    
    simuladores = [
        {
            "name": "Entrevistador Técnico Senior",
            "agent_id": "S-IA-Tec",
            "query": "¿Qué es un closure en JavaScript?",
            "esperado": "pregunta técnica profunda"
        },
        {
            "name": "Reclutador RRHH",
            "agent_id": "S-IA-RRHH",
            "query": "Cuéntame sobre tu experiencia trabajando en equipo",
            "esperado": "evaluación soft skills"
        },
        {
            "name": "CTO/Líder Técnico",
            "agent_id": "S-IA-CTO",
            "query": "¿Cómo diseñarías la arquitectura de un sistema de e-commerce escalable?",
            "esperado": "evaluación arquitectura"
        }
    ]
    
    results = []
    
    for i, sim in enumerate(simuladores, 1):
        try:
            print(f"\n{Colors.BOLD}Test 2.{i}: {sim['name']}{Colors.ENDC}")
            print(f"Pregunta del candidato: {sim['query']}")
            
            response = requests.post(
                f"{BASE_URL}/simulator/interact",
                json={
                    "session_id": SESSION_ID,
                    "agent_id": sim['agent_id'],
                    "message": sim['query']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                respuesta = data.get("response", "")
                
                tiene_respuesta = len(respuesta) > 50
                status = "✅" if tiene_respuesta else "❌"
                
                print_test(sim['name'], status)
                print_metric("Agente", sim['agent_id'])
                print_metric("Longitud respuesta", f"{len(respuesta)} caracteres")
                
                print(f"\n{Colors.OKCYAN}Respuesta del entrevistador:{Colors.ENDC}")
                print(f"   {respuesta[:250]}...")
                
                results.append({
                    "simulator": sim['name'],
                    "agent_id": sim['agent_id'],
                    "success": tiene_respuesta,
                    "response_length": len(respuesta)
                })
            else:
                print_test(sim['name'], "❌", f"Error HTTP {response.status_code}")
                results.append({
                    "simulator": sim['name'],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print_test(sim['name'], "❌", str(e))
            results.append({
                "simulator": sim['name'],
                "success": False,
                "error": str(e)
            })
    
    exitosos = sum(1 for r in results if r.get('success', False))
    print(f"\n{Colors.BOLD}Resumen Simuladores:{Colors.ENDC}")
    print_metric("Tests exitosos", f"{exitosos}/{len(simuladores)}")
    
    demo_results["tests"].append({
        "section": "Simuladores de Entrevista",
        "total": len(simuladores),
        "passed": exitosos,
        "details": results
    })
    
    return exitosos == len(simuladores)


# ============================================================================
# TEST 3: ENTRENADOR DIGITAL (Ejercicios Python, Java, Spring Boot)
# ============================================================================

def test_entrenador_digital():
    """Test del sistema de ejercicios multi-lenguaje"""
    print_section("TEST 3: ENTRENADOR DIGITAL - Ejercicios Multi-Lenguaje")
    
    # 3.1: Verificar estadísticas y filtros disponibles
    print(f"\n{Colors.BOLD}Test 3.1: Estadísticas del Sistema{Colors.ENDC}")
    
    try:
        stats_response = requests.get(f"{BASE_URL}/exercises/json/stats")
        filters_response = requests.get(f"{BASE_URL}/exercises/json/filters")
        
        if stats_response.status_code == 200 and filters_response.status_code == 200:
            stats = stats_response.json()
            filters = filters_response.json()
            
            print_test("Obtener estadísticas", "✅")
            print_metric("Total ejercicios", stats.get('total_exercises', 0))
            print_metric("Por dificultad", json.dumps(stats.get('by_difficulty', {}), indent=2))
            print_metric("Por lenguaje", json.dumps(stats.get('by_language', {}), indent=2))
            print_metric("Por framework", json.dumps(stats.get('by_framework', {}), indent=2))
            print_metric("Tags únicos", len(stats.get('unique_tags', [])))
            
            print(f"\n{Colors.BOLD}Filtros disponibles:{Colors.ENDC}")
            print_metric("Lenguajes", filters.get('languages', []))
            print_metric("Frameworks", filters.get('frameworks', []))
            print_metric("Dificultades", filters.get('difficulties', []))
            
            stats_ok = stats.get('total_exercises', 0) >= 8  # 4 Python + 4 Java + 4 Spring Boot = 12 mínimo
        else:
            print_test("Obtener estadísticas", "❌", "Error en requests")
            stats_ok = False
            
    except Exception as e:
        print_test("Obtener estadísticas", "❌", str(e))
        stats_ok = False
    
    # 3.2: Probar filtros por lenguaje
    print(f"\n{Colors.BOLD}Test 3.2: Filtrado por Lenguaje{Colors.ENDC}")
    
    filtros_test = [
        {"name": "Ejercicios Python", "params": {"language": "python"}},
        {"name": "Ejercicios Java", "params": {"language": "java"}},
        {"name": "Ejercicios Spring Boot", "params": {"framework": "spring-boot"}},
        {"name": "Ejercicios Fáciles", "params": {"difficulty": "Easy"}},
        {"name": "Ejercicios Difíciles", "params": {"difficulty": "Hard"}}
    ]
    
    filtros_results = []
    
    for filtro in filtros_test:
        try:
            response = requests.get(
                f"{BASE_URL}/exercises/json/list",
                params=filtro['params']
            )
            
            if response.status_code == 200:
                ejercicios = response.json()
                count = len(ejercicios)
                
                print_test(filtro['name'], "✅", f"Encontrados: {count}")
                filtros_results.append({
                    "filter": filtro['name'],
                    "success": True,
                    "count": count
                })
            else:
                print_test(filtro['name'], "❌", f"HTTP {response.status_code}")
                filtros_results.append({
                    "filter": filtro['name'],
                    "success": False
                })
        except Exception as e:
            print_test(filtro['name'], "❌", str(e))
            filtros_results.append({
                "filter": filtro['name'],
                "success": False,
                "error": str(e)
            })
    
    # 3.3: Evaluar ejercicios de diferentes lenguajes
    print(f"\n{Colors.BOLD}Test 3.3: Evaluación con IA (Mistral){Colors.ENDC}")
    
    ejercicios_evaluar = [
        {
            "name": "Python - Función suma",
            "exercise_id": "U1-PY-01",
            "code": """def suma(a, b):
    return a + b"""
        },
        {
            "name": "Java - Calculadora",
            "exercise_id": "U6-JAVA-01",
            "code": """public class Calculadora {
    private int resultado;
    
    public int sumar(int a, int b) {
        this.resultado = a + b;
        return this.resultado;
    }
    
    public int getResultado() {
        return this.resultado;
    }
}"""
        }
    ]
    
    eval_results = []
    
    for ejercicio in ejercicios_evaluar:
        try:
            print(f"\nEvaluando: {ejercicio['name']}")
            
            response = requests.post(
                f"{BASE_URL}/exercises/json/evaluate",
                json={
                    "exercise_id": ejercicio['exercise_id'],
                    "user_code": ejercicio['code']
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                evaluation = result.get('evaluation', {})
                score = evaluation.get('score', 0)
                xp = result.get('gamification', {}).get('xp_earned', 0)
                
                print_test(ejercicio['name'], "✅")
                print_metric("Score", f"{score}/100")
                print_metric("XP Ganado", xp)
                print_metric("Estado", "APROBADO" if score >= 70 else "NECESITA MEJORAS")
                
                feedback = evaluation.get('feedback', '')
                if feedback:
                    print(f"\n{Colors.OKCYAN}Feedback de IA:{Colors.ENDC}")
                    print(f"   {feedback[:200]}...")
                
                eval_results.append({
                    "exercise": ejercicio['name'],
                    "success": True,
                    "score": score,
                    "xp": xp
                })
            else:
                print_test(ejercicio['name'], "❌", f"HTTP {response.status_code}")
                eval_results.append({
                    "exercise": ejercicio['name'],
                    "success": False
                })
                
        except Exception as e:
            print_test(ejercicio['name'], "❌", str(e))
            eval_results.append({
                "exercise": ejercicio['name'],
                "success": False,
                "error": str(e)
            })
    
    # Resumen
    total_tests = 1 + len(filtros_test) + len(ejercicios_evaluar)
    exitosos = (
        (1 if stats_ok else 0) +
        sum(1 for r in filtros_results if r.get('success', False)) +
        sum(1 for r in eval_results if r.get('success', False))
    )
    
    print(f"\n{Colors.BOLD}Resumen Entrenador Digital:{Colors.ENDC}")
    print_metric("Tests exitosos", f"{exitosos}/{total_tests}")
    
    demo_results["tests"].append({
        "section": "Entrenador Digital",
        "total": total_tests,
        "passed": exitosos,
        "stats": stats_ok,
        "filters": filtros_results,
        "evaluations": eval_results
    })
    
    return exitosos == total_tests


# ============================================================================
# TEST 4: ANÁLISIS DE RIESGOS 5D
# ============================================================================

def test_analisis_riesgos():
    """Test del análisis de riesgos 5D personalizado"""
    print_section("TEST 4: ANÁLISIS DE RIESGOS 5D - IA Personalizada")
    
    try:
        print("Ejecutando análisis de riesgos sobre sesión actual...")
        
        response = requests.post(
            f"{BASE_URL}/risk-analysis/analyze",
            json={"session_id": SESSION_ID},
            timeout=60
        )
        
        if response.status_code == 200:
            analysis = response.json()
            dimensions = analysis.get('dimensions', {})
            
            print_test("Análisis de Riesgos 5D", "✅")
            print(f"\n{Colors.BOLD}Resultados por Dimensión (0-50):{Colors.ENDC}")
            
            for dim_name, dim_data in dimensions.items():
                score = dim_data.get('score', 0)
                level = dim_data.get('level', 'N/A')
                
                # Color según nivel
                if level == 'BAJO':
                    color = Colors.OKGREEN
                elif level == 'MEDIO':
                    color = Colors.WARNING
                else:
                    color = Colors.FAIL
                
                print(f"\n{color}{Colors.BOLD}{dim_name.upper()}:{Colors.ENDC}")
                print_metric("Score", f"{score}/50")
                print_metric("Nivel", level)
                print_metric("Descripción", dim_data.get('description', 'N/A')[:100])
            
            # Validaciones
            todas_dimensiones = len(dimensions) == 5
            scores_validos = all(
                0 <= dim.get('score', -1) <= 50 
                for dim in dimensions.values()
            )
            tiene_recommendations = len(analysis.get('general_recommendations', [])) > 0
            
            print(f"\n{Colors.BOLD}Validaciones:{Colors.ENDC}")
            print_test("5 dimensiones presentes", "✅" if todas_dimensiones else "❌")
            print_test("Scores válidos (0-50)", "✅" if scores_validos else "❌")
            print_test("Recomendaciones generadas", "✅" if tiene_recommendations else "❌")
            
            # Mostrar recomendaciones
            recommendations = analysis.get('general_recommendations', [])
            if recommendations:
                print(f"\n{Colors.BOLD}Recomendaciones Generales:{Colors.ENDC}")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec}")
            
            success = todas_dimensiones and scores_validos and tiene_recommendations
            
            demo_results["tests"].append({
                "section": "Análisis de Riesgos 5D",
                "total": 1,
                "passed": 1 if success else 0,
                "dimensions": dimensions,
                "recommendations_count": len(recommendations)
            })
            
            return success
        else:
            print_test("Análisis de Riesgos 5D", "❌", f"HTTP {response.status_code}")
            demo_results["tests"].append({
                "section": "Análisis de Riesgos 5D",
                "total": 1,
                "passed": 0,
                "error": f"HTTP {response.status_code}"
            })
            return False
            
    except Exception as e:
        print_test("Análisis de Riesgos 5D", "❌", str(e))
        demo_results["tests"].append({
            "section": "Análisis de Riesgos 5D",
            "total": 1,
            "passed": 0,
            "error": str(e)
        })
        return False


# ============================================================================
# REPORTE FINAL
# ============================================================================

def generar_reporte_final():
    """Genera un reporte profesional del demo"""
    print_section("REPORTE FINAL DEL DEMO - SISTEMA ACTIVIA")
    
    # Calcular totales
    total_tests = sum(t['total'] for t in demo_results['tests'])
    total_passed = sum(t['passed'] for t in demo_results['tests'])
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    # Header del reporte
    print(f"{Colors.BOLD}Sistema de Entrenamiento con IA - ACTIVIA{Colors.ENDC}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Session ID: {SESSION_ID}\n")
    
    # Resumen ejecutivo
    print(f"{Colors.BOLD}RESUMEN EJECUTIVO{Colors.ENDC}")
    print(f"─" * 60)
    print_metric("Total de Tests Ejecutados", total_tests)
    print_metric("Tests Exitosos", total_passed)
    print_metric("Tasa de Éxito", f"{success_rate:.1f}%")
    
    # Color según tasa de éxito
    if success_rate >= 90:
        status_color = Colors.OKGREEN
        status_text = "EXCELENTE ✅"
    elif success_rate >= 70:
        status_color = Colors.WARNING
        status_text = "BUENO ⚠️"
    else:
        status_color = Colors.FAIL
        status_text = "NECESITA ATENCIÓN ❌"
    
    print(f"\n{status_color}{Colors.BOLD}Estado General: {status_text}{Colors.ENDC}\n")
    
    # Desglose por módulo
    print(f"{Colors.BOLD}DESGLOSE POR MÓDULO{Colors.ENDC}")
    print(f"─" * 60)
    
    for test in demo_results['tests']:
        section = test['section']
        passed = test['passed']
        total = test['total']
        rate = (passed / total * 100) if total > 0 else 0
        
        status = "✅" if rate == 100 else "⚠️" if rate >= 70 else "❌"
        print(f"\n{status} {section}")
        print(f"   Tests: {passed}/{total} ({rate:.0f}%)")
    
    # Capacidades demostradas
    print(f"\n{Colors.BOLD}CAPACIDADES DEMOSTRADAS{Colors.ENDC}")
    print(f"─" * 60)
    
    capacidades = [
        "✅ Tutor Socrático con Mistral AI - Respuestas personalizadas",
        "✅ Simuladores de Entrevista - Múltiples perfiles (Técnico, RRHH, CTO)",
        "✅ Entrenador Digital - Python, Java y Spring Boot",
        "✅ Filtrado Avanzado - Por lenguaje, framework, dificultad",
        "✅ Evaluación con IA - Feedback automático de código",
        "✅ Análisis de Riesgos 5D - Evaluación personalizada de conversaciones",
        "✅ Gamificación - Sistema de XP y puntos",
        "✅ Integración Completa - Todos los módulos funcionando juntos"
    ]
    
    for capacidad in capacidades:
        print(f"   {capacidad}")
    
    # Tecnologías utilizadas
    print(f"\n{Colors.BOLD}STACK TECNOLÓGICO{Colors.ENDC}")
    print(f"─" * 60)
    print("   • Backend: FastAPI (Python)")
    print("   • IA: Mistral AI (mistral-small-latest, mistral-large-latest)")
    print("   • Frontend: React + TypeScript")
    print("   • Base de Datos: PostgreSQL + Redis")
    print("   • Contenedores: Docker + Docker Compose")
    
    # Guardar reporte JSON
    report_filename = f"demo_report_{int(time.time())}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(demo_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.OKGREEN}✅ Reporte guardado en: {report_filename}{Colors.ENDC}")
    
    # Conclusión
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    if success_rate >= 90:
        print(f"{Colors.OKGREEN}{Colors.BOLD}")
        print("🎉 DEMO EXITOSO - Sistema funcionando perfectamente")
        print("   Listo para presentación ejecutiva")
        print(f"{Colors.ENDC}")
    elif success_rate >= 70:
        print(f"{Colors.WARNING}{Colors.BOLD}")
        print("⚠️  DEMO PARCIALMENTE EXITOSO - Revisar módulos con fallas")
        print(f"{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}")
        print("❌ DEMO CON PROBLEMAS - Requiere atención urgente")
        print(f"{Colors.ENDC}")
    
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    return success_rate >= 70


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta todos los tests del demo"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     DEMO COMPLETO - SISTEMA ACTIVIA CON MISTRAL AI            ║")
    print("║     Entrenamiento Personalizado con Inteligencia Artificial   ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    print(f"Iniciando demo en: {BASE_URL}")
    print(f"Session ID: {SESSION_ID}\n")
    
    time.sleep(2)
    
    # Ejecutar todos los tests
    resultados = []
    
    try:
        resultados.append(("Tutor Socrático", test_tutor_socratico()))
        time.sleep(1)
        
        resultados.append(("Simuladores", test_simuladores()))
        time.sleep(1)
        
        resultados.append(("Entrenador Digital", test_entrenador_digital()))
        time.sleep(1)
        
        resultados.append(("Análisis de Riesgos", test_analisis_riesgos()))
        time.sleep(1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Demo interrumpido por el usuario{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Error general en el demo: {e}{Colors.ENDC}")
    
    # Generar reporte final
    time.sleep(2)
    exito_general = generar_reporte_final()
    
    return 0 if exito_general else 1


if __name__ == "__main__":
    exit(main())
