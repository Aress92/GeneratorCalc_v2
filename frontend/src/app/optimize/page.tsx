'use client';

/**
 * Optimization scenarios page - Module 2 MVP implementation.
 *
 * Strona scenariuszy optymalizacji - implementacja MVP modułu 2.
 */

import { useState, useEffect } from 'react';
import { useAuth, withAuth } from '@/contexts/AuthContext';
import { hasPermission } from '@/lib/auth';
import { OptimizationAPI, RegeneratorsAPI } from '@/lib/api-client';
import type { ScenariosResponse, JobsResponse, OptimizationScenario, OptimizationJob } from '@/types/api';
import ValidationErrorAlert from '@/components/common/ValidationErrorAlert';
import { LoadingOverlay } from '@/components/common/LoadingSpinner';
import OptimizationProgressBar from '@/components/optimization/OptimizationProgressBar';
import OptimizationResults from '@/components/optimization/OptimizationResults';
import ConvergenceChart from '@/components/optimization/ConvergenceChart';
import ScenarioDetailsModal from '@/components/optimization/ScenarioDetailsModal';
import ErrorDisplay from '@/components/common/ErrorDisplay';
// TODO: Re-enable sonner after fixing pnpm installation
// import { toast } from 'sonner';

// Temporary toast fallback until sonner is installed
const toast = {
  success: (msg: string) => console.log('✅', msg),
  error: (msg: string) => console.error('❌', msg),
  warning: (msg: string) => console.warn('⚠️', msg),
  info: (msg: string) => console.info('ℹ️', msg),
};

interface RegeneratorConfig {
  id: string;
  name: string;
  regenerator_type: string;
  status: string;
}

function OptimizePage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'scenarios' | 'jobs' | 'results'>('scenarios');
  const [scenarios, setScenarios] = useState<OptimizationScenario[]>([]);
  const [jobs, setJobs] = useState<OptimizationJob[]>([]);
  const [regeneratorConfigs, setRegeneratorConfigs] = useState<RegeneratorConfig[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateScenario, setShowCreateScenario] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState<OptimizationScenario | null>(null);
  const [selectedJobForResults, setSelectedJobForResults] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Array<{field: string, message: string, type: string}>>([]);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [selectedScenarios, setSelectedScenarios] = useState<Set<string>>(new Set());
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set());
  const [lastError, setLastError] = useState<any>(null);

  // New scenario form state
  const [newScenario, setNewScenario] = useState({
    name: '',
    description: '',
    scenario_type: 'geometry_optimization',
    base_configuration_id: '',
    objective: 'minimize_fuel_consumption',
    algorithm: 'slsqp',
    max_iterations: 1000,
    max_function_evaluations: 5000,  // Added missing field
    tolerance: 0.000001,
    max_runtime_minutes: 120,
    objective_weights: null,  // Added missing field
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

  // Load data when tab changes
  useEffect(() => {
    if (!user || !hasPermission(user, 'engineer')) return;

    if (activeTab === 'scenarios') {
      loadScenarios();
      loadRegeneratorConfigs();
    } else if (activeTab === 'jobs' || activeTab === 'results') {
      loadJobs();
    }
  }, [activeTab]); // ONLY activeTab - no user, no callbacks!

  // Auto-refresh jobs every 5 seconds when on jobs tab
  useEffect(() => {
    if (!user || !hasPermission(user, 'engineer')) return;
    if (activeTab !== 'jobs' || !autoRefreshEnabled) return;

    const hasRunningJobs = jobs.some(job => job.status === 'running' || job.status === 'pending');
    if (!hasRunningJobs) return; // Only refresh if there are active jobs

    const interval = setInterval(() => {
      loadJobs();
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, [activeTab, autoRefreshEnabled, jobs, user]);

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

  const loadRegeneratorConfigs = async () => {
    try {
      const data = await RegeneratorsAPI.getRegenerators();
      // Backend returns array directly, not wrapped in object
      const configs = Array.isArray(data) ? data : [];
      setRegeneratorConfigs(configs);
      // Set default base_configuration_id if available
      if (configs.length > 0 && !newScenario.base_configuration_id) {
        setNewScenario(prev => ({
          ...prev,
          base_configuration_id: configs[0].id
        }));
      }
    } catch (error) {
      console.error('Failed to load regenerator configs:', error);
    }
  };

  const loadScenarios = async () => {
    setIsLoading(true);
    try {
      const data = await OptimizationAPI.getScenarios() as ScenariosResponse;
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
      // Load all jobs for the user
      const data = await OptimizationAPI.getJobs() as JobsResponse;
      setJobs(data.jobs || []);
    } catch (error) {
      console.error('Failed to load jobs:', error);
      setJobs([]);
    } finally {
      setIsLoading(false);
    }
  };

  const createScenario = async () => {
    setIsLoading(true);
    setValidationErrors([]);

    try {
      // Debug: Log the data being sent
      console.log('Creating scenario with data:', JSON.stringify(newScenario, null, 2));

      const response = await OptimizationAPI.createScenario(newScenario);
      console.log('Scenario created successfully:', response);

      toast.success('Scenariusz został utworzony pomyślnie');
      await loadScenarios();
      setShowCreateScenario(false);
      setNewScenario({
        ...newScenario,
        name: '',
        description: ''
      });
    } catch (error: any) {
      console.error('Failed to create scenario:', error);

      // Check if it's a validation error (422) with structured errors
      if (error.status === 422 && error.validationErrors) {
        setValidationErrors(error.validationErrors);
        return; // Don't show alert, show validation errors component instead
      }

      // Fallback to toast for non-validation errors
      toast.error(`Nie udało się utworzyć scenariusza: ${error instanceof Error ? error.message : 'Nieznany błąd'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const startOptimization = async (scenarioId: string) => {
    setIsLoading(true);
    setLastError(null); // Clear previous errors
    try {
      await OptimizationAPI.createJob(scenarioId, {
        job_name: `Optymalizacja ${new Date().toLocaleString()}`,
        initial_values: {}
      });
      toast.success('Zadanie optymalizacji zostało uruchomione');
      setActiveTab('jobs');
      await loadJobs();
    } catch (error: any) {
      console.error('Failed to start optimization:', error);

      // Parse error from API response
      let errorData = error;
      if (error.message) {
        try {
          const parsed = JSON.parse(error.message);
          if (parsed.detail) {
            errorData = parsed.detail;
          }
        } catch {
          // Not JSON, use as-is
        }
      }

      // Store detailed error for display
      setLastError(errorData);

      // Show brief toast notification
      const errorMessage = errorData?.message || error.message || 'Nie udało się rozpocząć optymalizacji';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteScenario = async (scenarioId: string, scenarioName: string) => {
    if (!confirm(`Czy na pewno chcesz usunąć scenariusz "${scenarioName}"?\n\nTa operacja jest nieodwracalna i usunie również wszystkie powiązane zadania optymalizacji.`)) {
      return;
    }

    setIsLoading(true);
    try {
      await OptimizationAPI.deleteScenario(scenarioId);
      await loadScenarios();
      toast.success('Scenariusz został usunięty');
    } catch (error) {
      console.error('Failed to delete scenario:', error);
      toast.error('Nie udało się usunąć scenariusza');
    } finally {
      setIsLoading(false);
    }
  };

  const bulkDeleteScenarios = async () => {
    if (selectedScenarios.size === 0) return;

    const count = selectedScenarios.size;
    if (!confirm(`Czy na pewno chcesz usunąć ${count} scenariusz(y/ów)?\n\nTa operacja jest nieodwracalna i usunie również wszystkie powiązane zadania optymalizacji.`)) {
      return;
    }

    setIsLoading(true);
    try {
      await OptimizationAPI.bulkDeleteScenarios(Array.from(selectedScenarios));
      setSelectedScenarios(new Set());
      await loadScenarios();
      toast.success(`Usunięto ${count} scenariusz(y/ów)`);
    } catch (error) {
      console.error('Failed to bulk delete scenarios:', error);
      toast.error('Nie udało się usunąć scenariuszy');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleScenarioSelection = (scenarioId: string) => {
    const newSelection = new Set(selectedScenarios);
    if (newSelection.has(scenarioId)) {
      newSelection.delete(scenarioId);
    } else {
      newSelection.add(scenarioId);
    }
    setSelectedScenarios(newSelection);
  };

  const toggleAllScenarios = () => {
    if (selectedScenarios.size === scenarios.length) {
      setSelectedScenarios(new Set());
    } else {
      setSelectedScenarios(new Set(scenarios.map(s => s.id)));
    }
  };

  const bulkDeleteJobs = async () => {
    if (selectedJobs.size === 0) return;

    const count = selectedJobs.size;
    if (!confirm(`Czy na pewno chcesz usunąć ${count} zadanie/zadań?\n\nMożna usunąć tylko zakończone zadania (completed, failed, cancelled).`)) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await OptimizationAPI.bulkDeleteJobs(Array.from(selectedJobs)) as { deleted_count: number; skipped_count: number; message: string };
      setSelectedJobs(new Set());
      await loadJobs();

      if (response.skipped_count > 0) {
        toast.warning(`Usunięto ${response.deleted_count} zadanie/zadań. Pominięto ${response.skipped_count} aktywnych zadań.`);
      } else {
        toast.success(`Usunięto ${response.deleted_count} zadanie/zadań`);
      }
    } catch (error) {
      console.error('Failed to bulk delete jobs:', error);
      toast.error('Nie udało się usunąć zadań');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleJobSelection = (jobId: string) => {
    const newSelection = new Set(selectedJobs);
    if (newSelection.has(jobId)) {
      newSelection.delete(jobId);
    } else {
      newSelection.add(jobId);
    }
    setSelectedJobs(newSelection);
  };

  const toggleAllJobs = () => {
    if (selectedJobs.size === jobs.length) {
      setSelectedJobs(new Set());
    } else {
      setSelectedJobs(new Set(jobs.map(j => j.id)));
    }
  };

  const handleCancelJob = async (jobId: string) => {
    if (!confirm('Czy na pewno chcesz anulować to zadanie optymalizacji?')) {
      return;
    }

    try {
      await OptimizationAPI.cancelJobById(jobId);
      toast.success('Zadanie zostało anulowane');
      await loadJobs();
    } catch (error) {
      console.error('Failed to cancel job:', error);
      toast.error('Nie udało się anulować zadania');
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

      {/* Error Display */}
      {lastError && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
          <ErrorDisplay
            error={lastError}
            onRetry={() => {
              setLastError(null);
              // Retry logic based on error type
              if (lastError.scenario_id) {
                startOptimization(lastError.scenario_id);
              }
            }}
            onClose={() => setLastError(null)}
            showRetry={lastError.error_type !== 'PERMISSION_DENIED'}
          />
        </div>
      )}

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative">
        {isLoading && <LoadingOverlay text="Przetwarzanie..." />}
        {activeTab === 'scenarios' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center gap-4">
                <h2 className="text-xl font-semibold text-gray-900">Scenariusze Optymalizacji</h2>
                {scenarios.length > 0 && (
                  <div className="flex items-center gap-2">
                    <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedScenarios.size === scenarios.length && scenarios.length > 0}
                        onChange={toggleAllScenarios}
                        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      Zaznacz wszystkie
                    </label>
                    {selectedScenarios.size > 0 && (
                      <button
                        onClick={bulkDeleteScenarios}
                        className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
                        disabled={isLoading}
                      >
                        Usuń zaznaczone ({selectedScenarios.size})
                      </button>
                    )}
                  </div>
                )}
              </div>
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
                  <div key={scenario.id} className="bg-white rounded-lg shadow-md p-6 relative">
                    <div className="absolute top-4 left-4">
                      <input
                        type="checkbox"
                        checked={selectedScenarios.has(scenario.id)}
                        onChange={() => toggleScenarioSelection(scenario.id)}
                        className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                        onClick={(e) => e.stopPropagation()}
                      />
                    </div>
                    <div className="flex justify-between items-start mb-4 ml-8">
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
                      <button
                        onClick={() => deleteScenario(scenario.id, scenario.name)}
                        className="bg-red-600 text-white px-3 py-2 rounded text-sm hover:bg-red-700 transition-colors"
                        disabled={isLoading}
                        title="Usuń scenariusz"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
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
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center gap-4">
                <h2 className="text-xl font-semibold text-gray-900">Zadania Optymalizacji</h2>
                {jobs.some(job => job.status === 'running' || job.status === 'pending') && autoRefreshEnabled && (
                  <span className="flex items-center text-sm text-green-600">
                    <svg className="w-4 h-4 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Auto-odświeżanie co 5s
                  </span>
                )}
                {jobs.length > 0 && (
                  <div className="flex items-center gap-2">
                    <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedJobs.size === jobs.length && jobs.length > 0}
                        onChange={toggleAllJobs}
                        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      Zaznacz wszystkie
                    </label>
                    {selectedJobs.size > 0 && (
                      <button
                        onClick={bulkDeleteJobs}
                        className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
                        disabled={isLoading}
                      >
                        Usuń zaznaczone ({selectedJobs.size})
                      </button>
                    )}
                  </div>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setAutoRefreshEnabled(!autoRefreshEnabled)}
                  className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                    autoRefreshEnabled
                      ? 'bg-green-100 text-green-700 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  title={autoRefreshEnabled ? 'Wyłącz auto-odświeżanie' : 'Włącz auto-odświeżanie'}
                >
                  {autoRefreshEnabled ? '⏸' : '▶'} Auto
                </button>
                <button
                  onClick={() => loadJobs()}
                  disabled={isLoading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  {isLoading ? 'Odświeżanie...' : 'Odśwież'}
                </button>
              </div>
            </div>

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
                      <th className="px-4 py-3 text-left w-12">
                        {/* Checkbox column */}
                      </th>
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
                        <td className="px-4 py-4 whitespace-nowrap">
                          <input
                            type="checkbox"
                            checked={selectedJobs.has(job.id)}
                            onChange={() => toggleJobSelection(job.id)}
                            className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                          />
                        </td>
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
                        <td className="px-6 py-4">
                          <OptimizationProgressBar
                            job={{
                              id: job.id,
                              job_name: job.job_name,
                              status: job.status,
                              current_iteration: job.current_iteration,
                              progress_percentage: job.progress_percentage,
                              started_at: job.started_at,
                              runtime_seconds: job.runtime_seconds,
                              estimated_completion_at: job.estimated_completion_at
                            }}
                            showDetails={true}
                          />
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
                          {job.status === 'completed' ? (
                            <button
                              onClick={() => {
                                setSelectedJobForResults(job.id);
                                setActiveTab('results');
                              }}
                              className="text-blue-600 hover:text-blue-900 mr-3"
                            >
                              Zobacz wyniki
                            </button>
                          ) : (
                            <button className="text-gray-400 mr-3" disabled>
                              Zobacz
                            </button>
                          )}
                          {(job.status === 'running' || job.status === 'pending') && (
                            <button
                              onClick={() => handleCancelJob(job.id)}
                              className="text-red-600 hover:text-red-900"
                            >
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
            {selectedJobForResults ? (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900">Wyniki Optymalizacji</h2>
                  <button
                    onClick={() => setSelectedJobForResults(null)}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    ← Powrót do listy zadań
                  </button>
                </div>

                <OptimizationResults jobId={selectedJobForResults} />

                <ConvergenceChart jobId={selectedJobForResults} />
              </div>
            ) : (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Wyniki Optymalizacji</h2>

                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <p className="mt-2 text-gray-600">Ładowanie zadań...</p>
                  </div>
                ) : jobs.filter(j => j.status === 'completed').length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">Brak zakończonych optymalizacji</p>
                    <p className="text-gray-400 mt-2">Uruchom zadanie optymalizacji aby zobaczyć wyniki</p>
                  </div>
                ) : (
                  <div className="bg-white shadow-md rounded-lg overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Nazwa Zadania
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Ukończono
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Czas Wykonania
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Akcje
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {jobs
                          .filter(j => j.status === 'completed')
                          .map((job) => (
                            <tr key={job.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm font-medium text-gray-900">
                                  {job.job_name || `Zadanie ${job.id.slice(-8)}`}
                                </div>
                                <div className="text-sm text-gray-500">
                                  ID: {job.id.slice(-12)}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {job.completed_at
                                  ? new Date(job.completed_at).toLocaleString('pl-PL')
                                  : '-'
                                }
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {job.runtime_seconds
                                  ? `${Math.round(job.runtime_seconds / 60)} min ${Math.round(job.runtime_seconds % 60)} s`
                                  : '-'
                                }
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                <button
                                  onClick={() => setSelectedJobForResults(job.id)}
                                  className="text-blue-600 hover:text-blue-900"
                                >
                                  Zobacz wyniki
                                </button>
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Scenario Modal */}
      {showCreateScenario && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-full overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Nowy Scenariusz Optymalizacji</h3>

            {/* Validation Errors Display */}
            {validationErrors.length > 0 && (
              <ValidationErrorAlert
                errors={validationErrors}
                onClose={() => setValidationErrors([])}
              />
            )}

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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Konfiguracja bazowa</label>
                <select
                  value={newScenario.base_configuration_id}
                  onChange={(e) => setNewScenario({...newScenario, base_configuration_id: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                >
                  <option value="">Wybierz konfigurację...</option>
                  {regeneratorConfigs.map((config) => (
                    <option key={config.id} value={config.id}>
                      {config.name} ({config.regenerator_type})
                    </option>
                  ))}
                </select>
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
                disabled={isLoading || !newScenario.name || !newScenario.base_configuration_id}
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

      {/* Scenario Details Modal */}
      {selectedScenario && (
        <ScenarioDetailsModal
          scenario={selectedScenario}
          onClose={() => setSelectedScenario(null)}
        />
      )}
    </div>
  );
}

export default withAuth(OptimizePage);