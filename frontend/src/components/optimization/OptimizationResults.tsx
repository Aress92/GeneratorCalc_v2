'use client';

/**
 * Optimization Results Display Component
 *
 * Komponent wyświetlający wyniki optymalizacji z porównaniem baseline vs optimized
 */

import { useState, useEffect } from 'react';
import { OptimizationAPI } from '@/lib/api-client';
import type { OptimizationResult, PerformanceMetrics } from '@/types/api';
import { Activity, TrendingUp, TrendingDown, DollarSign, Zap, Wind, Thermometer } from 'lucide-react';

interface OptimizationResultsProps {
  jobId: string;
  onClose?: () => void;
}

interface MetricCardProps {
  title: string;
  baselineValue: number;
  optimizedValue: number;
  unit: string;
  icon: React.ReactNode;
  improvementPercentage?: number;
  higherIsBetter?: boolean;
}

function MetricCard({
  title,
  baselineValue,
  optimizedValue,
  unit,
  icon,
  improvementPercentage,
  higherIsBetter = true
}: MetricCardProps) {
  const isImprovement = higherIsBetter
    ? optimizedValue > baselineValue
    : optimizedValue < baselineValue;

  const improvement = improvementPercentage ??
    ((optimizedValue - baselineValue) / baselineValue * 100);

  const displayImprovement = Math.abs(improvement);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-700">{title}</h3>
        <div className="text-gray-400">{icon}</div>
      </div>

      <div className="space-y-3">
        <div>
          <div className="text-xs text-gray-500">Baseline</div>
          <div className="text-lg font-semibold text-gray-600">
            {baselineValue.toFixed(2)} {unit}
          </div>
        </div>

        <div>
          <div className="text-xs text-gray-500">Optymalizacja</div>
          <div className="text-2xl font-bold text-blue-600">
            {optimizedValue.toFixed(2)} {unit}
          </div>
        </div>

        <div className={`flex items-center text-sm font-medium ${
          isImprovement ? 'text-green-600' : 'text-red-600'
        }`}>
          {isImprovement ? (
            <TrendingUp className="w-4 h-4 mr-1" />
          ) : (
            <TrendingDown className="w-4 h-4 mr-1" />
          )}
          {displayImprovement.toFixed(2)}% {isImprovement ? 'poprawa' : 'spadek'}
        </div>
      </div>
    </div>
  );
}

export default function OptimizationResults({ jobId, onClose }: OptimizationResultsProps) {
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadResults();
  }, [jobId]);

  const loadResults = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await OptimizationAPI.getJobResults(jobId) as OptimizationResult;
      setResult(data);
    } catch (err: any) {
      console.error('Failed to load results:', err);
      setError(err.message || 'Nie udało się załadować wyników');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Ładowanie wyników...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-red-800 mb-2">Błąd ładowania wyników</h3>
        <p className="text-red-600">{error}</p>
        <button
          onClick={loadResults}
          className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
        >
          Spróbuj ponownie
        </button>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-yellow-800 mb-2">Brak wyników</h3>
        <p className="text-yellow-700">Wyniki optymalizacji nie są jeszcze dostępne.</p>
      </div>
    );
  }

  const { baseline_metrics, optimized_metrics, improvement_percentages, economic_analysis } = result;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Wyniki Optymalizacji</h2>
          <p className="text-gray-600 mt-1">
            Porównanie wydajności: Baseline vs Optymalizacja
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Efektywność Termiczna"
          baselineValue={baseline_metrics.thermal_efficiency}
          optimizedValue={optimized_metrics.thermal_efficiency}
          unit="%"
          icon={<Thermometer className="w-5 h-5" />}
          {...(improvement_percentages?.thermal_efficiency !== undefined && { improvementPercentage: improvement_percentages.thermal_efficiency })}
          higherIsBetter={true}
        />

        <MetricCard
          title="Spadek Ciśnienia"
          baselineValue={baseline_metrics.pressure_drop}
          optimizedValue={optimized_metrics.pressure_drop}
          unit="Pa"
          icon={<Wind className="w-5 h-5" />}
          {...(improvement_percentages?.pressure_drop !== undefined && { improvementPercentage: improvement_percentages.pressure_drop })}
          higherIsBetter={false}
        />

        <MetricCard
          title="Współczynnik HTC"
          baselineValue={baseline_metrics.heat_transfer_coefficient}
          optimizedValue={optimized_metrics.heat_transfer_coefficient}
          unit="W/m²K"
          icon={<Zap className="w-5 h-5" />}
          higherIsBetter={true}
        />

        <MetricCard
          title="NTU"
          baselineValue={baseline_metrics.ntu_value}
          optimizedValue={optimized_metrics.ntu_value}
          unit=""
          icon={<Activity className="w-5 h-5" />}
          higherIsBetter={true}
        />
      </div>

      {/* Economic Analysis */}
      {economic_analysis && (
        <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <DollarSign className="w-6 h-6 mr-2 text-green-600" />
            Analiza Ekonomiczna
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {economic_analysis.fuel_savings_percentage !== undefined && (
              <div>
                <div className="text-sm text-gray-600">Oszczędność paliwa</div>
                <div className="text-3xl font-bold text-green-600">
                  {economic_analysis.fuel_savings_percentage.toFixed(2)}%
                </div>
              </div>
            )}

            {economic_analysis.co2_reduction_percentage !== undefined && (
              <div>
                <div className="text-sm text-gray-600">Redukcja CO₂</div>
                <div className="text-3xl font-bold text-green-600">
                  {economic_analysis.co2_reduction_percentage.toFixed(2)}%
                </div>
              </div>
            )}

            {economic_analysis.annual_cost_savings !== undefined && (
              <div>
                <div className="text-sm text-gray-600">Oszczędności roczne</div>
                <div className="text-3xl font-bold text-blue-600">
                  €{economic_analysis.annual_cost_savings.toLocaleString()}
                </div>
              </div>
            )}

            {economic_analysis.payback_period_months !== undefined && (
              <div>
                <div className="text-sm text-gray-600">Okres zwrotu</div>
                <div className="text-3xl font-bold text-purple-600">
                  {economic_analysis.payback_period_months.toFixed(0)} mies.
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Design Variables Comparison */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Zmienne Projektowe</h3>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Zmienna
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Wartość Optymalna
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Jednostka
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.entries(result.design_variables_final).map(([key, value]) => (
                <tr key={key}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                    {value.toFixed(4)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {key.includes('height') || key.includes('thickness') || key.includes('spacing') ? 'm' :
                     key.includes('conductivity') ? 'W/(m·K)' :
                     key.includes('heat') ? 'J/(kg·K)' :
                     key.includes('density') ? 'kg/m³' : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Dodatkowe Metryki</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Baseline</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Prędkość przepływu ciepła:</span>
                <span className="font-semibold">{baseline_metrics.heat_transfer_rate.toFixed(0)} W</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Efektywność:</span>
                <span className="font-semibold">{baseline_metrics.effectiveness.toFixed(4)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Powierzchnia wymiany:</span>
                <span className="font-semibold">{baseline_metrics.surface_area.toFixed(2)} m²</span>
              </div>
              {baseline_metrics.wall_heat_loss && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Straty ciepła przez ściany:</span>
                  <span className="font-semibold">{baseline_metrics.wall_heat_loss.toFixed(0)} W</span>
                </div>
              )}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Po Optymalizacji</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Prędkość przepływu ciepła:</span>
                <span className="font-semibold text-blue-600">{optimized_metrics.heat_transfer_rate.toFixed(0)} W</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Efektywność:</span>
                <span className="font-semibold text-blue-600">{optimized_metrics.effectiveness.toFixed(4)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Powierzchnia wymiany:</span>
                <span className="font-semibold text-blue-600">{optimized_metrics.surface_area.toFixed(2)} m²</span>
              </div>
              {optimized_metrics.wall_heat_loss && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Straty ciepła przez ściany:</span>
                  <span className="font-semibold text-blue-600">{optimized_metrics.wall_heat_loss.toFixed(0)} W</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Quality Metrics */}
      {(result.solution_feasibility !== undefined || result.optimization_confidence !== undefined) && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Jakość Rozwiązania</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {result.solution_feasibility !== undefined && (
              <div>
                <div className="text-sm text-gray-600 mb-2">Wykonalność Rozwiązania</div>
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div
                    className="bg-green-600 h-4 rounded-full transition-all"
                    style={{ width: `${result.solution_feasibility * 100}%` }}
                  />
                </div>
                <div className="text-right text-sm font-semibold text-gray-700 mt-1">
                  {(result.solution_feasibility * 100).toFixed(0)}%
                </div>
              </div>
            )}

            {result.optimization_confidence !== undefined && (
              <div>
                <div className="text-sm text-gray-600 mb-2">Pewność Optymalizacji</div>
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div
                    className="bg-blue-600 h-4 rounded-full transition-all"
                    style={{ width: `${result.optimization_confidence * 100}%` }}
                  />
                </div>
                <div className="text-right text-sm font-semibold text-gray-700 mt-1">
                  {(result.optimization_confidence * 100).toFixed(0)}%
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
