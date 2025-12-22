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
      {/* Header con estadísticas */}
      {stats && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3 text-gray-800">
            <Book className="text-blue-600" size={28} />
            Entrenador Digital
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="text-sm text-gray-600 font-medium mb-1">Total Ejercicios</div>
              <div className="text-3xl font-bold text-gray-800">{stats.total_exercises}</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <div className="text-sm text-green-700 font-medium mb-1">Fácil</div>
              <div className="text-3xl font-bold text-green-700">{stats.by_difficulty.easy || 0}</div>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <div className="text-sm text-yellow-700 font-medium mb-1">Medio</div>
              <div className="text-3xl font-bold text-yellow-700">{stats.by_difficulty.medium || 0}</div>
            </div>
            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <div className="text-sm text-red-700 font-medium mb-1">Difícil</div>
              <div className="text-3xl font-bold text-red-700">{stats.by_difficulty.hard || 0}</div>
            </div>
          </div>
        </div>
      )}

      {/* Filtros y búsqueda */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <div className="flex flex-wrap gap-4">
          {/* Búsqueda */}
          <div className="flex-1 min-w-[250px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Buscar ejercicios..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-gray-700 placeholder-gray-400"
              />
            </div>
          </div>

          {/* Filtro de dificultad */}
          <div className="flex items-center gap-2">
            <Filter size={18} className="text-gray-500" />
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700"
            >
              <option value="">Todas las dificultades</option>
              <option value="easy">Fácil</option>
              <option value="medium">Medio</option>
              <option value="hard">Difícil</option>
            </select>
          </div>

          {/* Filtro de unidad */}
          <div>
            <select
              value={selectedUnit}
              onChange={(e) => setSelectedUnit(e.target.value)}
              className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700"
            >
              <option value="">Todas las unidades</option>
              <option value="U1">Unidad 1 - Fundamentos</option>
              <option value="U2">Unidad 2 - Estructuras</option>
              <option value="U3">Unidad 3 - Funciones</option>
              <option value="U4">Unidad 4 - Archivos</option>
              <option value="U5">Unidad 5 - POO</option>
            </select>
          </div>
        </div>
      </div>

      {/* Lista de ejercicios */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredExercises.length === 0 ? (
          <div className="col-span-full text-center py-16 bg-white rounded-lg shadow-md border border-gray-200">
            <div className="text-6xl mb-4">📚</div>
            <p className="text-xl text-gray-600 font-semibold">No se encontraron ejercicios</p>
            <p className="text-gray-400 mt-2">Intenta con otros filtros</p>
          </div>
        ) : (
          filteredExercises.map((exercise) => (
            <div
              key={exercise.id}
              onClick={() => handleExerciseClick(exercise.id)}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-all cursor-pointer border border-gray-200 hover:border-blue-400 overflow-hidden"
            >
              {/* Header */}
              <div className={`p-4 ${
                exercise.difficulty === 'Easy' ? 'bg-green-50 border-b border-green-200' :
                exercise.difficulty === 'Medium' ? 'bg-yellow-50 border-b border-yellow-200' :
                'bg-red-50 border-b border-red-200'
              }`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {exercise.is_completed ? (
                        <CheckCircle className="text-green-600" size={20} />
                      ) : (
                        <Circle className="text-gray-400" size={20} />
                      )}
                      <h3 className="font-bold text-lg text-gray-800">{exercise.title}</h3>
                    </div>
                    <span className="text-xs text-gray-500 font-mono">{exercise.id}</span>
                  </div>
                  <span className={`px-3 py-1 rounded-md text-xs font-semibold ${
                    exercise.difficulty === 'Easy' ? 'bg-green-200 text-green-800' :
                    exercise.difficulty === 'Medium' ? 'bg-yellow-200 text-yellow-800' :
                    'bg-red-200 text-red-800'
                  }`}>
                    {getDifficultyLabel(exercise.difficulty)}
                  </span>
                </div>
              </div>

              {/* Body */}
              <div className="p-4 space-y-3">
                {/* Métricas */}
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <Clock size={16} className="text-gray-500" />
                    <span>{exercise.estimated_time_minutes} min</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Award size={16} className="text-gray-500" />
                    <span>{exercise.points} pts</span>
                  </div>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-2">
                  {exercise.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded border border-blue-200"
                    >
                      {tag}
                    </span>
                  ))}
                  {exercise.tags.length > 3 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded border border-gray-200">
                      +{exercise.tags.length - 3}
                    </span>
                  )}
                </div>
              </div>

              {/* Footer */}
              <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition-colors">
                  {exercise.is_completed ? 'Reintentar' : 'Comenzar'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
