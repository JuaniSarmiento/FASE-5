"""
API Router para el Entrenador Digital - Modo Examen

Este módulo maneja:
1. Selección de materias y temas
2. Inicio de sesiones de entrenamiento (modo examen)
3. Sistema de pistas con penalización
4. Evaluación final con descuento por pistas usadas
5. Temporizador y control de tiempo
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import uuid
import redis
import os

from backend.database.config import get_db
from backend.api.routers.auth_new import get_current_user
from backend.database.models import UserDB as User
from backend.api.deps import get_llm_provider
from backend.llm.base import LLMMessage, LLMRole
from backend.services.code_evaluator import CodeEvaluator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/training", tags=["Digital Training"])

# Cargar datos de materias y temas
TRAINING_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "training"

# Configurar Redis para sesiones
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Redis conectado para sesiones de training")
    USE_REDIS = True
except Exception as e:
    logger.warning(f"⚠️ Redis no disponible, usando memoria: {e}")
    USE_REDIS = False
    redis_client = None


# ============================================================================
# SCHEMAS
# ============================================================================

class TemaInfo(BaseModel):
    """Información de un tema disponible"""
    id: str
    nombre: str
    descripcion: str
    dificultad: str
    tiempo_estimado_min: int


class MateriaInfo(BaseModel):
    """Información de una materia con sus temas"""
    materia: str
    codigo: str
    temas: List[TemaInfo]


class IniciarEntrenamientoRequest(BaseModel):
    """Request para iniciar una sesión de entrenamiento"""
    materia_codigo: str
    tema_id: str


class EjercicioActual(BaseModel):
    """Ejercicio actual que el usuario está resolviendo"""
    numero: int
    consigna: str
    codigo_inicial: str
    
class SesionEntrenamiento(BaseModel):
    """Información de una sesión de entrenamiento activa"""
    session_id: str
    materia: str
    tema: str
    ejercicio_actual: EjercicioActual
    total_ejercicios: int
    ejercicios_completados: int
    tiempo_limite_min: int
    inicio: datetime
    fin_estimado: datetime


class SubmitEjercicioRequest(BaseModel):
    """Request para enviar el código de un ejercicio"""
    session_id: str
    codigo_usuario: str
    
class ResultadoEjercicio(BaseModel):
    """Resultado de un ejercicio individual"""
    numero: int
    correcto: bool
    tests_pasados: int
    tests_totales: int
    mensaje: str


class ResultadoFinal(BaseModel):
    """Resultado final del examen completo"""
    session_id: str
    nota_final: float
    ejercicios_correctos: int
    total_ejercicios: int
    porcentaje: float
    aprobado: bool
    tiempo_usado_min: int
    resultados_detalle: List[ResultadoEjercicio]


class SolicitarPistaRequest(BaseModel):
    """Request para solicitar una pista"""
    session_id: str
    numero_pista: int  # 0, 1 o 2


class PistaResponse(BaseModel):
    """Respuesta con una pista"""
    contenido: str
    numero: int
    total_pistas: int


class CorreccionIARequest(BaseModel):
    """Request para solicitar corrección con IA"""
    session_id: str
    codigo_usuario: str
    
    
class CorreccionIAResponse(BaseModel):
    """Respuesta con corrección y sugerencias de IA"""
    analisis: str
    sugerencias: List[str]
    codigo_corregido: Optional[str] = None
    porcentaje: float
    aprobado: bool
    tiempo_usado_min: int
    resultados_detalle: List[ResultadoEjercicio]


# ============================================================================
# ALMACENAMIENTO DE SESIONES (Redis + fallback a memoria)
# ============================================================================

# Fallback en memoria si Redis no está disponible
sesiones_memoria: Dict[str, Dict[str, Any]] = {}

def guardar_sesion(session_id: str, datos: Dict[str, Any]) -> None:
    """Guarda una sesión en Redis o memoria"""
    # Convertir datetime a string para JSON
    datos_serializables = datos.copy()
    if 'inicio' in datos_serializables and isinstance(datos_serializables['inicio'], datetime):
        datos_serializables['inicio'] = datos_serializables['inicio'].isoformat()
    if 'fin_estimado' in datos_serializables and isinstance(datos_serializables['fin_estimado'], datetime):
        datos_serializables['fin_estimado'] = datos_serializables['fin_estimado'].isoformat()
    
    if USE_REDIS and redis_client:
        try:
            # Guardar en Redis con TTL de 2 horas
            redis_client.setex(
                f"training_session:{session_id}",
                7200,  # 2 horas
                json.dumps(datos_serializables)
            )
            logger.info(f"✅ Sesión {session_id} guardada en Redis")
        except Exception as e:
            logger.error(f"Error guardando en Redis: {e}")
            sesiones_memoria[session_id] = datos
    else:
        sesiones_memoria[session_id] = datos

def obtener_sesion(session_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene una sesión de Redis o memoria"""
    if USE_REDIS and redis_client:
        try:
            datos_json = redis_client.get(f"training_session:{session_id}")
            if datos_json:
                datos = json.loads(datos_json)
                # Convertir strings de datetime de vuelta a datetime
                if 'inicio' in datos and isinstance(datos['inicio'], str):
                    datos['inicio'] = datetime.fromisoformat(datos['inicio'])
                if 'fin_estimado' in datos and isinstance(datos['fin_estimado'], str):
                    datos['fin_estimado'] = datetime.fromisoformat(datos['fin_estimado'])
                logger.info(f"✅ Sesión {session_id} recuperada de Redis")
                return datos
        except Exception as e:
            logger.error(f"Error obteniendo de Redis: {e}")
    
    return sesiones_memoria.get(session_id)

def listar_sesiones_activas() -> List[str]:
    """Lista los IDs de sesiones activas"""
    if USE_REDIS and redis_client:
        try:
            keys = redis_client.keys("training_session:*")
            return [k.replace("training_session:", "") for k in keys]
        except:
            pass
    return list(sesiones_memoria.keys())


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def cargar_materia_datos(codigo_materia: str) -> Dict[str, Any]:
    """Carga los datos de una materia desde JSON"""
    # Mapeo de códigos a nombres de archivo
    mapeo_archivos = {
        "PROG1": "programacion1_temas.json",
        "programacion1": "programacion1_temas.json"
    }
    
    nombre_archivo = mapeo_archivos.get(codigo_materia.upper())
    if not nombre_archivo:
        nombre_archivo = f"{codigo_materia.lower()}_temas.json"
    
    archivo = TRAINING_DATA_PATH / nombre_archivo
    
    if not archivo.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Materia {codigo_materia} no encontrada"
        )
    
    with open(archivo, 'r', encoding='utf-8') as f:
        return json.load(f)


def obtener_tema(codigo_materia: str, tema_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene un tema específico de una materia"""
    datos = cargar_materia_datos(codigo_materia)
    
    for tema in datos['temas']:
        if tema['id'] == tema_id:
            return tema
    
    return None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/materias", response_model=List[MateriaInfo])
async def obtener_materias_disponibles():
    """
    Obtiene la lista de materias disponibles con sus temas
    """
    try:
        materias = []
        
        # Por ahora solo Programación 1
        # En el futuro agregar más materias
        try:
            datos_prog1 = cargar_materia_datos("PROG1")
            
            temas_info = []
            for tema in datos_prog1['temas']:
                temas_info.append(TemaInfo(
                    id=tema['id'],
                    nombre=tema['nombre'],
                    descripcion=tema['descripcion'],
                    dificultad=tema['dificultad'],
                    tiempo_estimado_min=tema['tiempo_estimado_min']
                ))
            
            materias.append(MateriaInfo(
                materia=datos_prog1['materia'],
                codigo=datos_prog1['codigo'],
                temas=temas_info
            ))
        except Exception as e:
            logger.warning(f"No se pudo cargar Programación 1: {e}")
        
        return materias
        
    except Exception as e:
        logger.error(f"Error obteniendo materias: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al cargar las materias disponibles"
        )


@router.post("/iniciar", response_model=SesionEntrenamiento)
async def iniciar_entrenamiento(
    request: IniciarEntrenamientoRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Inicia una nueva sesión de entrenamiento con múltiples ejercicios
    """
    try:
        # Obtener el tema seleccionado
        tema = obtener_tema(request.materia_codigo, request.tema_id)
        
        if not tema:
            raise HTTPException(
                status_code=404,
                detail=f"Tema {request.tema_id} no encontrado"
            )
        
        # Verificar si el tema tiene ejercicios múltiples o uno solo
        if 'ejercicios' in tema:
            ejercicios = tema['ejercicios']
            total_ejercicios = len(ejercicios)
            ejercicio_inicial = ejercicios[0]
        elif 'ejercicio' in tema:
            # Formato antiguo con un solo ejercicio
            ejercicio_inicial = tema['ejercicio']
            ejercicios = [ejercicio_inicial]
            total_ejercicios = 1
        else:
            raise HTTPException(
                status_code=500,
                detail="Tema sin ejercicios configurados"
            )
        
        # Crear ID único para la sesión
        session_id = str(uuid.uuid4())
        
        # Calcular tiempos
        inicio = datetime.now()
        tiempo_limite = tema['tiempo_estimado_min']
        fin_estimado = inicio + timedelta(minutes=tiempo_limite)
        
        # Crear datos de sesión
        datos_sesion = {
            'user_id': current_user.id,
            'materia_codigo': request.materia_codigo,
            'tema_id': request.tema_id,
            'ejercicios': ejercicios,
            'total_ejercicios': total_ejercicios,
            'ejercicio_actual_index': 0,
            'resultados': [],
            'inicio': inicio,
            'fin_estimado': fin_estimado,
            'tiempo_limite_min': tiempo_limite,
            'finalizado': False
        }
        
        # Guardar sesión en Redis o memoria
        guardar_sesion(session_id, datos_sesion)
        logger.info(f"✅ Nueva sesión creada: {session_id}")
        
        # Construir respuesta con el primer ejercicio
        return SesionEntrenamiento(
            session_id=session_id,
            materia=tema['nombre'],
            tema=tema['nombre'],
            ejercicio_actual=EjercicioActual(
                numero=1,
                consigna=ejercicio_inicial['consigna'],
                codigo_inicial=ejercicio_inicial['codigo_inicial']
            ),
            total_ejercicios=total_ejercicios,
            ejercicios_completados=0,
            tiempo_limite_min=tiempo_limite,
            inicio=inicio,
            fin_estimado=fin_estimado
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error iniciando entrenamiento: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al iniciar el entrenamiento"
        )


@router.post("/submit-ejercicio")
async def submit_ejercicio(
    request: SubmitEjercicioRequest,
    current_user: User = Depends(get_current_user),
    llm = Depends(get_llm_provider)
):
    """
    Envía el código de un ejercicio para evaluación con IA
    La IA analiza el código y determina si cumple con la consigna
    """
    try:
        # Verificar sesión con logging detallado
        logger.info(f"🔥🔥🔥 Submit ejercicio - Session ID: {request.session_id}")
        print(f"🔥🔥🔥 SUBMIT EJERCICIO LLAMADO - Session: {request.session_id}")
        sesiones_activas = listar_sesiones_activas()
        logger.info(f"Sesiones activas: {sesiones_activas}")
        
        sesion = obtener_sesion(request.session_id)
        if not sesion:
            logger.error(f"Sesión {request.session_id} no encontrada. Sesiones disponibles: {len(sesiones_activas)}")
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada o expirada"
            )
        
        # Verificar permisos
        if sesion['user_id'] != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para acceder a esta sesión"
            )
        
        # Obtener ejercicio actual
        index_actual = sesion['ejercicio_actual_index']
        logger.info(f"Evaluando ejercicio {index_actual + 1}/{sesion['total_ejercicios']}")
        
        if index_actual >= len(sesion['ejercicios']):
            logger.error(f"Índice fuera de rango: {index_actual} >= {len(sesion['ejercicios'])}")
            raise HTTPException(status_code=400, detail="Índice de ejercicio inválido")
        
        ejercicio = sesion['ejercicios'][index_actual]
        
        logger.info(f"📝 Ejercicio obtenido: {ejercicio.keys()}")
        logger.info(f"📝 Tests en ejercicio: {ejercicio.get('tests', 'NO TIENE TESTS')}")
        print(f"📝 EJERCICIO KEYS: {list(ejercicio.keys())}")
        print(f"📝 TESTS: {ejercicio.get('tests', [])}")
        
        # ========================================================================
        # EJECUTAR TESTS REALES (NO SIMULADOS)
        # ========================================================================
        
        logger.info(f"🧪🧪🧪 Ejecutando tests para ejercicio {index_actual + 1}")
        print(f"🧪🧪🧪 EJECUTANDO TESTS - Ejercicio {index_actual + 1}")
        
        # Importar execute_python_code del router de exercises
        from .exercises import execute_python_code
        
        # Obtener tests (pueden llamarse 'tests' o 'tests_ocultos')
        tests = ejercicio.get('tests', ejercicio.get('tests_ocultos', []))
        tests_passed = 0
        tests_total = len(tests)
        stdout_output = ""
        stderr_output = ""
        total_execution_time = 0
        
        # Ejecutar cada test
        for i, test in enumerate(tests, 1):
            test_input = test.get('input', '')
            expected = test.get('expected', '')
            
            logger.info(f"Ejecutando test {i}/{tests_total}: input='{test_input}', expected='{expected}'")
            
            # Ejecutar código del estudiante
            stdout, stderr, exec_time = execute_python_code(
                request.codigo_usuario,
                str(test_input),
                timeout_seconds=30
            )
            
            total_execution_time += exec_time
            stdout_output += stdout + "\n"
            stderr_output += stderr + "\n"
            
            # Verificar si pasó el test
            if not stderr:
                # Evaluar el test
                try:
                    # Si test_input es una llamada a función, evaluar
                    if '(' in test_input:
                        exec_globals = {}
                        exec(request.codigo_usuario, exec_globals)
                        actual_result = eval(test_input, exec_globals)
                        
                        # Comparar resultados - manejar diferentes formatos de expected
                        test_passed = False
                        
                        # Si expected es string, intentar varias estrategias de comparación
                        if isinstance(expected, str):
                            # 1. Comparar como strings (normalizar ambos)
                            actual_str = str(actual_result).strip()
                            expected_str = expected.strip()
                            
                            # 2. Si expected tiene "..." significa "aproximadamente"
                            if '...' in expected_str:
                                # Comparar prefijo (ej: "85.666..." == "85.66666...")
                                expected_prefix = expected_str.replace('...', '').strip()
                                if actual_str.startswith(expected_prefix):
                                    test_passed = True
                            # 3. Intentar evaluar expected como expresión Python y comparar
                            elif expected_str:
                                try:
                                    # Primero intentar eval directo
                                    expected_value = eval(expected_str)
                                    test_passed = actual_result == expected_value
                                except:
                                    # Si falla eval, normalizar strings y comparar
                                    # Quitar paréntesis, espacios extra, etc.
                                    actual_normalized = actual_str.replace("(", "").replace(")", "").replace("'", "").replace('"', "").strip()
                                    expected_normalized = expected_str.replace("(", "").replace(")", "").replace("'", "").replace('"', "").strip()
                                    test_passed = actual_normalized == expected_normalized
                        else:
                            # expected ya es un valor Python, comparar directo
                            test_passed = actual_result == expected
                        
                        if test_passed:
                            tests_passed += 1
                            logger.info(f"✓ Test {i} PASADO")
                        else:
                            logger.warning(f"✗ Test {i} FALLÓ: expected={expected}, actual={actual_result}")
                    else:
                        # Comparar output directo
                        if stdout.strip() == str(expected).strip():
                            tests_passed += 1
                            logger.info(f"✓ Test {i} PASADO")
                        else:
                            logger.warning(f"✗ Test {i} FALLÓ: output no coincide")
                except Exception as e:
                    logger.warning(f"✗ Test {i} ERROR: {e}")
            else:
                logger.warning(f"✗ Test {i} FALLÓ: {stderr}")
        
        # Crear sandbox_result con resultados reales
        sandbox_result = {
            'exit_code': 0 if not stderr_output.strip() else 1,
            'stdout': stdout_output.strip(),
            'stderr': stderr_output.strip(),
            'tests_passed': tests_passed,
            'tests_total': tests_total,
            'execution_time_ms': total_execution_time,
            'language': 'python',
            'evaluation_type': 'execution'
        }
        
        logger.info(f"📊 Tests ejecutados: {tests_passed}/{tests_total} pasados")
        
        # ========================================================================
        # EVALUACIÓN CON CODE_EVALUATOR (Sistema Profesional)
        # ========================================================================
        
        logger.info(f"Evaluando con CodeEvaluator - Ejercicio {index_actual + 1}")
        
        # Preparar formato de ejercicio para CodeEvaluator
        exercise_formatted = {
            'id': f"training_{sesion['tema_id']}_{index_actual + 1}",
            'meta': {
                'title': f"Ejercicio {index_actual + 1}: {ejercicio.get('consigna', '')[:50]}..."
            },
            'content': {
                'mission_markdown': ejercicio.get('consigna', ''),
                'constraints': [f"Debe cumplir: {test['input']} → {test['expected']}" for test in ejercicio.get('tests', [])]
            }
        }
        
        # Evaluar con CodeEvaluator (sandbox_result ya fue creado arriba con tests reales)
        try:
            evaluator = CodeEvaluator(llm_client=llm)
            evaluation_result = await evaluator.evaluate(
                exercise=exercise_formatted,
                student_code=request.codigo_usuario,
                sandbox_result=sandbox_result,
                student_id=str(current_user.id)
            )
            
            logger.info(f"✅ Evaluación completada por IA")
            
            # Extraer datos de la evaluación
            eval_data = evaluation_result.get('evaluation', {})
            score = eval_data.get('score', 0)
            status = eval_data.get('status', 'FAIL')
            
            # Usar los tests reales que ya ejecutamos
            correcto = status == 'PASS' and score >= 70 and tests_passed == tests_total
            mensaje = eval_data.get('toast_message', 'Evaluado por IA')
            
            # Guardar evaluación completa para feedback detallado
            feedback_completo = eval_data.get('summary_markdown', '')
            
        except Exception as e:
            logger.error(f"Error en evaluación con CodeEvaluator: {e}", exc_info=True)
            # Fallback seguro - usar resultados de tests reales
            correcto = tests_passed == tests_total and tests_total > 0
            mensaje = f"Tests: {tests_passed}/{tests_total}"
            feedback_completo = f"Tests ejecutados: {tests_passed}/{tests_total} pasados."
        
        # Guardar resultado
        resultado = {
            'numero': index_actual + 1,
            'correcto': correcto,
            'tests_pasados': tests_passed,
            'tests_totales': tests_total,
            'mensaje': mensaje
        }
        sesion['resultados'].append(resultado)
        
        # Avanzar al siguiente ejercicio
        sesion['ejercicio_actual_index'] += 1
        
        # Guardar sesión actualizada
        guardar_sesion(request.session_id, sesion)
        
        # Verificar si hay más ejercicios
        hay_mas = sesion['ejercicio_actual_index'] < sesion['total_ejercicios']
        
        if hay_mas:
            # Retornar resultado y siguiente ejercicio
            siguiente = sesion['ejercicios'][sesion['ejercicio_actual_index']]
            return {
                'resultado': resultado,
                'hay_siguiente': True,
                'siguiente_ejercicio': {
                    'numero': sesion['ejercicio_actual_index'] + 1,
                    'consigna': siguiente['consigna'],
                    'codigo_inicial': siguiente['codigo_inicial']
                }
            }
        else:
            # Último ejercicio, calcular resultado final
            sesion['finalizado'] = True
            logger.info(f"Sesión {request.session_id} finalizada exitosamente")
            
            # Calcular nota basándose en porcentaje de tests pasados (más justo)
            total_tests_todos = sum(r['tests_totales'] for r in sesion['resultados'])
            total_tests_pasados = sum(r['tests_pasados'] for r in sesion['resultados'])
            
            # Calcular porcentaje y nota
            if total_tests_todos > 0:
                porcentaje = (total_tests_pasados / total_tests_todos) * 100
                nota = (total_tests_pasados / total_tests_todos) * 10
            else:
                porcentaje = 0
                nota = 0
            
            # Contar ejercicios perfectos (100% tests pasados)
            correctos = sum(1 for r in sesion['resultados'] if r['correcto'])
            
            logger.info(f"📊 Nota final calculada: {nota:.2f}/10 ({total_tests_pasados}/{total_tests_todos} tests)")
            
            # No borrar la sesión aquí, dejarla para revisión
            # del sesiones_activas[request.session_id]  # REMOVED
            
            return {
                'resultado': resultado,
                'hay_siguiente': False,
                'resultado_final': {
                    'session_id': request.session_id,
                    'nota_final': round(nota, 2),
                    'ejercicios_correctos': correctos,
                    'total_ejercicios': sesion['total_ejercicios'],
                    'porcentaje': round(porcentaje, 1),
                    'aprobado': nota >= 6,
                    'tiempo_usado_min': int((datetime.now() - sesion['inicio']).total_seconds() / 60),
                    'resultados_detalle': sesion['resultados']
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluando ejercicio: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al evaluar el ejercicio"
        )


@router.post("/pista", response_model=PistaResponse)
async def solicitar_pista(
    request: SolicitarPistaRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Solicita una pista para el ejercicio actual
    """
    try:
        # Verificar sesión
        sesion = obtener_sesion(request.session_id)
        if not sesion:
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada o expirada"
            )
        
        # Verificar permisos
        if sesion['user_id'] != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para acceder a esta sesión"
            )
        
        # Obtener ejercicio actual
        index_actual = sesion['ejercicio_actual_index']
        ejercicio = sesion['ejercicios'][index_actual]
        
        # Verificar que el ejercicio tenga pistas
        if 'pistas' not in ejercicio or not ejercicio['pistas']:
            raise HTTPException(
                status_code=404,
                detail="Este ejercicio no tiene pistas disponibles"
            )
        
        # Verificar que el número de pista sea válido
        if request.numero_pista < 0 or request.numero_pista >= len(ejercicio['pistas']):
            raise HTTPException(
                status_code=400,
                detail=f"Número de pista inválido. Disponibles: 0-{len(ejercicio['pistas']) - 1}"
            )
        
        pista = ejercicio['pistas'][request.numero_pista]
        
        return PistaResponse(
            contenido=pista,
            numero=request.numero_pista,
            total_pistas=len(ejercicio['pistas'])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo pista: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al obtener la pista"
        )


@router.post("/corregir-ia", response_model=CorreccionIAResponse)
async def corregir_con_ia(
    request: CorreccionIARequest,
    current_user: User = Depends(get_current_user),
    llm = Depends(get_llm_provider)
):
    """
    Usa IA (Gemini/Mistral) para analizar el código y dar feedback
    """
    try:
        # Verificar sesión
        sesion = obtener_sesion(request.session_id)
        if not sesion:
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada o expirada"
            )
        
        # Verificar permisos
        if sesion['user_id'] != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para acceder a esta sesión"
            )
        
        # Obtener ejercicio actual
        index_actual = sesion['ejercicio_actual_index']
        ejercicio = sesion['ejercicios'][index_actual]
        
        # Ejecutar tests para ver qué falla
        errores_tests = []
        namespace = {}
        
        try:
            exec(request.codigo_usuario, namespace)
            
            for i, test in enumerate(ejercicio['tests']):
                try:
                    result = eval(test['input'], namespace)
                    expected = test['expected']
                    
                    if isinstance(expected, float):
                        if abs(result - expected) >= 0.01:
                            errores_tests.append(f"Test {i+1}: {test['input']} debería retornar {expected}, pero retorna {result}")
                    elif result != expected:
                        errores_tests.append(f"Test {i+1}: {test['input']} debería retornar {expected}, pero retorna {result}")
                except Exception as e:
                    errores_tests.append(f"Test {i+1}: {test['input']} genera error: {str(e)}")
        except Exception as e:
            errores_tests.append(f"Error al ejecutar código: {str(e)}")
        
        # Preparar prompt para la IA
        tests_descritos = "\n".join(f"- {test['input']} debe retornar {test['expected']}" for test in ejercicio['tests'])
        errores_descritos = "\n".join(errores_tests) if errores_tests else "El código pasa todos los tests correctamente."
        
        prompt = f"""Eres un tutor de programación Python. Un estudiante está trabajando en el siguiente ejercicio:

CONSIGNA: {ejercicio['consigna']}

CÓDIGO DEL ESTUDIANTE:
{request.codigo_usuario}

TESTS QUE DEBE PASAR:
{tests_descritos}

ERRORES ENCONTRADOS:
{errores_descritos}

Por favor:
1. Analiza qué está mal en el código (si algo está mal)
2. Da 2-3 sugerencias específicas para mejorar
3. NO des la solución completa, solo pistas útiles
4. Sé conciso y directo

Responde en formato:
ANÁLISIS: [tu análisis breve]
SUGERENCIAS:
- [sugerencia 1]
- [sugerencia 2]
- [sugerencia 3]
"""

        # Llamar a la IA
        messages = [
            LLMMessage(role=LLMRole.USER, content=prompt)
        ]
        
        response = await llm.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        # Parsear respuesta
        respuesta_ia = response.content
        
        # Extraer análisis y sugerencias
        analisis = ""
        sugerencias = []
        
        if "ANÁLISIS:" in respuesta_ia:
            analisis = respuesta_ia.split("ANÁLISIS:")[1].split("SUGERENCIAS:")[0].strip()
        
        if "SUGERENCIAS:" in respuesta_ia:
            sugerencias_texto = respuesta_ia.split("SUGERENCIAS:")[1].strip()
            sugerencias = [s.strip("- ").strip() for s in sugerencias_texto.split("\n") if s.strip().startswith("-")]
        
        if not analisis:
            analisis = respuesta_ia[:200] + "..."
        
        if not sugerencias:
            sugerencias = ["Revisa la lógica de tu código", "Verifica que retornes el valor correcto", "Prueba cada test manualmente"]
        
        return CorreccionIAResponse(
            analisis=analisis,
            sugerencias=sugerencias[:3],  # Máximo 3 sugerencias
            codigo_corregido=None  # No dar código corregido, solo hints
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en corrección IA: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al analizar con IA"
        )
        
        # Marcar como finalizada
        sesion['finalizado'] = True
        sesion['codigo_enviado'] = request.codigo_usuario
        
        # ====================================================================
        # EJECUTAR TESTS AUTOMÁTICOS
        # ====================================================================
        
        ejercicio = sesion['ejercicio']
        tests_pasados = 0
        tests_totales = 0
        errores_tests = []
        
        try:
            # Crear namespace para ejecutar el código
            namespace = {}
            exec(request.codigo_usuario, namespace)
            
            # Ejecutar tests
            tests_ocultos = ejercicio.get('tests_ocultos', [])
            tests_totales = len(tests_ocultos)
            
            for i, test in enumerate(tests_ocultos, 1):
                try:
                    # Ejecutar test
                    resultado = eval(test['input'], namespace)
                    esperado = test['expected']
                    
                    # Verificar resultado
                    if str(resultado) == esperado or resultado == esperado:
                        tests_pasados += 1
                    else:
                        errores_tests.append(f"Test {i}: esperado {esperado}, obtenido {resultado}")
                        
                except Exception as e:
                    errores_tests.append(f"Test {i}: error de ejecución - {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error ejecutando código: {e}")
            errores_tests.append(f"Error general: {str(e)}")
        
        # Calcular nota base (70% tests + 30% calidad de código)
        porcentaje_tests = (tests_pasados / tests_totales * 100) if tests_totales > 0 else 0
        nota_base = porcentaje_tests * 0.7  # 70% por tests
        
        # ====================================================================
        # EVALUACIÓN CON IA
        # ====================================================================
        
        try:
            prompt_evaluacion = f"""Evalúa el siguiente código de Python para un ejercicio de programación.

EJERCICIO:
{ejercicio['titulo']}

CONSIGNA:
{ejercicio['consigna']}

REQUISITOS:
{chr(10).join('- ' + req for req in ejercicio['requisitos'])}

CÓDIGO DEL ESTUDIANTE:
```python
{request.codigo_usuario}
```

RESULTADOS DE TESTS:
- Tests pasados: {tests_pasados}/{tests_totales}
- Errores: {chr(10).join(errores_tests) if errores_tests else 'Ninguno'}

Proporciona:
1. Calificación de calidad de código (0-30 puntos)
2. Feedback constructivo
3. Lista de 3 fortalezas del código
4. Lista de 3 mejoras sugeridas

Formato JSON:
{{
    "calidad_codigo": <número 0-30>,
    "feedback": "<texto>",
    "fortalezas": ["...", "...", "..."],
    "mejoras": ["...", "...", "..."]
}}
"""
            
            messages = [
                LLMMessage(role=LLMRole.SYSTEM, content="Eres un profesor experto evaluando código de estudiantes."),
                LLMMessage(role=LLMRole.USER, content=prompt_evaluacion)
            ]
            
            response = llm_provider.generate(messages, max_tokens=1000, temperature=0.3)
            
            # Parsear respuesta
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            evaluacion_ia = json.loads(content.strip())
            
            # Agregar puntos de calidad al nota_base
            nota_base += evaluacion_ia.get('calidad_codigo', 0)
            
            feedback_ia = evaluacion_ia.get('feedback', 'Buen intento')
            fortalezas = evaluacion_ia.get('fortalezas', [])
            mejoras = evaluacion_ia.get('mejoras', [])
            
        except Exception as e:
            logger.error(f"Error en evaluación IA: {e}")
            feedback_ia = f"Tests pasados: {tests_pasados}/{tests_totales}"
            fortalezas = ["Código ejecutable"] if tests_pasados > 0 else []
            mejoras = ["Revisar lógica"] if tests_pasados < tests_totales else []
        
        # ====================================================================
        # CALCULAR NOTA FINAL CON PENALIZACIÓN
        # ====================================================================
        
        penalizacion = sesion['penalizacion_total']
        nota_final = max(0, nota_base - penalizacion)
        
        # Determinar si aprobó (>= 60)
        aprobado = nota_final >= 60
        
        # Construir resultado
        return ResultadoExamen(
            session_id=request.session_id,
            aprobado=aprobado,
            nota_base=round(nota_base, 2),
            penalizacion_pistas=penalizacion,
            nota_final=round(nota_final, 2),
            tiempo_usado_min=tiempo_usado_min,
            pistas_usadas=sesion['pistas_usadas'],
            feedback_ia=feedback_ia,
            tests_pasados=tests_pasados,
            tests_totales=tests_totales,
            fortalezas=fortalezas,
            mejoras=mejoras
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluando examen: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al evaluar el examen"
        )


@router.get("/sesion/{session_id}/estado")
async def obtener_estado_sesion(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el estado actual de una sesión
    (útil para mostrar tiempo restante, pistas usadas, etc.)
    """
    try:
        if session_id not in sesiones_activas:
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada"
            )
        
        sesion = sesiones_activas[session_id]
        
        if sesion['user_id'] != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para acceder a esta sesión"
            )
        
        # Calcular tiempo restante
        ahora = datetime.now()
        tiempo_transcurrido = ahora - sesion['inicio']
        tiempo_restante = sesion['fin_estimado'] - ahora
        
        return {
            "session_id": session_id,
            "finalizado": sesion['finalizado'],
            "tiempo_transcurrido_min": int(tiempo_transcurrido.total_seconds() / 60),
            "tiempo_restante_min": int(tiempo_restante.total_seconds() / 60),
            "pistas_usadas": sesion['pistas_usadas'],
            "penalizacion_actual": sesion['penalizacion_total'],
            "pistas_disponibles": len(sesion['ejercicio']['pistas']) - sesion['pistas_usadas']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el estado de la sesión"
        )


@router.delete("/sesion/{session_id}")
async def cancelar_sesion(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancela una sesión activa
    """
    try:
        if session_id not in sesiones_activas:
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada"
            )
        
        sesion = sesiones_activas[session_id]
        
        if sesion['user_id'] != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para cancelar esta sesión"
            )
        
        # Eliminar sesión
        del sesiones_activas[session_id]
        
        return {"message": "Sesión cancelada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelando sesión: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al cancelar la sesión"
        )
