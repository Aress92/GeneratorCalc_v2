'use client';

/**
 * Enhanced progress bar component for optimization jobs.
 * Wyświetla zaawansowany pasek postępu dla zadań optymalizacji.
 */

import { useEffect, useState } from 'react';

export interface OptimizationJobProgress {
  id: string;
  job_name: string | null;
  status: string;
  current_iteration: number;
  progress_percentage: number;
  started_at: string | null;
  runtime_seconds: number | null;
  estimated_completion_at: string | null;
}

interface OptimizationProgressBarProps {
  job: OptimizationJobProgress;
  showDetails?: boolean;
  onUpdate?: (job: OptimizationJobProgress) => void;
}

export default function OptimizationProgressBar({
  job,
  showDetails = true,
  onUpdate
}: OptimizationProgressBarProps) {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (job.status === 'running') {
      setIsAnimating(true);
    } else {
      setIsAnimating(false);
    }
  }, [job.status]);

  const getProgressColor = () => {
    if (job.status === 'completed') return 'bg-green-500';
    if (job.status === 'failed') return 'bg-red-500';
    if (job.status === 'cancelled') return 'bg-gray-500';
    if (job.status === 'running') return 'bg-blue-600';
    return 'bg-yellow-500';
  };

  const getProgressGradient = () => {
    if (job.status === 'completed') return 'from-green-400 to-green-600';
    if (job.status === 'failed') return 'from-red-400 to-red-600';
    if (job.status === 'cancelled') return 'from-gray-400 to-gray-600';
    if (job.status === 'running') return 'from-blue-400 to-blue-600';
    return 'from-yellow-400 to-yellow-600';
  };

  const getStatusIcon = () => {
    switch (job.status) {
      case 'completed':
        return (
          <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'running':
        return (
          <svg className="w-4 h-4 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        );
      case 'failed':
        return (
          <svg className="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      case 'pending':
        return (
          <svg className="w-4 h-4 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return null;
    }
  };

  const formatTimeRemaining = () => {
    if (!job.estimated_completion_at) return null;

    const now = new Date().getTime();
    const estimated = new Date(job.estimated_completion_at).getTime();
    const remaining = Math.max(0, estimated - now);

    const minutes = Math.floor(remaining / 60000);
    const seconds = Math.floor((remaining % 60000) / 1000);

    if (minutes > 60) {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `~${hours}h ${mins}m pozostało`;
    }

    if (minutes > 0) {
      return `~${minutes}m ${seconds}s pozostało`;
    }

    return `~${seconds}s pozostało`;
  };

  const formatElapsedTime = () => {
    if (!job.started_at) return null;

    const started = new Date(job.started_at).getTime();
    const now = new Date().getTime();
    const elapsed = now - started;

    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);

    if (minutes > 60) {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours}h ${mins}m`;
    }

    if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    }

    return `${seconds}s`;
  };

  return (
    <div className="w-full">
      {/* Progress bar */}
      <div className="relative w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
        <div
          className={`h-full bg-gradient-to-r ${getProgressGradient()} transition-all duration-500 ease-out ${
            isAnimating ? 'animate-pulse' : ''
          }`}
          style={{ width: `${Math.min(100, Math.max(0, job.progress_percentage))}%` }}
        >
          {/* Shimmer effect for running jobs */}
          {job.status === 'running' && (
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-shimmer"
                 style={{
                   backgroundSize: '200% 100%',
                   animation: 'shimmer 2s infinite linear'
                 }}
            />
          )}
        </div>

        {/* Progress percentage overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs font-semibold text-gray-700 drop-shadow-sm">
            {job.progress_percentage.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Details */}
      {showDetails && (
        <div className="mt-2 flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className="font-medium">
              Iteracja {job.current_iteration}
            </span>
          </div>

          <div className="flex items-center space-x-4">
            {job.status === 'running' && job.estimated_completion_at && (
              <span className="text-xs text-gray-500">
                {formatTimeRemaining()}
              </span>
            )}

            {job.started_at && (
              <span className="text-xs text-gray-500">
                Czas: {formatElapsedTime()}
              </span>
            )}
          </div>
        </div>
      )}

      <style jsx>{`
        @keyframes shimmer {
          0% {
            background-position: -200% 0;
          }
          100% {
            background-position: 200% 0;
          }
        }

        .animate-shimmer {
          animation: shimmer 2s infinite linear;
        }
      `}</style>
    </div>
  );
}
