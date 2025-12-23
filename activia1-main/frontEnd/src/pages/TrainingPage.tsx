import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  GraduationCap, 
  Clock, 
  TrendingUp, 
  PlayCircle,
  AlertCircle,
  Sparkles
} from 'lucide-react';
import { trainingService, MateriaInfo, TemaInfo } from '../services/api';

/**
 * TrainingPage - Página de selección de materia y tema
 * 
 * Permite al usuario:
 * - Ver materias disponibles (por ahora solo Programación 1)
 * - Seleccionar un tema de la materia
 * - Ver información del tema (dificultad, tiempo estimado)
 * - Iniciar el entrenamiento tipo examen
 */

const TrainingPage: React.FC = () => {
  const navigate = useNavigate();
  
  const [materias, setMaterias] = useState<MateriaInfo[]>([]);
  const [materiaSeleccionada, setMateriaSeleccionada] = useState<MateriaInfo | null>(null);
  const [temaSeleccionado, setTemaSeleccionado] = useState<TemaInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar materias al montar el componente
  useEffect(() => {
    loadMaterias();
  }, []);

  const loadMaterias = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔄 Cargando materias desde:', '/api/v1/training/materias');
      const data = await trainingService.getMaterias();
      console.log('✅ Materias cargadas:', data);
      console.log('🔧 Limpiando selección de materia (debe estar en null)');
      setMaterias(data);
      setMateriaSeleccionada(null); // Limpiar selección para forzar elección del usuario
      setTemaSeleccionado(null); // También limpiar tema
      console.log('✅ Materia seleccionada después de limpiar:', null);

      // NO auto-seleccionar materia - el usuario debe elegir del combo
      if (data.length === 0) {
        console.warn('⚠️ No hay materias disponibles');
        setError('No hay materias disponibles en este momento');
      }
    } catch (err: any) {
      console.error('❌ Error cargando materias:', err);
      console.error('Detalles del error:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
      
      let errorMsg = 'Error al cargar las materias disponibles. ';
      if (err.response?.status === 404) {
        errorMsg += 'Endpoint no encontrado. Verifica que el backend esté corriendo.';
      } else if (err.response?.status === 401) {
        errorMsg += 'No autorizado. Por favor inicia sesión nuevamente.';
      } else if (err.message.includes('Network Error')) {
        errorMsg += 'No se puede conectar al backend. Verifica que esté corriendo en http://localhost:8000';
      } else {
        errorMsg += err.message;
      }
      
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleIniciarEntrenamiento = async (tema: TemaInfo) => {
    if (!materiaSeleccionada) {
      return;
    }

    try {
      // Navegar a la página de examen con los datos
      navigate('/training/exam', {
        state: {
          materia_codigo: materiaSeleccionada.codigo,
          tema_id: tema.id
        }
      });
    } catch (err) {
      console.error('Error iniciando entrenamiento:', err);
      setError('Error al iniciar el entrenamiento');
    }
  };

  const getDifficultyColor = (dificultad: string): string => {
    const lower = dificultad.toLowerCase();
    if (lower.includes('fácil') || lower.includes('muy fácil')) {
      return 'bg-green-500/10 text-green-400 border-green-500/30';
    }
    if (lower.includes('media') || lower.includes('intermedia')) {
      return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30';
    }
    if (lower.includes('difícil') || lower.includes('avanzada')) {
      return 'bg-red-500/10 text-red-400 border-red-500/30';
    }
    return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-purple-500 mb-6"></div>
          <p className="text-white text-xl font-bold mb-2">Cargando materias...</p>
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
              <p className="text-gray-400 mt-1">Modo Examen - Elige tu tema y demuestra tus habilidades</p>
            </div>
          </div>
          
          {/* Info banner */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-300">
              <p className="font-medium mb-1">💡 ¿Cómo funciona?</p>
              <p className="text-blue-400/80">
                1. Selecciona un tema • 2. El examen tiene tiempo límite • 3. Puedes pedir hasta 4 pistas (reducen tu nota) • 4. Recibe feedback instantáneo con IA
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

        {/* Selector de Materia (Combo Dropdown) */}
        {materias.length > 0 && (
          <div className="mb-8">
            <div className="glass rounded-2xl p-6">
              <label className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-purple-400" />
                Selecciona una Materia
              </label>
              <select
                value={materiaSeleccionada?.codigo || ''}
                onChange={(e) => {
                  const selected = materias.find(m => m.codigo === e.target.value);
                  setMateriaSeleccionada(selected || null);
                  setTemaSeleccionado(null); // Resetear tema cuando cambia materia
                  console.log('📚 Materia seleccionada:', selected?.materia);
                }}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all cursor-pointer hover:bg-gray-800/70"
              >
                <option value="" className="bg-gray-800">Elige una materia...</option>
                {materias.map((materia) => (
                  <option key={materia.codigo} value={materia.codigo} className="bg-gray-800">
                    {materia.materia} ({materia.temas.length} ejercicios)
                  </option>
                ))}
              </select>

              {/* Info de materia seleccionada */}
              {materiaSeleccionada && (
                <div className="mt-4 p-4 bg-purple-500/10 border border-purple-500/30 rounded-xl">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-white">{materiaSeleccionada.materia}</h3>
                      <p className="text-sm text-gray-400">Código: <span className="text-purple-400 font-mono">{materiaSeleccionada.codigo}</span></p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-purple-400">{materiaSeleccionada.temas.length}</p>
                      <p className="text-xs text-gray-400">Ejercicios</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Grid de temas */}
        {materiaSeleccionada && (
          <div>
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-400" />
              Selecciona un Tema
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {materiaSeleccionada.temas.map((tema) => (
                <div
                  key={tema.id}
                  onClick={() => setTemaSeleccionado(tema)}
                  className={`glass rounded-xl p-6 cursor-pointer transition-all hover:scale-[1.02] flex flex-col ${
                    temaSeleccionado?.id === tema.id
                      ? 'ring-2 ring-purple-500 bg-purple-500/10'
                      : 'hover:bg-gray-800/50'
                  }`}
                >
                  {/* Título del tema */}
                  <h4 className="text-lg font-bold text-white mb-2">{tema.nombre}</h4>

                  {/* Descripción */}
                  <p className="text-gray-400 text-sm mb-4 flex-grow">{tema.descripcion}</p>

                  {/* Metadata */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className={`px-3 py-1 rounded-lg text-xs font-medium border ${getDifficultyColor(tema.dificultad)}`}>
                      {tema.dificultad}
                    </span>
                    <span className="px-3 py-1 rounded-lg text-xs font-medium bg-gray-700/50 text-gray-300 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {tema.tiempo_estimado_min} min
                    </span>
                  </div>

                  {/* Botón de Iniciar - SOLO si está seleccionado */}
                  {temaSeleccionado?.id === tema.id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation(); // Evitar que se dispare el onClick de la card
                        handleIniciarEntrenamiento(tema);
                      }}
                      className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg font-bold text-white flex items-center justify-center gap-2 hover:scale-105 transition-transform shadow-lg shadow-purple-500/30 mt-2"
                    >
                      <PlayCircle className="w-5 h-5" />
                      Iniciar Entrenamiento
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mensaje si no hay temas */}
        {materiaSeleccionada && materiaSeleccionada.temas.length === 0 && (
          <div className="text-center py-12">
            <TrendingUp className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No hay temas disponibles en esta materia</p>
          </div>
        )}
        
        {/* Mensaje si no hay materias */}
        {!loading && !error && materias.length === 0 && (
          <div className="glass rounded-2xl p-12 text-center">
            <AlertCircle className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">No hay materias disponibles</h3>
            <p className="text-gray-400 mb-6">El sistema no pudo cargar las materias. Por favor verifica:</p>
            <div className="bg-gray-800/50 rounded-xl p-4 text-left space-y-2 mb-6">
              <p className="text-sm text-gray-300">✓ Backend corriendo en <code className="text-purple-400">http://localhost:8000</code></p>
              <p className="text-sm text-gray-300">✓ Archivo <code className="text-purple-400">programacion1_temas.json</code> existe</p>
              <p className="text-sm text-gray-300">✓ Revisa la consola del navegador (F12) para más detalles</p>
            </div>
            <button
              onClick={loadMaterias}
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
