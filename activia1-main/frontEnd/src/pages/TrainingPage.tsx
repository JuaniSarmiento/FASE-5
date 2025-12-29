import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  GraduationCap,
  Clock,
  PlayCircle,
  AlertCircle,
  Sparkles,
  Award
} from 'lucide-react';
import { trainingService, type LenguajeInfo, type LeccionInfo } from '../services/api/training.service';

/**
 * TrainingPage - Página de selección de lenguaje, lección y ejercicio
 *
 * Flujo de 3 pasos:
 * 1. Seleccionar Lenguaje (Dropdown)
 * 2. Seleccionar Lección (Dropdown)
 * 3. Seleccionar Ejercicio (Grid de tarjetas)
 */

const TrainingPage: React.FC = () => {
  const navigate = useNavigate();

  const [lenguajes, setLenguajes] = useState<LenguajeInfo[]>([]);
  const [lenguajeSeleccionado, setLenguajeSeleccionado] = useState<LenguajeInfo | null>(null);
  const [leccionSeleccionada, setLeccionSeleccionada] = useState<LeccionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar lenguajes al montar el componente
  useEffect(() => {
    loadLenguajes();
  }, []);

  const loadLenguajes = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔄 Cargando lenguajes desde:', '/api/v1/training/lenguajes');
      const data = await trainingService.getLenguajes();
      console.log('✅ Lenguajes cargados:', data);
      setLenguajes(data);
      setLenguajeSeleccionado(null);
      setLeccionSeleccionada(null);

      if (data.length === 0) {
        console.warn('⚠️ No hay lenguajes disponibles');
        setError('No hay lenguajes disponibles en este momento');
      }
    } catch (err: unknown) {
      console.error('❌ Error cargando lenguajes:', err);

      let errorMsg = 'Error al cargar los lenguajes disponibles. ';
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const response = (err as { response?: { status?: number } }).response;
        if (response?.status === 404) {
          errorMsg += 'Endpoint no encontrado. Verifica que el backend esté corriendo.';
        } else if (response?.status === 401) {
          errorMsg += 'No autorizado. Por favor inicia sesión nuevamente.';
        }
      } else if (err instanceof Error && err.message.includes('Network Error')) {
        errorMsg += 'No se puede conectar al backend. Verifica que esté corriendo en http://localhost:8000';
      } else if (err instanceof Error) {
        errorMsg += err.message;
      }

      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (dificultad: string): string => {
    const lower = dificultad.toLowerCase();
    if (lower.includes('fácil') || lower.includes('facil') || lower.includes('easy')) {
      return 'bg-green-500/10 text-green-400 border-green-500/30';
    }
    if (lower.includes('media') || lower.includes('intermedia') || lower.includes('medium')) {
      return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30';
    }
    if (lower.includes('difícil') || lower.includes('dificil') || lower.includes('avanzada') || lower.includes('hard')) {
      return 'bg-red-500/10 text-red-400 border-red-500/30';
    }
    return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-purple-500 mb-6"></div>
          <p className="text-white text-xl font-bold mb-2">Cargando lenguajes...</p>
          <p className="text-gray-400 text-sm">Conectando con el servidor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-purple-500/10 rounded-xl">
              <GraduationCap className="w-8 h-8 text-purple-400" />
            </div>
            <div>
              <h1 className="text-4xl font-bold gradient-text">Entrenador Digital</h1>
              <p className="text-gray-400 mt-1">Modo Examen - Elige tu lenguaje y lección</p>
            </div>
          </div>

          {/* Info banner */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-300">
              <p className="font-medium mb-1">💡 ¿Cómo funciona?</p>
              <p className="text-blue-400/80">
                1. Selecciona un lenguaje • 2. Elige una lección • 3. El examen tiene tiempo límite • 4. Puedes pedir hasta 4 pistas (reducen tu nota) • 5. Recibe feedback instantáneo con IA
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Selectores de Lenguaje y Lección (con animación) */}
        {lenguajes.length > 0 && (
          <div className={`grid gap-6 mb-8 transition-all duration-500 ${
            lenguajeSeleccionado && lenguajeSeleccionado.lecciones.length > 0
              ? 'grid-cols-1 md:grid-cols-2'
              : 'grid-cols-1'
          }`}>

            {/* Selector de Lenguaje */}
            <div className="glass rounded-2xl p-6 transition-all duration-500">
              <label className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-purple-400" />
                Selecciona un Lenguaje
              </label>
              <select
                value={lenguajeSeleccionado?.language || ''}
                onChange={(e) => {
                  const selected = lenguajes.find(l => l.language === e.target.value);
                  setLenguajeSeleccionado(selected || null);
                  setLeccionSeleccionada(null); // Resetear lección cuando cambia lenguaje
                  console.log('📚 Lenguaje seleccionado:', selected?.nombre_completo);
                }}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all cursor-pointer hover:bg-gray-800/70"
              >
                <option value="" className="bg-gray-800">Elige un lenguaje...</option>
                {lenguajes.map((lenguaje) => (
                  <option key={lenguaje.language} value={lenguaje.language} className="bg-gray-800">
                    {lenguaje.nombre_completo} ({lenguaje.lecciones.length} lecciones)
                  </option>
                ))}
              </select>

              {/* Info de lenguaje seleccionado */}
              {lenguajeSeleccionado && (
                <div className="mt-4 p-4 bg-purple-500/10 border border-purple-500/30 rounded-xl animate-fade-in">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-white">{lenguajeSeleccionado.nombre_completo}</h3>
                      <p className="text-sm text-gray-400">Lenguaje: <span className="text-purple-400 font-mono">{lenguajeSeleccionado.language}</span></p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-purple-400">{lenguajeSeleccionado.lecciones.length}</p>
                      <p className="text-xs text-gray-400">Lecciones</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Selector de Lección (aparece con animación) */}
            {lenguajeSeleccionado && lenguajeSeleccionado.lecciones.length > 0 && (
              <div className="glass rounded-2xl p-6 animate-slide-in-right">
                <label className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-400" />
                  Selecciona una Lección
                </label>
                <select
                  value={leccionSeleccionada?.id || ''}
                  onChange={(e) => {
                    const selected = lenguajeSeleccionado.lecciones.find(l => l.id === e.target.value);
                    setLeccionSeleccionada(selected || null);
                    console.log('📖 Lección seleccionada:', selected?.nombre);
                  }}
                  className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all cursor-pointer hover:bg-gray-800/70"
                >
                  <option value="" className="bg-gray-800">Elige una lección...</option>
                  {lenguajeSeleccionado.lecciones.map((leccion) => (
                    <option key={leccion.id} value={leccion.id} className="bg-gray-800">
                      {leccion.nombre} ({leccion.ejercicios.length} ejercicios - {leccion.total_puntos} pts)
                    </option>
                  ))}
                </select>

                {/* Info de lección seleccionada */}
                {leccionSeleccionada && (
                  <div className="mt-4 p-4 bg-purple-500/10 border border-purple-500/30 rounded-xl animate-fade-in">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-bold text-white">{leccionSeleccionada.nombre}</h3>
                        <p className="text-sm text-gray-400">{leccionSeleccionada.descripcion}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-purple-400">{leccionSeleccionada.ejercicios.length}</p>
                        <p className="text-xs text-gray-400">Ejercicios</p>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-3">
                      <span className={`px-3 py-1 rounded-lg text-xs font-medium border ${getDifficultyColor(leccionSeleccionada.dificultad)}`}>
                        {leccionSeleccionada.dificultad}
                      </span>
                      <span className="px-3 py-1 rounded-lg text-xs font-medium bg-yellow-700/30 text-yellow-300 flex items-center gap-1">
                        <Award className="w-3 h-3" />
                        {leccionSeleccionada.total_puntos} pts totales
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Grid de Ejercicios Individuales */}
        {leccionSeleccionada && (
          <div>
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-purple-400" />
              Ejercicios Disponibles
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {leccionSeleccionada.ejercicios.sort((a, b) => a.id.localeCompare(b.id)).map((ejercicio) => (
                <div
                  key={ejercicio.id}
                  className="glass rounded-xl p-5 flex flex-col hover:bg-gray-800/50 transition-all"
                >
                  {/* Título del ejercicio */}
                  <h4 className="text-lg font-bold text-white mb-2">{ejercicio.titulo}</h4>

                  {/* Metadata del ejercicio */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className={`px-2 py-1 rounded-lg text-xs font-medium border ${getDifficultyColor(ejercicio.dificultad)}`}>
                      {ejercicio.dificultad}
                    </span>
                    <span className="px-2 py-1 rounded-lg text-xs font-medium bg-gray-700/50 text-gray-300 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {ejercicio.tiempo_estimado_min} min
                    </span>
                    <span className="px-2 py-1 rounded-lg text-xs font-medium bg-yellow-700/30 text-yellow-300 flex items-center gap-1">
                      <Award className="w-3 h-3" />
                      {ejercicio.puntos} pts
                    </span>
                  </div>

                  {/* Botón Iniciar */}
                  <button
                    onClick={() => {
                      // Navegar al examen con este ejercicio específico
                      navigate('/training/exam', {
                        state: {
                          language: lenguajeSeleccionado!.language,
                          unit_number: leccionSeleccionada.unit_number,
                          leccion_nombre: leccionSeleccionada.nombre,
                          exercise_id: ejercicio.id  // Pasar el ID del ejercicio específico
                        }
                      });
                    }}
                    className="w-full px-4 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg font-bold text-white flex items-center justify-center gap-2 hover:scale-105 transition-transform shadow-lg shadow-purple-500/30 mt-auto"
                  >
                    <PlayCircle className="w-4 h-4" />
                    Iniciar
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mensaje si no hay lecciones */}
        {lenguajeSeleccionado && lenguajeSeleccionado.lecciones.length === 0 && (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No hay lecciones disponibles en este lenguaje</p>
          </div>
        )}

        {/* Mensaje si no hay lenguajes */}
        {!loading && !error && lenguajes.length === 0 && (
          <div className="glass rounded-2xl p-12 text-center">
            <AlertCircle className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">No hay lenguajes disponibles</h3>
            <p className="text-gray-400 mb-6">El sistema no pudo cargar los lenguajes. Por favor verifica:</p>
            <div className="bg-gray-800/50 rounded-xl p-4 text-left space-y-2 mb-6">
              <p className="text-sm text-gray-300">✓ Backend corriendo en <code className="text-purple-400">http://localhost:8000</code></p>
              <p className="text-sm text-gray-300">✓ Base de datos PostgreSQL con ejercicios cargados</p>
              <p className="text-sm text-gray-300">✓ Revisa la consola del navegador (F12) para más detalles</p>
            </div>
            <button
              onClick={loadLenguajes}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-xl font-bold text-white transition-colors"
            >
              Reintentar
            </button>
          </div>
        )}

      </div>
    </div>
  );
};

export default TrainingPage;
