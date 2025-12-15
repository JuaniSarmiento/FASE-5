import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './shared/components/Toast/Toast';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import TutorPage from './pages/TutorPage';
import ExercisesPageNew from './pages/ExercisesPageNew';
import SimulatorsPage from './pages/SimulatorsPage';
import AnalyticsPage from './pages/AnalyticsPage';
// FIX 2.1: Import missing pages (Cortez2 audit)
import EvaluatorPage from './pages/EvaluatorPage';
import RisksPage from './pages/RisksPage';
import GitAnalyticsPage from './pages/GitAnalyticsPage';
import TraceabilityPage from './pages/TraceabilityPage';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ToastProvider>
          <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              {/* FIX 2.8: Add ErrorBoundary to DashboardPage */}
              <Route path="dashboard" element={<ErrorBoundary><DashboardPage /></ErrorBoundary>} />
              {/* Critical pages with markdown rendering wrapped with their own ErrorBoundary */}
              <Route path="tutor" element={<ErrorBoundary><TutorPage /></ErrorBoundary>} />
              <Route path="exercises" element={<ErrorBoundary><ExercisesPageNew /></ErrorBoundary>} />
              <Route path="simulators" element={<ErrorBoundary><SimulatorsPage /></ErrorBoundary>} />
              {/* FIX 2.8: Add ErrorBoundary to AnalyticsPage */}
              <Route path="analytics" element={<ErrorBoundary><AnalyticsPage /></ErrorBoundary>} />
              {/* FIX 2.1: Add missing routes (Cortez2 audit) */}
              <Route path="evaluator" element={<ErrorBoundary><EvaluatorPage /></ErrorBoundary>} />
              <Route path="risks" element={<ErrorBoundary><RisksPage /></ErrorBoundary>} />
              <Route path="git" element={<ErrorBoundary><GitAnalyticsPage /></ErrorBoundary>} />
              <Route path="traceability" element={<ErrorBoundary><TraceabilityPage /></ErrorBoundary>} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Routes>
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;