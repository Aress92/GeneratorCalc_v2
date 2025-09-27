'use client';

/**
 * Optimization scenarios page - Module 2 MVP implementation.
 *
 * Strona scenariuszy optymalizacji - implementacja MVP modułu 2.
 */

import { useState, useEffect } from 'react';
import { useAuth, withAuth } from '@/contexts/AuthContext';
import { hasPermission } from '@/lib/auth';
import { OptimizationAPI } from '@/lib/api-client';

interface OptimizationScenario {
  id: string;
  name: string;
  description?: string;
  scenario_type: string;
  base_configuration_id: string;
  objective: string;
  algorithm: string;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface OptimizationJob {
  id: string;
  scenario_id: string;
  job_name?: string;
  status: string;
  progress_percentage: number;
  current_iteration: number;
  started_at?: string;
  completed_at?: string;
  runtime_seconds?: number;
  error_message?: string;
  created_at: string;
}

function OptimizePage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'scenarios' | 'jobs' | 'results'>('scenarios');
  const [scenarios, setScenarios] = useState<OptimizationScenario[]>([]);
  const [jobs, setJobs] = useState<OptimizationJob[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateScenario, setShowCreateScenario] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState<OptimizationScenario | null>(null);

  // New scenario form state
  const [newScenario, setNewScenario] = useState({
    name: '',
    description: '',
    scenario_type: 'geometry_optimization',
    base_configuration_id: '',
    objective: 'minimize_fuel_consumption',
    algorithm: 'slsqp',
    max_iterations: 1000,
    tolerance: 0.000001,
    max_runtime_minutes: 120,
    design_variables: {
      checker_height: {
        name: 'checker_height',
        description: 'Wysokość cegieł checker',
        unit: 'm',
        min_value: 0.3,
        max_value: 2.0,
        baseline_value: 0.5,
        variable_type: 'continuous'
      },
      checker_spacing: {
        name: 'checker_spacing',
        description: 'Odstęp między cegłami',
        unit: 'm',
        min_value: 0.05,
        max_value: 0.3,
        baseline_value: 0.1,
        variable_type: 'continuous'
      },
      wall_thickness: {
        name: 'wall_thickness',
        description: 'Grubość ściany',
        unit: 'm',
        min_value: 0.2,
        max_value: 0.8,
        baseline_value: 0.3,
        variable_type: 'continuous'
      }
    }
  });

  useEffect(() => {
    if (user && hasPermission(user, 'engineer')) {
      if (activeTab === 'scenarios') {
        loadScenarios();
      } else if (activeTab === 'jobs') {
        loadJobs();
      }
    }
  }, [activeTab, user]);

  if (!user || !hasPermission(user, 'engineer')) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Brak uprawnień</h2>
          <p className="text-gray-600">Nie masz uprawnień do optymalizacji regeneratorów.</p>
        </div>
      </div>
    );
  }

  const loadScenarios = async () => {
    setIsLoading(true);
    try {
      const data = await OptimizationAPI.getScenarios();
      setScenarios(data.scenarios || []);
    } catch (error) {
      console.error('Failed to load scenarios:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadJobs = async () => {
    setIsLoading(true);
    try {
      // Note: This endpoint needs to be implemented or use a different approach
      // For now, we'll show empty jobs or load from a scenario
      setJobs([]);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createScenario = async () => {
    setIsLoading(true);
    try {
      await OptimizationAPI.createScenario(newScenario);
      await loadScenarios();
      setShowCreateScenario(false);
      setNewScenario({
        ...newScenario,
        name: '',
        description: ''
      });
    } catch (error) {
      console.error('Failed to create scenario:', error);
      alert('Nie udało się utworzyć scenariusza');
    } finally {
      setIsLoading(false);
    }
  };

  const startOptimization = async (scenarioId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/optimize/scenarios/${scenarioId}/jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          job_name: `Optymalizacja ${new Date().toLocaleString()}`,
          initial_values: {}
        })
      });

      if (response.ok) {
        setActiveTab('jobs');
        await loadJobs();
      } else {
        const error = await response.json();
        alert(`Błąd: ${error.detail}`);
      }
    } catch (error) {
      console.error('Failed to start optimization:', error);
      alert('Nie udało się rozpocząć optymalizacji');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'Zakończono';
      case 'running': return 'W trakcie';
      case 'failed': return 'Błąd';
      case 'pending': return 'Oczekuje';
      case 'cancelled': return 'Anulowano';
      default: return status;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-3xl font-bold text-gray-900">Optymalizacja Regeneratorów</h1>
            <p className="mt-2 text-gray-600">Zarządzaj scenariuszami optymalizacji i monitoruj postęp zadań</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('scenarios')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'scenarios'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Scenariusze
            </button>
            <button
              onClick={() => setActiveTab('jobs')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'jobs'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Zadania
            </button>
            <button
              onClick={() => setActiveTab('results')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'results'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Wyniki
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'scenarios' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Scenariusze Optymalizacji</h2>
              <button
                onClick={() => setShowCreateScenario(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                disabled={isLoading}
              >
                Nowy Scenariusz
              </button>
            </div>

            {isLoading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Ładowanie scenariuszy...</p>
              </div>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {scenarios.map((scenario) => (
                  <div key={scenario.id} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">{scenario.name}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(scenario.status)}`}>
                        {getStatusText(scenario.status)}
                      </span>
                    </div>

                    <p className="text-gray-600 text-sm mb-4">{scenario.description || 'Brak opisu'}</p>

                    <div className="space-y-2 text-sm text-gray-500">
                      <div>Typ: <span className="font-medium">{scenario.scenario_type}</span></div>
                      <div>Cel: <span className="font-medium">{scenario.objective}</span></div>
                      <div>Algorytm: <span className="font-medium">{scenario.algorithm.toUpperCase()}</span></div>
                      <div>Utworzono: <span className="font-medium">{new Date(scenario.created_at).toLocaleDateString()}</span></div>
                    </div>

                    <div className="flex space-x-2 mt-4">
                      <button
                        onClick={() => startOptimization(scenario.id)}
                        className="flex-1 bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 transition-colors"
                        disabled={isLoading}
                      >
                        Uruchom
                      </button>
                      <button
                        onClick={() => setSelectedScenario(scenario)}
                        className="flex-1 bg-gray-600 text-white px-3 py-2 rounded text-sm hover:bg-gray-700 transition-colors"
                      >
                        Szczegóły
                      </button>
                    </div>
                  </div>
                ))}

                {scenarios.length === 0 && !isLoading && (
                  <div className="col-span-full text-center py-12">
                    <p className="text-gray-500 text-lg">Brak scenariuszy optymalizacji</p>
                    <p className="text-gray-400 mt-2">Utwórz pierwszy scenariusz aby rozpocząć</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'jobs' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Zadania Optymalizacji</h2>

            {isLoading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Ładowanie zadań...</p>
              </div>
            ) : (
              <div className="bg-white shadow-md rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Nazwa
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Postęp
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Czas
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Akcje
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {jobs.map((job) => (
                      <tr key={job.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {job.job_name || `Zadanie ${job.id.slice(-8)}`}
                          </div>
                          <div className="text-sm text-gray-500">
                            Iteracja {job.current_iteration}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(job.status)}`}>
                            {getStatusText(job.status)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${job.progress_percentage}%` }}
                            ></div>
                          </div>
                          <div className="text-sm text-gray-500 mt-1">
                            {job.progress_percentage.toFixed(1)}%
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {job.runtime_seconds
                            ? `${Math.round(job.runtime_seconds / 60)} min`
                            : job.started_at
                              ? `${Math.round((new Date().getTime() - new Date(job.started_at).getTime()) / 60000)} min`
                              : '-'
                          }
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button className="text-blue-600 hover:text-blue-900 mr-3">
                            Zobacz
                          </button>
                          {job.status === 'running' && (
                            <button className="text-red-600 hover:text-red-900">
                              Anuluj
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {jobs.length === 0 && (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">Brak zadań optymalizacji</p>
                    <p className="text-gray-400 mt-2">Uruchom scenariusz aby rozpocząć optymalizację</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'results' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Wyniki Optymalizacji</h2>
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">Wyniki będą dostępne po zakończeniu optymalizacji</p>
              <p className="text-gray-400 mt-2">Uruchom zadanie optymalizacji aby zobaczyć wyniki</p>
            </div>
          </div>
        )}
      </div>

      {/* Create Scenario Modal */}
      {showCreateScenario && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-full overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Nowy Scenariusz Optymalizacji</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nazwa</label>
                <input
                  type="text"
                  value={newScenario.name}
                  onChange={(e) => setNewScenario({...newScenario, name: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="Nazwa scenariusza"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Opis</label>
                <textarea
                  value={newScenario.description}
                  onChange={(e) => setNewScenario({...newScenario, description: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 h-20"
                  placeholder="Opcjonalny opis scenariusza"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Typ scenariusza</label>
                  <select
                    value={newScenario.scenario_type}
                    onChange={(e) => setNewScenario({...newScenario, scenario_type: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="geometry_optimization">Optymalizacja geometrii</option>
                    <option value="material_optimization">Optymalizacja materiałów</option>
                    <option value="operating_conditions">Warunki pracy</option>
                    <option value="comprehensive">Kompleksowa</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Cel optymalizacji</label>
                  <select
                    value={newScenario.objective}
                    onChange={(e) => setNewScenario({...newScenario, objective: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="minimize_fuel_consumption">Minimalizacja zużycia paliwa</option>
                    <option value="minimize_co2_emissions">Minimalizacja emisji CO₂</option>
                    <option value="maximize_efficiency">Maksymalizacja wydajności</option>
                    <option value="minimize_cost">Minimalizacja kosztów</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Max iteracji</label>
                  <input
                    type="number"
                    value={newScenario.max_iterations}
                    onChange={(e) => setNewScenario({...newScenario, max_iterations: parseInt(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    min="10"
                    max="10000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Tolerancja</label>
                  <input
                    type="number"
                    value={newScenario.tolerance}
                    onChange={(e) => setNewScenario({...newScenario, tolerance: parseFloat(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    step="0.000001"
                    min="0.000001"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Max czas (min)</label>
                  <input
                    type="number"
                    value={newScenario.max_runtime_minutes}
                    onChange={(e) => setNewScenario({...newScenario, max_runtime_minutes: parseInt(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    min="1"
                    max="720"
                  />
                </div>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={createScenario}
                disabled={isLoading || !newScenario.name}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
              >
                {isLoading ? 'Tworzenie...' : 'Utwórz'}
              </button>
              <button
                onClick={() => setShowCreateScenario(false)}
                className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Anuluj
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default withAuth(OptimizePage);