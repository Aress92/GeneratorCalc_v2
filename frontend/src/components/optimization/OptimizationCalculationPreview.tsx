'use client';

import React, { useState, useEffect } from 'react';
import { X, Calculator, TrendingUp, DollarSign, AlertTriangle, CheckCircle } from 'lucide-react';
import { ApiClient } from '@/lib/api-client';
// TODO: Re-enable sonner after fixing pnpm installation
// import { toast } from 'sonner';

// Temporary toast fallback until sonner is installed
const toast = {
  success: (msg: string) => console.log('✅', msg),
  error: (msg: string) => console.error('❌', msg),
  warning: (msg: string) => console.warn('⚠️', msg),
  info: (msg: string) => console.info('ℹ️', msg),
};

interface CalculationStep {
  step_name: string;
  formula: string;
  substitution: string;
  result: number;
  unit: string;
  explanation: string;
}

interface ConstraintCheck {
  value: number;
  limit: number;
  status: 'OK' | 'VIOLATED';
  margin: number;
  explanation: string;
}

interface CalculationPreview {
  scenario_id: string;
  scenario_name: string;
  design_variables: Record<string, number>;
  geometry_calculations: CalculationStep[];
  heat_transfer_calculations: CalculationStep[];
  performance_calculations: CalculationStep[];
  economic_calculations: CalculationStep[];
  final_metrics: Record<string, number>;
  constraints_check: Record<string, ConstraintCheck>;
  operating_conditions: Record<string, number>;
  material_properties: Record<string, number>;
}

interface OptimizationCalculationPreviewProps {
  scenarioId: string;
  onClose: () => void;
}

export default function OptimizationCalculationPreview({
  scenarioId,
  onClose,
}: OptimizationCalculationPreviewProps) {
  const [preview, setPreview] = useState<CalculationPreview | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'geometry' | 'heat_transfer' | 'performance' | 'economic'>('geometry');

  useEffect(() => {
    loadPreview();
  }, [scenarioId]);

  const loadPreview = async () => {
    try {
      setLoading(true);
      const data = await ApiClient.getScenarioCalculationPreview(scenarioId);
      setPreview(data as CalculationPreview);
    } catch (error: any) {
      toast.error('Błąd ładowania podglądu obliczeń');
      console.error('Failed to load calculation preview:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderCalculationStep = (step: CalculationStep, index: number) => (
    <div key={index} className="bg-gray-50 rounded-lg p-4 space-y-2">
      <div className="flex items-start justify-between">
        <h4 className="font-medium text-gray-900">{step.step_name}</h4>
        <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
          Krok {index + 1}
        </span>
      </div>

      {/* Formula */}
      <div className="bg-white p-3 rounded border border-gray-200">
        <div className="text-xs text-gray-500 mb-1">Wzór:</div>
        <div className="font-mono text-sm text-gray-900">{step.formula}</div>
      </div>

      {/* Substitution */}
      <div className="bg-white p-3 rounded border border-gray-200">
        <div className="text-xs text-gray-500 mb-1">Podstawienie wartości:</div>
        <div className="font-mono text-sm text-gray-700">{step.substitution}</div>
      </div>

      {/* Result */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-3 rounded border border-green-200">
        <div className="flex items-center justify-between">
          <div className="text-xs text-green-600 mb-1">Wynik:</div>
          <div className="text-lg font-bold text-green-700">
            {step.result.toFixed(4)} {step.unit}
          </div>
        </div>
      </div>

      {/* Explanation */}
      <div className="text-sm text-gray-600 italic">{step.explanation}</div>
    </div>
  );

  const renderConstraints = () => {
    if (!preview) return null;

    return (
      <div className="space-y-3">
        {Object.entries(preview.constraints_check).map(([key, constraint]) => (
          <div
            key={key}
            className={`p-4 rounded-lg border-2 ${
              constraint.status === 'OK'
                ? 'bg-green-50 border-green-300'
                : 'bg-red-50 border-red-300'
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                {constraint.status === 'OK' ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                )}
                <h4 className="font-medium text-gray-900">{key.replace(/_/g, ' ').toUpperCase()}</h4>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  constraint.status === 'OK'
                    ? 'bg-green-200 text-green-800'
                    : 'bg-red-200 text-red-800'
                }`}
              >
                {constraint.status}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 text-sm">
              <div>
                <div className="text-gray-600">Wartość:</div>
                <div className="font-semibold">{constraint.value.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-gray-600">Limit:</div>
                <div className="font-semibold">{constraint.limit.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-gray-600">Margines:</div>
                <div
                  className={`font-semibold ${
                    constraint.margin > 0 ? 'text-green-700' : 'text-red-700'
                  }`}
                >
                  {constraint.margin > 0 ? '+' : ''}
                  {constraint.margin.toFixed(2)}
                </div>
              </div>
            </div>

            <div className="mt-2 text-sm text-gray-700 italic">{constraint.explanation}</div>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md">
          <div className="flex items-center gap-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <div className="text-lg">Generowanie podglądu obliczeń...</div>
          </div>
        </div>
      </div>
    );
  }

  if (!preview) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Calculator className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Podgląd Obliczeń Optymalizacji</h2>
              <p className="text-blue-100 text-sm mt-1">{preview.scenario_name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 bg-gray-50 px-6">
          <div className="flex gap-1">
            <button
              onClick={() => setActiveTab('geometry')}
              className={`px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'geometry'
                  ? 'border-blue-600 text-blue-600 bg-white'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Geometria ({preview.geometry_calculations.length})
            </button>
            <button
              onClick={() => setActiveTab('heat_transfer')}
              className={`px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'heat_transfer'
                  ? 'border-blue-600 text-blue-600 bg-white'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Wymiana Ciepła ({preview.heat_transfer_calculations.length})
            </button>
            <button
              onClick={() => setActiveTab('performance')}
              className={`px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'performance'
                  ? 'border-blue-600 text-blue-600 bg-white'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Wydajność ({preview.performance_calculations.length})
            </button>
            <button
              onClick={() => setActiveTab('economic')}
              className={`px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'economic'
                  ? 'border-blue-600 text-blue-600 bg-white'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Ekonomia ({preview.economic_calculations.length})
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Design Variables */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-3">Zmienne Projektowe</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {Object.entries(preview.design_variables).map(([key, value]) => (
                  <div key={key} className="bg-white p-3 rounded shadow-sm">
                    <div className="text-xs text-gray-500">{key.replace(/_/g, ' ')}</div>
                    <div className="font-semibold text-gray-900">{value.toFixed(3)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Calculation Steps */}
            {activeTab === 'geometry' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                  Obliczenia Geometryczne
                </h3>
                {preview.geometry_calculations.map((step, idx) => renderCalculationStep(step, idx))}
              </div>
            )}

            {activeTab === 'heat_transfer' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <TrendingUp className="w-6 h-6 text-orange-600" />
                  Obliczenia Wymiany Ciepła
                </h3>
                {preview.heat_transfer_calculations.map((step, idx) => renderCalculationStep(step, idx))}
              </div>
            )}

            {activeTab === 'performance' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                  Obliczenia Wydajnościowe
                </h3>
                {preview.performance_calculations.map((step, idx) => renderCalculationStep(step, idx))}

                {/* Constraints */}
                <div className="mt-8">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Sprawdzenie Ograniczeń</h3>
                  {renderConstraints()}
                </div>
              </div>
            )}

            {activeTab === 'economic' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <DollarSign className="w-6 h-6 text-yellow-600" />
                  Obliczenia Ekonomiczne
                </h3>
                {preview.economic_calculations.map((step, idx) => renderCalculationStep(step, idx))}
              </div>
            )}

            {/* Final Metrics Summary */}
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-300 rounded-lg p-6 mt-8">
              <h3 className="text-xl font-bold text-purple-900 mb-4">Podsumowanie Wyników</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-xs text-gray-500">Sprawność termiczna</div>
                  <div className="text-2xl font-bold text-purple-700">
                    {(preview.final_metrics.thermal_efficiency * 100).toFixed(2)}%
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-xs text-gray-500">Spadek ciśnienia</div>
                  <div className="text-2xl font-bold text-purple-700">
                    {preview.final_metrics.pressure_drop.toFixed(0)} Pa
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-xs text-gray-500">NTU</div>
                  <div className="text-2xl font-bold text-purple-700">
                    {preview.final_metrics.ntu_value.toFixed(2)}
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-xs text-gray-500">Współczynnik HTC</div>
                  <div className="text-2xl font-bold text-purple-700">
                    {preview.final_metrics.heat_transfer_coefficient.toFixed(1)} W/(m²·K)
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-xs text-gray-500">Powierzchnia</div>
                  <div className="text-2xl font-bold text-purple-700">
                    {preview.final_metrics.surface_area.toFixed(0)} m²
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-xs text-gray-500">Efektywność</div>
                  <div className="text-2xl font-bold text-purple-700">
                    {(preview.final_metrics.effectiveness * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 bg-gray-50 px-6 py-4 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Zamknij
          </button>
        </div>
      </div>
    </div>
  );
}
