'use client';

/**
 * Scenario Details Modal Component
 *
 * Modal wyświetlający pełną konfigurację scenariusza optymalizacji
 */

import { useState } from 'react';
import { X, Settings, Target, Cpu, Sliders, Box, AlertCircle, Calculator } from 'lucide-react';
import type { OptimizationScenario } from '@/types/api';
import OptimizationCalculationPreview from './OptimizationCalculationPreview';

interface ScenarioDetailsModalProps {
  scenario: OptimizationScenario;
  onClose: () => void;
}

interface DesignVariable {
  name: string;
  description?: string;
  unit?: string;
  min_value: number;
  max_value: number;
  baseline_value?: number;
  variable_type?: string;
}

interface Constraint {
  name: string;
  constraint_type: string;
  expression?: string;
  function_name?: string;
  bounds?: { lower?: number; upper?: number };
  tolerance?: number;
  is_active?: boolean;
}

export default function ScenarioDetailsModal({ scenario, onClose }: ScenarioDetailsModalProps) {
  const [showCalculationPreview, setShowCalculationPreview] = useState(false);

  // Parse scenario data
  const scenarioData = scenario as any;
  const designVariables: Record<string, DesignVariable> = scenarioData.design_variables || {};
  const boundsConfig: Record<string, { min: number; max: number }> = scenarioData.bounds_config || {};
  const constraintsConfig = scenarioData.constraints_config || {};
  const constraints: Constraint[] = constraintsConfig.constraints || [];
  const optimizationConfig = scenarioData.optimization_config || {};
  const objectiveWeights = scenarioData.objective_weights || {};

  // Get scenario type label
  const getScenarioTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'baseline': 'Baseline',
      'geometry_optimization': 'Optymalizacja Geometrii',
      'material_optimization': 'Optymalizacja Materiałów',
      'operating_conditions': 'Warunki Pracy',
      'comprehensive': 'Optymalizacja Kompleksowa'
    };
    return labels[type] || type;
  };

  // Get objective label
  const getObjectiveLabel = (objective: string) => {
    const labels: Record<string, string> = {
      'minimize_fuel_consumption': 'Minimalizacja Zużycia Paliwa',
      'minimize_co2_emissions': 'Minimalizacja Emisji CO₂',
      'maximize_efficiency': 'Maksymalizacja Wydajności',
      'minimize_cost': 'Minimalizacja Kosztów',
      'multi_objective': 'Wielokryterialna'
    };
    return labels[objective] || objective;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Settings className="w-6 h-6 text-white" />
            <div>
              <h2 className="text-xl font-bold text-white">{scenario.name}</h2>
              <p className="text-blue-100 text-sm">Szczegóły Scenariusza Optymalizacji</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-blue-100 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Basic Information */}
          <section className="bg-gray-50 rounded-lg p-5">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2 text-blue-600" />
              Informacje Podstawowe
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-600">Nazwa</label>
                <p className="text-gray-900 font-semibold">{scenario.name}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Typ Scenariusza</label>
                <p className="text-gray-900 font-semibold">{getScenarioTypeLabel(scenario.scenario_type)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Cel Optymalizacji</label>
                <p className="text-gray-900 font-semibold">{getObjectiveLabel(scenario.objective)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Algorytm</label>
                <p className="text-gray-900 font-semibold">{scenario.algorithm.toUpperCase()}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Status</label>
                <p className="text-gray-900 font-semibold capitalize">{scenario.status}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Data Utworzenia</label>
                <p className="text-gray-900 font-semibold">
                  {new Date(scenario.created_at).toLocaleString('pl-PL')}
                </p>
              </div>
            </div>
            {scenario.description && (
              <div className="mt-4">
                <label className="text-sm font-medium text-gray-600">Opis</label>
                <p className="text-gray-700 mt-1">{scenario.description}</p>
              </div>
            )}
          </section>

          {/* Optimization Parameters */}
          <section className="bg-white border border-gray-200 rounded-lg p-5">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Cpu className="w-5 h-5 mr-2 text-purple-600" />
              Parametry Optymalizacji
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded p-3">
                <label className="text-xs font-medium text-gray-600">Max Iteracji</label>
                <p className="text-lg font-bold text-gray-900">{scenarioData.max_iterations || 1000}</p>
              </div>
              <div className="bg-gray-50 rounded p-3">
                <label className="text-xs font-medium text-gray-600">Max Ewaluacji</label>
                <p className="text-lg font-bold text-gray-900">{scenarioData.max_function_evaluations || 5000}</p>
              </div>
              <div className="bg-gray-50 rounded p-3">
                <label className="text-xs font-medium text-gray-600">Tolerancja</label>
                <p className="text-lg font-bold text-gray-900">{scenarioData.tolerance || 1e-6}</p>
              </div>
              <div className="bg-gray-50 rounded p-3">
                <label className="text-xs font-medium text-gray-600">Max Czas (min)</label>
                <p className="text-lg font-bold text-gray-900">{scenarioData.max_runtime_minutes || 120}</p>
              </div>
            </div>
          </section>

          {/* Design Variables */}
          <section className="bg-white border border-gray-200 rounded-lg p-5">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Sliders className="w-5 h-5 mr-2 text-green-600" />
              Zmienne Projektowe ({Object.keys(designVariables).length})
            </h3>

            {Object.keys(designVariables).length === 0 ? (
              <p className="text-gray-500 text-center py-4">Brak zdefiniowanych zmiennych projektowych</p>
            ) : (
              <div className="space-y-3">
                {Object.entries(designVariables).map(([key, variable]) => (
                  <div key={key} className="bg-gradient-to-r from-gray-50 to-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-semibold text-gray-900">
                          {variable.description || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </h4>
                        <p className="text-sm text-gray-500">
                          Klucz: <code className="bg-gray-100 px-1 rounded">{key}</code>
                        </p>
                      </div>
                      <div className="text-right">
                        <span className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">
                          {variable.variable_type || 'continuous'}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
                      <div>
                        <label className="text-xs text-gray-600">Minimum</label>
                        <p className="text-sm font-bold text-red-600">
                          {variable.min_value} {variable.unit || ''}
                        </p>
                      </div>
                      <div>
                        <label className="text-xs text-gray-600">Maximum</label>
                        <p className="text-sm font-bold text-green-600">
                          {variable.max_value} {variable.unit || ''}
                        </p>
                      </div>
                      {variable.baseline_value !== undefined && (
                        <div>
                          <label className="text-xs text-gray-600">Baseline</label>
                          <p className="text-sm font-bold text-gray-700">
                            {variable.baseline_value} {variable.unit || ''}
                          </p>
                        </div>
                      )}
                      {variable.unit && (
                        <div>
                          <label className="text-xs text-gray-600">Jednostka</label>
                          <p className="text-sm font-bold text-gray-700">{variable.unit}</p>
                        </div>
                      )}
                    </div>

                    {/* Visual range indicator */}
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>{variable.min_value}</span>
                        {variable.baseline_value !== undefined && (
                          <span className="text-gray-700 font-semibold">
                            Baseline: {variable.baseline_value}
                          </span>
                        )}
                        <span>{variable.max_value}</span>
                      </div>
                      <div className="relative h-2 bg-gradient-to-r from-red-200 via-yellow-200 to-green-200 rounded-full">
                        {variable.baseline_value !== undefined && (
                          <div
                            className="absolute top-1/2 -translate-y-1/2 w-1 h-4 bg-gray-700 rounded"
                            style={{
                              left: `${((variable.baseline_value - variable.min_value) / (variable.max_value - variable.min_value)) * 100}%`
                            }}
                          />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Bounds Configuration */}
          {Object.keys(boundsConfig).length > 0 && (
            <section className="bg-white border border-gray-200 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Box className="w-5 h-5 mr-2 text-orange-600" />
                Konfiguracja Granic
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Zmienna</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Min</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Max</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Zakres</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(boundsConfig).map(([key, bounds]) => (
                      <tr key={key}>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{key}</td>
                        <td className="px-4 py-3 text-sm text-red-600 font-semibold">{bounds.min}</td>
                        <td className="px-4 py-3 text-sm text-green-600 font-semibold">{bounds.max}</td>
                        <td className="px-4 py-3 text-sm text-gray-700">
                          <div className="w-32 h-2 bg-gradient-to-r from-red-200 to-green-200 rounded-full" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {/* Constraints */}
          {constraints.length > 0 && (
            <section className="bg-white border border-gray-200 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Target className="w-5 h-5 mr-2 text-red-600" />
                Ograniczenia ({constraints.length})
              </h3>
              <div className="space-y-3">
                {constraints.map((constraint, index) => (
                  <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{constraint.name}</h4>
                        <p className="text-sm text-gray-600 mt-1">
                          Typ: <span className="font-medium">{constraint.constraint_type}</span>
                        </p>
                        {constraint.expression && (
                          <p className="text-sm text-gray-700 mt-2">
                            <code className="bg-white px-2 py-1 rounded border border-gray-300">
                              {constraint.expression}
                            </code>
                          </p>
                        )}
                        {constraint.function_name && (
                          <p className="text-sm text-gray-700 mt-1">
                            Funkcja: <code className="bg-white px-2 py-1 rounded">{constraint.function_name}</code>
                          </p>
                        )}
                        {constraint.bounds && (
                          <p className="text-sm text-gray-700 mt-1">
                            Granice: [{constraint.bounds.lower || '-∞'}, {constraint.bounds.upper || '∞'}]
                          </p>
                        )}
                        {constraint.tolerance !== undefined && (
                          <p className="text-sm text-gray-600 mt-1">
                            Tolerancja: {constraint.tolerance}
                          </p>
                        )}
                      </div>
                      <div>
                        {constraint.is_active !== false ? (
                          <span className="inline-block bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded">
                            Aktywne
                          </span>
                        ) : (
                          <span className="inline-block bg-gray-100 text-gray-600 text-xs font-semibold px-2 py-1 rounded">
                            Nieaktywne
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Objective Weights (for multi-objective) */}
          {Object.keys(objectiveWeights).length > 0 && (
            <section className="bg-white border border-gray-200 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Wagi Funkcji Celu</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {Object.entries(objectiveWeights).map(([key, weight]) => (
                  <div key={key} className="bg-gray-50 rounded p-3">
                    <label className="text-xs font-medium text-gray-600">{key}</label>
                    <p className="text-lg font-bold text-gray-900">{weight as number}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Additional Configuration */}
          {Object.keys(optimizationConfig).length > 0 && (
            <section className="bg-gray-50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Dodatkowa Konfiguracja</h3>
              <pre className="bg-white border border-gray-200 rounded p-4 text-xs overflow-x-auto">
                {JSON.stringify(optimizationConfig, null, 2)}
              </pre>
            </section>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 flex justify-between items-center border-t border-gray-200">
          <button
            onClick={() => setShowCalculationPreview(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Calculator className="w-4 h-4" />
            Podgląd Obliczeń
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Zamknij
          </button>
        </div>
      </div>

      {/* Calculation Preview Modal */}
      {showCalculationPreview && (
        <OptimizationCalculationPreview
          scenarioId={scenario.id}
          onClose={() => setShowCalculationPreview(false)}
        />
      )}
    </div>
  );
}
