'use client';

/**
 * Convergence Chart Component - displays SLSQP algorithm convergence history
 *
 * Komponent wykresu konwergencji - wyświetla historię zbieżności algorytmu SLSQP
 */

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { OptimizationAPI } from '@/lib/api-client';
import type { OptimizationIteration } from '@/types/api';

interface ConvergenceChartProps {
  jobId: string;
  height?: number;
}

interface ChartDataPoint {
  iteration: number;
  objective_value: number;
  best_value: number;
  is_improvement: boolean;
}

export default function ConvergenceChart({ jobId, height = 400 }: ConvergenceChartProps) {
  const [iterations, setIterations] = useState<OptimizationIteration[]>([]);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadIterations();
  }, [jobId]);

  useEffect(() => {
    if (iterations.length > 0) {
      processChartData();
    }
  }, [iterations]);

  const loadIterations = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await OptimizationAPI.getJobIterations(jobId, { limit: 1000 }) as any;

      // Handle different response formats
      const iterationsArray = Array.isArray(data) ? data : (data.iterations || []);

      // Sort by iteration number
      const sortedIterations = iterationsArray.sort(
        (a: OptimizationIteration, b: OptimizationIteration) =>
          a.iteration_number - b.iteration_number
      );

      setIterations(sortedIterations);
    } catch (err: any) {
      console.error('Failed to load iterations:', err);
      setError(err.message || 'Nie udało się załadować danych iteracji');
    } finally {
      setIsLoading(false);
    }
  };

  const processChartData = () => {
    let bestValue = Infinity;

    const data: ChartDataPoint[] = iterations.map((iter) => {
      const objectiveValue = iter.objective_value;

      // Track best value (assuming minimization)
      if (objectiveValue < bestValue) {
        bestValue = objectiveValue;
      }

      return {
        iteration: iter.iteration_number,
        objective_value: objectiveValue,
        best_value: bestValue,
        is_improvement: iter.is_improvement
      };
    });

    setChartData(data);
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Wykres Konwergencji</h3>
        <div className="flex items-center justify-center" style={{ height }}>
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Ładowanie danych...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Wykres Konwergencji</h3>
        <div className="bg-red-50 border border-red-200 rounded p-4">
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadIterations}
            className="mt-2 text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
          >
            Spróbuj ponownie
          </button>
        </div>
      </div>
    );
  }

  if (chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Wykres Konwergencji</h3>
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
          <p className="text-yellow-700">Brak danych iteracji do wyświetlenia.</p>
        </div>
      </div>
    );
  }

  // Calculate statistics
  const firstValue = chartData[0]?.objective_value ?? 0;
  const lastValue = chartData[chartData.length - 1]?.objective_value ?? 0;
  const bestValue = chartData[chartData.length - 1]?.best_value ?? 0;
  const improvement = ((firstValue - bestValue) / Math.abs(firstValue)) * 100;
  const totalIterations = chartData.length;
  const improvementCount = chartData.filter(d => d.is_improvement).length;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h3 className="text-xl font-bold text-gray-900">Wykres Konwergencji</h3>
        <p className="text-sm text-gray-600 mt-1">
          Historia zbieżności algorytmu SLSQP (minimalizacja funkcji celu)
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 rounded p-3">
          <div className="text-xs text-gray-600">Iteracje</div>
          <div className="text-lg font-bold text-gray-900">{totalIterations}</div>
        </div>
        <div className="bg-gray-50 rounded p-3">
          <div className="text-xs text-gray-600">Wartość początkowa</div>
          <div className="text-lg font-bold text-gray-900">{firstValue.toFixed(6)}</div>
        </div>
        <div className="bg-green-50 rounded p-3">
          <div className="text-xs text-green-600">Najlepsza wartość</div>
          <div className="text-lg font-bold text-green-700">{bestValue.toFixed(6)}</div>
        </div>
        <div className="bg-blue-50 rounded p-3">
          <div className="text-xs text-blue-600">Poprawa</div>
          <div className="text-lg font-bold text-blue-700">{improvement.toFixed(2)}%</div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="iteration"
            label={{ value: 'Numer Iteracji', position: 'insideBottom', offset: -5 }}
            stroke="#6b7280"
          />
          <YAxis
            label={{ value: 'Wartość Funkcji Celu', angle: -90, position: 'insideLeft' }}
            stroke="#6b7280"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '0.5rem',
              padding: '0.75rem'
            }}
            formatter={(value: number) => value.toFixed(6)}
            labelFormatter={(label) => `Iteracja ${label}`}
          />
          <Legend
            wrapperStyle={{ paddingTop: '1rem' }}
          />
          <Line
            type="monotone"
            dataKey="objective_value"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: '#3b82f6', r: 3 }}
            activeDot={{ r: 5 }}
            name="Wartość bieżąca"
          />
          <Line
            type="monotone"
            dataKey="best_value"
            stroke="#10b981"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="Najlepsza wartość"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Additional Info */}
      <div className="mt-4 p-4 bg-blue-50 rounded">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3 text-sm">
            <p className="text-blue-700">
              <strong>Interpretacja:</strong> Algorytm SLSQP wykonał {totalIterations} iteracji,
              z czego {improvementCount} ({((improvementCount/totalIterations)*100).toFixed(1)}%)
              przyniosło poprawę. Linia niebieska pokazuje wartość funkcji celu w każdej iteracji,
              a zielona linia przerywana wskazuje najlepszą dotychczas znalezioną wartość.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
