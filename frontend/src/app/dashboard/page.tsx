'use client';

/**
 * Main dashboard page with interactive metrics and charts.
 *
 * Główna strona dashboardu z interaktywnymi metrykami i wykresami.
 */

import { useAuth, withAuth } from '@/contexts/AuthContext';
import { getRoleDisplayName, getRoleBadgeColor, hasPermission } from '@/lib/auth';
import MetricsDashboard from '@/components/dashboard/MetricsDashboard';
import { useRouter } from 'next/navigation';

function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();

  if (!user) return null;

  const handleLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Forglass Regenerator Optimizer
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">{user.full_name || user.username}</span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                  {getRoleDisplayName(user.role)}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Wyloguj
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="mb-8 text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Witaj, {user.full_name || user.username}!
            </h2>
            <p className="text-lg text-gray-600">
              System optymalizacji regeneratorów pieców szklarskich
            </p>
          </div>

          {/* Interactive Metrics Dashboard */}
          <MetricsDashboard />

          {/* Quick Navigation Cards */}
          <div className="mt-12 mb-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">Quick Access</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Import Data */}
              <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200 hover:shadow-xl transition-shadow">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="p-3 bg-blue-50 rounded-md">
                        <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <h4 className="text-lg font-medium text-gray-900">
                        Import danych
                      </h4>
                      <p className="text-sm text-gray-500">
                        Pliki XLSX z konfiguracjami regeneratorów
                      </p>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-6 py-3">
                  <div className="text-sm">
                    <a
                      href="/import"
                      className={`font-medium ${
                        hasPermission(user, 'engineer')
                          ? 'text-blue-600 hover:text-blue-500'
                          : 'text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      Importuj dane →
                    </a>
                  </div>
                </div>
              </div>

              {/* Optimization */}
              <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200 hover:shadow-xl transition-shadow">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="p-3 bg-green-50 rounded-md">
                        <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <h4 className="text-lg font-medium text-gray-900">
                        Optymalizacja
                      </h4>
                      <p className="text-sm text-gray-500">
                        Scenariusze optymalizacji SLSQP
                      </p>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-6 py-3">
                  <div className="text-sm">
                    <a
                      href="/optimize"
                      className={`font-medium ${
                        hasPermission(user, 'engineer')
                          ? 'text-green-600 hover:text-green-500'
                          : 'text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      Utwórz scenariusz →
                    </a>
                  </div>
                </div>
              </div>

              {/* 3D Visualization */}
              <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200 hover:shadow-xl transition-shadow">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="p-3 bg-purple-50 rounded-md">
                        <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <h4 className="text-lg font-medium text-gray-900">
                        Wizualizacja 3D
                      </h4>
                      <p className="text-sm text-gray-500">
                        Interaktywny konfigurator regeneratorów
                      </p>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-6 py-3">
                  <div className="text-sm">
                    <a
                      href="/3d-demo"
                      className="font-medium text-purple-600 hover:text-purple-500"
                    >
                      Otwórz konfigurator →
                    </a>
                  </div>
                </div>
              </div>

              {/* Reports */}
              <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200 hover:shadow-xl transition-shadow">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="p-3 bg-orange-50 rounded-md">
                        <svg className="h-6 w-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <h4 className="text-lg font-medium text-gray-900">
                        Raporty
                      </h4>
                      <p className="text-sm text-gray-500">
                        PDF & XLSX z analizami wyników
                      </p>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-6 py-3">
                  <div className="text-sm">
                    <a
                      href="/reports"
                      className="font-medium text-orange-600 hover:text-orange-500"
                    >
                      Przeglądaj raporty →
                    </a>
                  </div>
                </div>
              </div>

              {/* Materials Database */}
              <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200 hover:shadow-xl transition-shadow">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="p-3 bg-indigo-50 rounded-md">
                        <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <h4 className="text-lg font-medium text-gray-900">
                        Baza materiałów
                      </h4>
                      <p className="text-sm text-gray-500">
                        103 materiały z właściwościami termicznymi
                      </p>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-6 py-3">
                  <div className="text-sm">
                    <button
                      onClick={() => router.push('/materials')}
                      className="font-medium text-indigo-600 hover:text-indigo-500 transition-colors cursor-pointer"
                    >
                      Zarządzaj materiałami →
                    </button>
                  </div>
                </div>
              </div>

              {/* Admin Panel */}
              {hasPermission(user, 'admin') && (
                <div className="bg-white overflow-hidden shadow-lg rounded-lg border border-red-200 hover:shadow-xl transition-shadow">
                  <div className="p-6">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="p-3 bg-red-50 rounded-md">
                          <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                          </svg>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <h4 className="text-lg font-medium text-gray-900">
                          Panel administratora
                        </h4>
                        <p className="text-sm text-gray-500">
                          Zarządzanie systemem i użytkownikami
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 px-6 py-3">
                    <div className="text-sm">
                      <button className="font-medium text-red-600 hover:text-red-500">
                        Panel admina →
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-500">
            Forglass Regenerator Optimizer v1.0.0 • Forglass Engineering Team • 2025
          </div>
        </div>
      </footer>
    </div>
  );
}

export default withAuth(DashboardPage);