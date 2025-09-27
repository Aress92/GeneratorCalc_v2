'use client';

/**
 * Optimization results visualization component.
 *
 * Komponent wizualizacji wyników optymalizacji.
 */

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

interface OptimizationResult {
  id: string;
  job_id: string;
  objective_value: number;
  baseline_metrics: PerformanceMetrics;
  optimized_metrics: PerformanceMetrics;
  improvement_percentages: { [key: string]: number };
  economic_analysis: EconomicAnalysis;
  thermal_efficiency?: number;
  pressure_drop?: number;
  heat_transfer_coefficient?: number;
  ntu_value?: number;
  solution_feasibility?: number;
  optimization_confidence?: number;
  created_at: string;
}

interface PerformanceMetrics {
  thermal_efficiency: number;
  heat_transfer_rate: number;
  pressure_drop: number;
  ntu_value: number;
  effectiveness: number;
  heat_transfer_coefficient: number;
  surface_area: number;
  wall_heat_loss?: number;
}

interface EconomicAnalysis {
  fuel_savings_percentage?: number;
  co2_reduction_percentage?: number;
  annual_cost_savings?: number;
  payback_period_months?: number;
  capital_cost_estimate?: number;
  net_present_value?: number;
}

interface OptimizationResultsProps {
  jobId: string;
  className?: string;
}

const COLORS = {
  primary: '#3B82F6',
  secondary: '#10B981',
  accent: '#F59E0B',
  danger: '#EF4444',
  success: '#059669',
  warning: '#D97706'
};

const PIE_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export default function OptimizationResults({ jobId, className }: OptimizationResultsProps) {
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeChart, setActiveChart] = useState<'performance' | 'economic' | 'convergence' | 'sensitivity'>('performance');

  useEffect(() => {
    loadResults();
  }, [jobId]);

  const loadResults = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/optimize/jobs/${jobId}/results`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else if (response.status === 404) {
        setError('Wyniki nie są jeszcze dostępne');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Błąd pobierania wyników');
      }
    } catch (error) {
      console.error('Failed to load results:', error);
      setError('Błąd połączenia z serwerem');
    } finally {
      setIsLoading(false);
    }
  };

  const formatNumber = (value: number | undefined, decimals: number = 2, suffix: string = ''): string => {
    if (value === undefined || value === null) return '-';
    return `${value.toFixed(decimals)}${suffix}`;
  };

  const formatPercentage = (value: number | undefined): string => {
    return formatNumber(value, 1, '%');
  };

  const formatCurrency = (value: number | undefined): string => {
    if (value === undefined || value === null) return '-';
    return `€${value.toLocaleString()}`;
  };

  const getPerformanceComparisonData = () => {
    if (!result) return [];

    return [
      {
        metric: 'Efektywność cieplna',
        baseline: result.baseline_metrics.thermal_efficiency * 100,
        optimized: result.optimized_metrics.thermal_efficiency * 100,
        improvement: result.improvement_percentages.thermal_efficiency || 0,
        unit: '%'
      },
      {
        metric: 'Spadek ciśnienia',
        baseline: result.baseline_metrics.pressure_drop,
        optimized: result.optimized_metrics.pressure_drop,
        improvement: ((result.baseline_metrics.pressure_drop - result.optimized_metrics.pressure_drop) / result.baseline_metrics.pressure_drop) * 100,
        unit: 'Pa'
      },
      {
        metric: 'Współczynnik przenikania',
        baseline: result.baseline_metrics.heat_transfer_coefficient,
        optimized: result.optimized_metrics.heat_transfer_coefficient,
        improvement: ((result.optimized_metrics.heat_transfer_coefficient - result.baseline_metrics.heat_transfer_coefficient) / result.baseline_metrics.heat_transfer_coefficient) * 100,
        unit: 'W/m²K'
      },
      {
        metric: 'NTU',
        baseline: result.baseline_metrics.ntu_value,
        optimized: result.optimized_metrics.ntu_value,
        improvement: ((result.optimized_metrics.ntu_value - result.baseline_metrics.ntu_value) / result.baseline_metrics.ntu_value) * 100,
        unit: '-'
      }
    ];
  };

  const getEconomicData = () => {
    if (!result?.economic_analysis) return [];

    return [
      {
        name: 'Oszczędności paliwa',
        value: result.economic_analysis.fuel_savings_percentage || 0,
        color: COLORS.success
      },
      {
        name: 'Redukcja CO₂',
        value: result.economic_analysis.co2_reduction_percentage || 0,
        color: COLORS.primary
      }
    ];
  };

  const getSensitivityData = () => {
    // Mock sensitivity data - in real implementation this would come from backend
    return [
      { variable: 'Wysokość checker', sensitivity: 0.85, fullMark: 1 },
      { variable: 'Odstęp checker', sensitivity: 0.72, fullMark: 1 },
      { variable: 'Grubość ściany', sensitivity: 0.45, fullMark: 1 },
      { variable: 'Przewodność cieplna', sensitivity: 0.68, fullMark: 1 },
      { variable: 'Ciepło właściwe', sensitivity: 0.32, fullMark: 1 },
      { variable: 'Gęstość', sensitivity: 0.28, fullMark: 1 }
    ];
  };

  if (isLoading) {
    return (
      <div className={`${className || ''} flex items-center justify-center py-12`}>
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Ładowanie wyników optymalizacji...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className || ''} flex items-center justify-center py-12`}>
        <div className="text-center">
          <div className="text-red-600 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={loadResults}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Spróbuj ponownie
          </button>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className={`${className || ''} text-center py-12`}>
        <p className="text-gray-500">Brak wyników do wyświetlenia</p>
      </div>
    );
  }

  return (
    <div className={className || ''}>
      {/* Results Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-green-50 rounded-lg p-6">
          <div className="text-green-600 text-3xl font-bold">
            {formatPercentage(result.economic_analysis.fuel_savings_percentage)}
          </div>
          <div className="text-green-800 font-medium">Oszczędności paliwa</div>
          <div className="text-green-600 text-sm">
            {formatCurrency(result.economic_analysis.annual_cost_savings)} rocznie
          </div>
        </div>

        <div className="bg-blue-50 rounded-lg p-6">
          <div className="text-blue-600 text-3xl font-bold">
            {formatPercentage(result.economic_analysis.co2_reduction_percentage)}
          </div>
          <div className="text-blue-800 font-medium">Redukcja CO₂</div>
          <div className="text-blue-600 text-sm">Emisje</div>
        </div>

        <div className="bg-purple-50 rounded-lg p-6">
          <div className="text-purple-600 text-3xl font-bold">
            {formatNumber(result.thermal_efficiency! * 100, 1)}%
          </div>
          <div className="text-purple-800 font-medium">Efektywność</div>
          <div className="text-purple-600 text-sm">Cieplna</div>
        </div>

        <div className="bg-orange-50 rounded-lg p-6">
          <div className="text-orange-600 text-3xl font-bold">
            {result.economic_analysis.payback_period_months
              ? `${Math.round(result.economic_analysis.payback_period_months)} mies.`
              : '-'
            }
          </div>
          <div className="text-orange-800 font-medium">Okres zwrotu</div>
          <div className="text-orange-600 text-sm">Inwestycji</div>
        </div>
      </div>

      {/* Chart Navigation */}
      <div className="mb-6">
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {[
            { key: 'performance', label: 'Wydajność' },
            { key: 'economic', label: 'Ekonomia' },
            { key: 'sensitivity', label: 'Wrażliwość' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveChart(tab.key as any)}
              className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                activeChart === tab.key
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Charts */}
      <div className="bg-white rounded-lg shadow-md p-6">
        {activeChart === 'performance' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Porównanie wydajności</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={getPerformanceComparisonData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="metric" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip
                  formatter={(value: number, name: string) => [
                    `${value.toFixed(2)}`,
                    name === 'baseline' ? 'Baseline' : name === 'optimized' ? 'Zoptymalizowany' : 'Poprawa'
                  ]}
                />
                <Legend />
                <Bar dataKey="baseline" fill={COLORS.accent} name="Baseline" />
                <Bar dataKey="optimized" fill={COLORS.primary} name="Zoptymalizowany" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeChart === 'economic' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Korzyści ekonomiczne</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={getEconomicData()}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {getEconomicData().map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => [`${value.toFixed(1)}%`, 'Poprawa']} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {formatCurrency(result.economic_analysis.annual_cost_savings)}
                  </div>
                  <div className="text-gray-600">Roczne oszczędności</div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {result.economic_analysis.payback_period_months
                      ? `${Math.round(result.economic_analysis.payback_period_months)} miesięcy`
                      : 'N/A'
                    }
                  </div>
                  <div className="text-gray-600">Okres zwrotu</div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {formatCurrency(result.economic_analysis.net_present_value)}
                  </div>
                  <div className="text-gray-600">NPV (10 lat)</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeChart === 'sensitivity' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Analiza wrażliwości</h3>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={getSensitivityData()}>
                <PolarGrid />
                <PolarAngleAxis dataKey="variable" />
                <PolarRadiusAxis domain={[0, 1]} />
                <Radar
                  name="Wrażliwość"
                  dataKey="sensitivity"
                  stroke={COLORS.primary}
                  fill={COLORS.primary}
                  fillOpacity={0.3}
                />
                <Tooltip formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'Wpływ na cel']} />
              </RadarChart>
            </ResponsiveContainer>
            <div className="mt-4 text-sm text-gray-600">
              <p>Wykres pokazuje wrażliwość funkcji celu na zmiany poszczególnych parametrów optymalizacji.</p>
              <p>Wyższe wartości oznaczają większy wpływ parametru na wynik optymalizacji.</p>
            </div>
          </div>
        )}
      </div>

      {/* Technical Details */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Szczegóły techniczne</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Parametry optymalizacji</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Wartość funkcji celu:</span>
                <span className="font-medium">{formatNumber(result.objective_value, 6)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Spadek ciśnienia:</span>
                <span className="font-medium">{formatNumber(result.pressure_drop)} Pa</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Współczynnik przenikania:</span>
                <span className="font-medium">{formatNumber(result.heat_transfer_coefficient)} W/m²K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">NTU:</span>
                <span className="font-medium">{formatNumber(result.ntu_value)}</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-2">Jakość rozwiązania</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Dopuszczalność rozwiązania:</span>
                <span className="font-medium">{formatPercentage(result.solution_feasibility! * 100)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Pewność optymalizacji:</span>
                <span className="font-medium">{formatPercentage(result.optimization_confidence! * 100)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Data zakończenia:</span>
                <span className="font-medium">{new Date(result.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}