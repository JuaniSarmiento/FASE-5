import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import {
  Clock,
  Send,
  CheckCircle,
  XCircle,
  TrendingUp,
  ArrowLeft,
  ChevronRight,
  Lightbulb,
  Sparkles
} from 'lucide-react';
import { 
  trainingService, 
  SesionEntrenamiento, 
  ResultadoFinal, 
  EjercicioActual, 
  SubmitEjercicioResponse,
  PistaResponse,
  CorreccionIAResponse
} from '../services/api';

const TrainingExamPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const { language, unit_number, leccion_nombre } = location.state || {};

  const [sesion, setSesion] = useState<SesionEntrenamiento | null>(null);
  const [ejercicioActual, setEjercicioActual] = useState<EjercicioActual | null>(null);
  const [codigo, setCodigo] = useState<string>('');
  const [tiempoRestante, setTiempoRestante] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [resultadoFinal, setResultadoFinal] = useState<ResultadoFinal | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ejerciciosCompletados, setEjerciciosCompletados] = useState<number>(0);
  const [mostrarResultadoEjercicio, setMostrarResultadoEjercicio] = useState<boolean>(false);
  const [ultimoResultado, setUltimoResultado] = useState<any>(null);

  // Estados para pistas y corrección IA
  const [pistaActual, setPistaActual] = useState<PistaResponse | null>(null);
  const [numeroPistaActual, setNumeroPistaActual] = useState<number>(0);
  const [correccionIA, setCorreccionIA] = useState<CorreccionIAResponse | null>(null);
  const [loadingPista, setLoadingPista] = useState<boolean>(false);
  const [loadingIA, setLoadingIA] = useState<boolean>(false);

  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    if (!language || !unit_number) {
      navigate('/training');
      return;
    }

    iniciarSesion();

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [language, unit_number]);

  const iniciarSesion = async () => {
    try {
      setLoading(true);
      const data = await trainingService.iniciarEntrenamiento({
        language,
        unit_number
      });
      
      setSesion(data);
      setEjercicioActual(data.ejercicio_actual);
      setCodigo(data.ejercicio_actual.codigo_inicial);
      setEjerciciosCompletados(data.ejercicios_completados);
      
      const inicio = new Date(data.inicio).getTime();
      const fin = new Date(data.fin_estimado).getTime();
      const restante = Math.floor((fin - Date.now()) / 1000);
      setTiempoRestante(restante);
      
      timerRef.current = window.setInterval(() => {
        setTiempoRestante((prev) => {
          if (prev <= 1) {
            if (timerRef.current) clearInterval(timerRef.current);
            alert('¡Tiempo agotado!');
            navigate('/training');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      
    } catch (err) {
      console.error('Error iniciando sesión:', err);
      setError('Error al iniciar la sesión');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitEjercicio = async () => {
    if (!sesion || !codigo.trim()) return;

    try {
      setSubmitting(true);
      setError(null);
      
      const response: SubmitEjercicioResponse = await trainingService.submitEjercicio({
        session_id: sesion.session_id,
        codigo_usuario: codigo
      });
      
      setUltimoResultado(response.resultado);
      setMostrarResultadoEjercicio(true);
      
      if (response.hay_siguiente && response.siguiente_ejercicio) {
        setTimeout(() => {
          setEjercicioActual(response.siguiente_ejercicio!);
          setCodigo(response.siguiente_ejercicio!.codigo_inicial);
          setEjerciciosCompletados(prev => prev + 1);
          setMostrarResultadoEjercicio(false);
          // Resetear pistas y corrección IA al cambiar de ejercicio
          setPistaActual(null);
          setNumeroPistaActual(0);
          setCorreccionIA(null);
        }, 2000);
      } else if (response.resultado_final) {
        setTimeout(() => {
          setResultadoFinal(response.resultado_final!);
          if (timerRef.current) clearInterval(timerRef.current);
        }, 2000);
      }
      
    } catch (err: any) {
      console.error('Error enviando ejercicio:', err);
      setError(err.response?.data?.detail || 'Error al evaluar el ejercicio');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSolicitarPista = async () => {
    if (!sesion) return;

    try {
      setLoadingPista(true);
      setError(null);
      
      const pista = await trainingService.solicitarPista({
        session_id: sesion.session_id,
        numero_pista: numeroPistaActual
      });
      
      setPistaActual(pista);
      setNumeroPistaActual(prev => prev + 1);
      
    } catch (err: any) {
      console.error('Error solicitando pista:', err);
      setError(err.response?.data?.detail || 'Error al obtener la pista');
    } finally {
      setLoadingPista(false);
    }
  };

  const handleCorregirConIA = async () => {
    if (!sesion || !codigo.trim()) return;

    try {
      setLoadingIA(true);
      setError(null);
      
      const correccion = await trainingService.corregirConIA({
        session_id: sesion.session_id,
        codigo_usuario: codigo
      });
      
      setCorreccionIA(correccion);
      
    } catch (err: any) {
      console.error('Error solicitando corrección IA:', err);
      setError(err.response?.data?.detail || 'Error al obtener corrección de IA');
    } finally {
      setLoadingIA(false);
    }
  };

  const formatTime = (segundos: number): string => {
    const minutos = Math.floor(segundos / 60);
    const segs = segundos % 60;
    return `${minutos.toString().padStart(2, '0')}:${segs.toString().padStart(2, '0')}`;
  };

  const getTimeColor = (): string => {
    if (tiempoRestante > 600) return 'text-green-400';
    if (tiempoRestante > 300) return 'text-yellow-400';
    return 'text-red-400 animate-pulse';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Cargando ejercicios...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-6">
        <div className="max-w-md glass rounded-xl p-8 text-center">
          <div className="w-16 h-16 mx-auto mb-6 bg-red-500/10 rounded-full flex items-center justify-center">
            <XCircle className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">Error al cargar</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button
            onClick={() => navigate('/training')}
            className="w-full py-3 px-6 rounded-xl gradient-bg text-white font-medium hover:opacity-90 transition-opacity"
          >
            Volver al menú
          </button>
        </div>
      </div>
    );
  }

  if (!sesion || !ejercicioActual) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Cargando ejercicios...</p>
        </div>
      </div>
    );
  }

  if (resultadoFinal) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            {resultadoFinal.aprobado ? (
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-green-500/10 mb-4">
                <CheckCircle className="w-16 h-16 text-green-400" />
              </div>
            ) : (
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-red-500/10 mb-4">
                <XCircle className="w-16 h-16 text-red-400" />
              </div>
            )}
            
            <h1 className="text-4xl font-bold gradient-text mb-2">
              {resultadoFinal.aprobado ? '¡Aprobado!' : 'Necesitas mejorar'}
            </h1>
            <p className="text-gray-400">Completaste {resultadoFinal.total_ejercicios} ejercicios</p>
          </div>

          <div className="glass rounded-2xl p-8 mb-6">
            <div className="text-center mb-6">
              <div className="text-6xl font-bold gradient-text mb-2">
                {resultadoFinal.nota_final.toFixed(1)}
              </div>
              <p className="text-gray-400">Nota Final</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800/50 rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-green-400 mb-1">
                  {resultadoFinal.ejercicios_correctos}
                </div>
                <p className="text-sm text-gray-400">Correctos</p>
              </div>
              
              <div className="bg-gray-800/50 rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-purple-400 mb-1">
                  {resultadoFinal.porcentaje.toFixed(0)}%
                </div>
                <p className="text-sm text-gray-400">Porcentaje</p>
              </div>
              
              <div className="bg-gray-800/50 rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-blue-400 mb-1">
                  {resultadoFinal.tiempo_usado_min} min
                </div>
                <p className="text-sm text-gray-400">Tiempo usado</p>
              </div>
            </div>
          </div>

          <div className="glass rounded-xl p-6 mb-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-purple-400" />
              Resultados por Ejercicio
            </h3>
            
            <div className="space-y-3">
              {resultadoFinal.resultados_detalle.map((r: any) => (
                <div key={r.numero} className="bg-gray-800/50 rounded-lg p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {r.correcto ? (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-400" />
                    )}
                    <span className="text-white font-medium">Ejercicio {r.numero}</span>
                  </div>
                  <div className="text-sm text-gray-400">
                    {r.tests_pasados}/{r.tests_totales} tests
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => navigate('/training')}
              className="flex-1 py-3 px-6 rounded-xl bg-gray-700 text-white font-medium hover:bg-gray-600 transition-colors"
            >
              Volver al menú
            </button>
            <button
              onClick={() => window.location.reload()}
              className="flex-1 py-3 px-6 rounded-xl gradient-bg text-white font-medium hover:opacity-90 transition-opacity"
            >
              Intentar de nuevo
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigate('/training')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Cancelar
          </button>
          
          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className="text-sm text-gray-400">Progreso</div>
              <div className="text-xl font-bold text-white">
                {ejerciciosCompletados} / {sesion?.total_ejercicios || 0}
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-sm text-gray-400">Tiempo restante</div>
              <div className={`text-2xl font-mono font-bold ${getTimeColor()}`}>
                <Clock className="w-5 h-5 inline mr-2" />
                {formatTime(tiempoRestante)}
              </div>
            </div>
          </div>
        </div>

        <div className="mb-6">
          <div className="flex gap-1">
            {Array.from({ length: sesion?.total_ejercicios || 0 }).map((_, i) => (
              <div
                key={i}
                className={`flex-1 h-2 rounded-full transition-colors ${
                  i < ejerciciosCompletados
                    ? 'bg-green-500'
                    : i === ejerciciosCompletados
                    ? 'bg-purple-500 animate-pulse'
                    : 'bg-gray-700'
                }`}
              ></div>
            ))}
          </div>
        </div>

        {mostrarResultadoEjercicio && ultimoResultado && (
          <div className={`glass rounded-xl p-6 mb-6 border-l-4 ${
            ultimoResultado.correcto ? 'border-green-500' : 'border-red-500'
          }`}>
            <div className="flex items-center gap-4">
              {ultimoResultado.correcto ? (
                <CheckCircle className="w-8 h-8 text-green-400" />
              ) : (
                <XCircle className="w-8 h-8 text-red-400" />
              )}
              <div>
                <h3 className="text-lg font-bold text-white">
                  {ultimoResultado.correcto ? '¡Correcto!' : 'Incorrecto'}
                </h3>
                <p className="text-gray-400">
                  {ultimoResultado.tests_pasados}/{ultimoResultado.tests_totales} tests pasados
                </p>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="glass rounded-xl p-4 mb-6 bg-red-500/10 border border-red-500/20">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass rounded-xl p-6">
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-2xl font-bold gradient-text">
                  Ejercicio {ejercicioActual?.numero}
                </h2>
                <span className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-400 text-sm font-medium">
                  {sesion?.tema}
                </span>
              </div>
            </div>
            
            <div className="bg-gray-800/50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-3">Consigna:</h3>
              <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                {ejercicioActual?.consigna}
              </p>
            </div>
          </div>

          <div className="glass rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Editor de Código</h3>
            
            <div className="border border-gray-700 rounded-xl overflow-hidden mb-4" style={{ height: '400px' }}>
              <Editor
                height="100%"
                defaultLanguage="python"
                theme="vs-dark"
                value={codigo}
                onChange={(value) => setCodigo(value || '')}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 4,
                }}
              />
            </div>

            <div className="flex gap-3 mb-4">
              <button
                onClick={handleSolicitarPista}
                disabled={loadingPista || !sesion || (pistaActual !== null && numeroPistaActual >= pistaActual.total_pistas)}
                className="flex-1 py-2 px-4 rounded-lg bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-yellow-500/30 transition-colors flex items-center justify-center gap-2"
              >
                {loadingPista ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-400"></div>
                    Cargando...
                  </>
                ) : pistaActual !== null && numeroPistaActual >= pistaActual.total_pistas ? (
                  <>
                    <Lightbulb className="w-4 h-4" />
                    Sin más pistas
                  </>
                ) : (
                  <>
                    <Lightbulb className="w-4 h-4" />
                    Pista {numeroPistaActual + 1}
                  </>
                )}
              </button>

              <button
                onClick={handleCorregirConIA}
                disabled={loadingIA || !sesion || !codigo.trim()}
                className="flex-1 py-2 px-4 rounded-lg bg-purple-500/20 text-purple-400 border border-purple-500/30 font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-500/30 transition-colors flex items-center justify-center gap-2"
              >
                {loadingIA ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-400"></div>
                    Analizando...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Corregir con IA
                  </>
                )}
              </button>
            </div>

            {pistaActual && (
              <div className="glass rounded-lg p-4 mb-4 bg-yellow-500/5 border border-yellow-500/20">
                <div className="flex items-start gap-3">
                  <Lightbulb className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-yellow-400 mb-1">
                      Pista {pistaActual.numero + 1} de {pistaActual.total_pistas}
                    </h4>
                    <p className="text-sm text-gray-300">{pistaActual.contenido}</p>
                  </div>
                </div>
              </div>
            )}

            {correccionIA && (
              <div className="glass rounded-lg p-4 mb-4 bg-purple-500/5 border border-purple-500/20">
                <div className="flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-purple-400 mb-2">Análisis de IA</h4>
                    <p className="text-sm text-gray-300 mb-3">{correccionIA.analisis}</p>
                    {correccionIA.sugerencias.length > 0 && (
                      <>
                        <h5 className="text-xs font-semibold text-purple-400 mb-1">Sugerencias:</h5>
                        <ul className="space-y-1">
                          {correccionIA.sugerencias.map((sug, idx) => (
                            <li key={idx} className="text-xs text-gray-400 flex items-start gap-2">
                              <span className="text-purple-400">•</span>
                              <span>{sug}</span>
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={handleSubmitEjercicio}
              disabled={submitting || !codigo.trim()}
              className="w-full py-3 px-6 rounded-xl gradient-bg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Evaluando...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Enviar Ejercicio
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainingExamPage;
