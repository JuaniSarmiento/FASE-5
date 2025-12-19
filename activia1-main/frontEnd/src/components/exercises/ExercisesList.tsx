/**
 * ExercisesList Component
 * Muestra el listado de ejercicios disponibles con filtros
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Book, 
  Clock, 
  Award, 
  Filter,
  Search,
  CheckCircle,
  Circle
} from 'lucide-react';
import { exercisesService, ExerciseListItem, ExerciseStats } from '@/services/api/exercises.service';

interface ExercisesListProps {
  onSelectExercise?: (exerciseId: string) => void;
}

export const ExercisesList: React.FC<ExercisesListProps> = ({ onSelectExercise }) => {
  const navigate = useNavigate();
  const [exercises, setExercises] = useState<ExerciseListItem[]>([]);
  const [stats, setStats] = useState<ExerciseStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filtros
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('');
  const [selectedUnit, setSelectedUnit] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadExercises();
    loadStats();
  }, [selectedDifficulty, selectedUnit]);

  const loadExercises = async () => {
    try {
      setLoading(true);
      const data = await exercisesService.listJSON({
        difficulty: selectedDifficulty || undefined,
        unit: selectedUnit || undefined,
      });
      setExercises(data);
      setError(null);
    } catch (err) {
      setError('Error al cargar ejercicios');
      console.error('Error loading exercises:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await exercisesService.getJSONStats();
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const handleExerciseClick = (exerciseId: string) => {
    if (onSelectExercise) {
      onSelectExercise(exerciseId);
    } else {
      navigate(`/exercises/${exerciseId}`);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'hard':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getDifficultyLabel = (difficulty: string) => {
    const labels: Record<string, string> = {
      easy: 'Fácil',
      medium: 'Medio',
      hard: 'Difícil',
    };
    return labels[difficulty.toLowerCase()] || difficulty;
  };

  // Filtrar por búsqueda
  const filteredExercises = exercises?.filter(ex =>
    ex.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ex.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  ) || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con estadísticas y gradiente */}
      {stats && (
        <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-2xl shadow-2xl p-8 text-white">
          <h2 className="text-4xl font-bold mb-6 flex items-center gap-3">
            <span className="text-5xl">💻</span> Entrenador Digital
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-5 border border-white/30 hover:bg-white/30 transition-all">
              <div className="text-sm text-indigo-100 font-semibold mb-1">Total Ejercicios</div>
              <div className="text-4xl font-bold">{stats.total_exercises}</div>
            </div>
            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-5 border border-white/30 hover:bg-white/30 transition-all">
              <div className="text-sm text-green-100 font-semibold mb-1">⭐ Fácil</div>
              <div className="text-4xl font-bold">{stats.by_difficulty.easy || 0}</div>
            </div>
            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-5 border border-white/30 hover:bg-white/30 transition-all">
              <div className="text-sm text-yellow-100 font-semibold mb-1">⭐⭐ Medio</div>
              <div className="text-4xl font-bold">{stats.by_difficulty.medium || 0}</div>
            </div>
            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-5 border border-white/30 hover:bg-white/30 transition-all">
              <div className="text-sm text-red-100 font-semibold mb-1">⭐⭐⭐ Difícil</div>
              <div className="text-4xl font-bold">{stats.by_difficulty.hard || 0}</div>
            </div>
          </div>
        </div>
      )}

      {/* Filtros y búsqueda con mejor diseño */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-indigo-100">
        <div className="flex flex-wrap gap-4">
          {/* Búsqueda */}
          <div className="flex-1 min-w-[250px]">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-indigo-400" size={22} />
              <input
                type="text"
                placeholder="🔍 Buscar ejercicios por nombre o tema..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border-2 border-indigo-200 rounded-xl focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 transition-all text-gray-700 placeholder-gray-400"
              />
            </div>
          </div>

          {/* Filtro de dificultad */}
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-2 rounded-lg">
              <Filter size={20} className="text-white" />
            </div>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="border-2 border-indigo-200 rounded-xl px-5 py-3 focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 font-semibold text-gray-700"
            >
              <option value="">Todas las dificultades</option>
              <option value="easy">⭐ Fácil</option>
              <option value="medium">⭐⭐ Medio</option>
              <option value="hard">⭐⭐⭐ Difícil</option>
            </select>
          </div>

          {/* Filtro de unidad */}
          <div>
            <select
              value={selectedUnit}
              onChange={(e) => setSelectedUnit(e.target.value)}
              className="border-2 border-indigo-200 rounded-xl px-5 py-3 focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 font-semibold text-gray-700"
            >
              <option value="">📚 Todas las unidades</option>
              <option value="U1">📖 Unidad 1 - Fundamentos</option>
              <option value="U2">🏗️ Unidad 2 - Estructuras</option>
              <option value="U3">⚙️ Unidad 3 - Funciones</option>
              <option value="U4">📁 Unidad 4 - Archivos</option>
              <option value="U5">🎨 Unidad 5 - POO</option>
            </select>
          </div>
        </div>
      </div>

      {/* Lista de ejercicios con cards mejoradas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredExercises.length === 0 ? (
          <div className="col-span-full text-center py-16 bg-white rounded-xl shadow-lg">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-xl text-gray-500 font-semibold">No se encontraron ejercicios</p>
            <p className="text-gray-400 mt-2">Intenta con otros filtros</p>
          </div>
        ) : (
          filteredExercises.map((exercise) => (
            <div
              key={exercise.id}
              onClick={() => handleExerciseClick(exercise.id)}
              className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all cursor-pointer border-2 border-transparent hover:border-indigo-300 overflow-hidden group transform hover:scale-105 duration-300"
            >
              {/* Header con gradiente */}
              <div className={`p-5 bg-gradient-to-r ${
                exercise.difficulty === 'Easy' ? 'from-green-400 to-emerald-500' :
                exercise.difficulty === 'Medium' ? 'from-yellow-400 to-orange-500' :
                'from-red-400 to-pink-500'
              } text-white`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {exercise.is_completed ? (
                        <div className="bg-white/30 p-1 rounded-full">
                          <CheckCircle className="text-white" size={22} />
                        </div>
                      ) : (
                        <div className="bg-white/20 p-1 rounded-full">
                          <Circle className="text-white/70" size={22} />
                        </div>
                      )}
                      <h3 className="font-bold text-xl">{exercise.title}</h3>
                    </div>
                    <span className="text-xs text-white/80 font-mono bg-white/20 px-2 py-1 rounded">{exercise.id}</span>
                  </div>
                  <span className="px-4 py-2 rounded-xl text-sm font-bold bg-white/30 backdrop-blur-sm border border-white/40">
                    {exercise.difficulty === 'Easy' ? '⭐ Fácil' :
                     exercise.difficulty === 'Medium' ? '⭐⭐ Medio' : '⭐⭐⭐ Difícil'}
                  </span>
                </div>
              </div>

              {/* Body */}
              <div className="p-5 space-y-4">
                {/* Métricas con iconos mejorados */}
                <div className="flex items-center gap-4 text-sm font-semibold text-gray-600">
                  <div className="flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-lg">
                    <Clock size={18} className="text-blue-600" />
                    <span>{exercise.estimated_time_minutes} min</span>
                  </div>
                  <div className="flex items-center gap-2 bg-purple-50 px-3 py-2 rounded-lg">
                    <Award size={18} className="text-purple-600" />
                    <span>{exercise.points} XP</span>
                  </div>
                </div>

                {/* Tags con mejor diseño */}
                <div className="flex flex-wrap gap-2">
                  {exercise.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1.5 bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 text-xs font-semibold rounded-lg border border-indigo-200"
                    >
                      #{tag}
                    </span>
                  ))}
                  {exercise.tags.length > 3 && (
                    <span className="px-3 py-1.5 bg-gray-100 text-gray-600 text-xs font-semibold rounded-lg border border-gray-200">
                      +{exercise.tags.length - 3} más
                    </span>
                  )}
                </div>
              </div>

              {/* Footer con botón llamativo */}
              <div className="px-5 py-4 bg-gradient-to-r from-gray-50 to-indigo-50/30 border-t-2 border-indigo-100">
                <button className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-3 rounded-xl transition-all shadow-md hover:shadow-lg transform group-hover:scale-105">
                  🚀 {exercise.is_completed ? 'Reintentar' : 'Comenzar'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
