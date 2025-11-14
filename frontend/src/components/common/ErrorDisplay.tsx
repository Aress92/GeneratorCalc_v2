'use client';

import React from 'react';
import { AlertTriangle, XCircle, Info, RefreshCw, ExternalLink } from 'lucide-react';

interface DetailedError {
  error_type: string;
  message: string;
  details: string;
  suggestion: string;
  [key: string]: any; // Additional context fields
}

interface ErrorDisplayProps {
  error: any;
  onRetry?: () => void;
  onClose?: () => void;
  showRetry?: boolean;
  className?: string;
}

export default function ErrorDisplay({
  error,
  onRetry,
  onClose,
  showRetry = true,
  className = '',
}: ErrorDisplayProps) {
  // Parse error - handle both structured and simple errors
  const parseError = (err: any): DetailedError | null => {
    if (!err) return null;

    // If error is already structured (from backend)
    if (typeof err === 'object' && err.error_type) {
      return err as DetailedError;
    }

    // If error has detail property (FastAPI HTTPException)
    if (err.detail && typeof err.detail === 'object' && err.detail.error_type) {
      return err.detail as DetailedError;
    }

    // If error message contains JSON
    if (err.message && typeof err.message === 'string') {
      try {
        const parsed = JSON.parse(err.message);
        if (parsed.error_type) return parsed as DetailedError;
      } catch {
        // Not JSON, continue
      }
    }

    // Simple error message
    return {
      error_type: 'UNKNOWN_ERROR',
      message: err.message || String(err),
      details: err.toString(),
      suggestion: 'Spróbuj ponownie lub skontaktuj się z administratorem',
    };
  };

  const errorData = parseError(error);
  if (!errorData) return null;

  // Get icon and color based on error type
  const getErrorStyle = (type: string) => {
    if (type.includes('NOT_FOUND') || type === 'SCENARIO_NOT_FOUND') {
      return {
        icon: Info,
        color: 'blue',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-300',
        textColor: 'text-blue-900',
        iconColor: 'text-blue-600',
      };
    }

    if (type.includes('PERMISSION') || type === 'PERMISSION_DENIED') {
      return {
        icon: XCircle,
        color: 'red',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-300',
        textColor: 'text-red-900',
        iconColor: 'text-red-600',
      };
    }

    if (type.includes('VALIDATION') || type === 'TOO_MANY_ACTIVE_JOBS') {
      return {
        icon: AlertTriangle,
        color: 'yellow',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-300',
        textColor: 'text-yellow-900',
        iconColor: 'text-yellow-600',
      };
    }

    // Default (errors, server errors)
    return {
      icon: XCircle,
      color: 'red',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-300',
      textColor: 'text-red-900',
      iconColor: 'text-red-600',
    };
  };

  const style = getErrorStyle(errorData.error_type);
  const Icon = style.icon;

  // Get user-friendly error type label
  const getErrorTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      PERMISSION_DENIED: 'Brak uprawnień',
      SCENARIO_NOT_FOUND: 'Scenariusz nie znaleziony',
      SCENARIO_INACTIVE: 'Scenariusz nieaktywny',
      NO_DESIGN_VARIABLES: 'Brak zmiennych projektowych',
      BASE_CONFIG_NOT_FOUND: 'Brak konfiguracji bazowej',
      TOO_MANY_ACTIVE_JOBS: 'Za dużo aktywnych zadań',
      VALIDATION_ERROR: 'Błąd walidacji',
      INTERNAL_SERVER_ERROR: 'Błąd serwera',
      UNKNOWN_ERROR: 'Nieznany błąd',
    };
    return labels[type] || type.replace(/_/g, ' ');
  };

  // Extract additional context fields (excluding standard ones)
  const additionalContext: Record<string, any> = {};
  const standardFields = ['error_type', 'message', 'details', 'suggestion', 'error_trace'];
  Object.entries(errorData).forEach(([key, value]) => {
    if (!standardFields.includes(key) && value !== null && value !== undefined) {
      additionalContext[key] = value;
    }
  });

  return (
    <div className={`rounded-lg border-2 ${style.borderColor} ${style.bgColor} p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <Icon className={`w-6 h-6 ${style.iconColor} flex-shrink-0 mt-0.5`} />
          <div>
            <h3 className={`text-lg font-bold ${style.textColor}`}>{errorData.message}</h3>
            <p className="text-sm text-gray-500 mt-1">{getErrorTypeLabel(errorData.error_type)}</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Zamknij"
          >
            <XCircle className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Details */}
      <div className="space-y-3">
        <div className="bg-white bg-opacity-50 rounded-lg p-4 border border-gray-200">
          <h4 className="font-semibold text-gray-900 mb-2 text-sm">Szczegóły błędu:</h4>
          <p className="text-sm text-gray-700 leading-relaxed">{errorData.details}</p>
        </div>

        {/* Suggestion */}
        <div className="bg-white rounded-lg p-4 border-2 border-green-200">
          <h4 className="font-semibold text-green-900 mb-2 text-sm flex items-center gap-2">
            <Info className="w-4 h-4" />
            Jak naprawić:
          </h4>
          <p className="text-sm text-green-800 leading-relaxed">{errorData.suggestion}</p>
        </div>

        {/* Additional Context */}
        {Object.keys(additionalContext).length > 0 && (
          <details className="bg-gray-100 rounded-lg p-4 border border-gray-300">
            <summary className="font-semibold text-gray-900 cursor-pointer text-sm flex items-center gap-2">
              <ExternalLink className="w-4 h-4" />
              Dodatkowe informacje ({Object.keys(additionalContext).length})
            </summary>
            <div className="mt-3 space-y-2">
              {Object.entries(additionalContext).map(([key, value]) => (
                <div key={key} className="flex gap-2 text-xs">
                  <span className="font-mono text-gray-600 min-w-[120px]">{key}:</span>
                  <span className="font-mono text-gray-900 break-all">
                    {Array.isArray(value)
                      ? `[${value.length} items]`
                      : typeof value === 'object'
                      ? JSON.stringify(value)
                      : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </details>
        )}

        {/* Error Trace (only in debug mode) */}
        {errorData.error_trace && (
          <details className="bg-gray-900 text-gray-100 rounded-lg p-4">
            <summary className="font-mono text-xs cursor-pointer">Stack Trace (Debug)</summary>
            <pre className="mt-2 text-xs overflow-x-auto whitespace-pre-wrap">{errorData.error_trace}</pre>
          </details>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex gap-3">
        {showRetry && onRetry && (
          <button
            onClick={onRetry}
            className={`flex items-center gap-2 px-4 py-2 bg-${style.color}-600 hover:bg-${style.color}-700 text-white rounded-lg transition-colors font-medium`}
            style={{
              backgroundColor: style.color === 'blue' ? '#2563eb' : style.color === 'red' ? '#dc2626' : '#ca8a04',
            }}
          >
            <RefreshCw className="w-4 h-4" />
            Spróbuj ponownie
          </button>
        )}

        {/* Contextual action buttons based on error type */}
        {errorData.error_type === 'SCENARIO_NOT_FOUND' && (
          <a
            href="/optimize?tab=scenarios"
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors font-medium"
          >
            <ExternalLink className="w-4 h-4" />
            Przejdź do scenariuszy
          </a>
        )}

        {errorData.error_type === 'BASE_CONFIG_NOT_FOUND' && (
          <a
            href="/configurator"
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors font-medium"
          >
            <ExternalLink className="w-4 h-4" />
            Utwórz konfigurację
          </a>
        )}

        {errorData.error_type === 'TOO_MANY_ACTIVE_JOBS' && errorData.active_job_ids && (
          <button
            onClick={() => {
              // Show active jobs - implement this based on your UI
              console.log('Active jobs:', errorData.active_job_ids);
            }}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors font-medium"
          >
            <ExternalLink className="w-4 h-4" />
            Zobacz aktywne zadania
          </button>
        )}
      </div>
    </div>
  );
}

// Compact version for inline errors
export function InlineErrorDisplay({
  error,
  onRetry,
  className = '',
}: {
  error: any;
  onRetry?: () => void;
  className?: string;
}) {
  const parseError = (err: any): DetailedError | null => {
    if (!err) return null;
    if (typeof err === 'object' && err.error_type) return err as DetailedError;
    if (err.detail && typeof err.detail === 'object' && err.detail.error_type) return err.detail as DetailedError;
    return {
      error_type: 'ERROR',
      message: err.message || String(err),
      details: '',
      suggestion: '',
    };
  };

  const errorData = parseError(error);
  if (!errorData) return null;

  return (
    <div className={`flex items-center gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-3 ${className}`}>
      <AlertTriangle className="w-4 h-4 flex-shrink-0" />
      <span className="flex-1">{errorData.message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-red-600 hover:text-red-800 font-medium flex items-center gap-1"
        >
          <RefreshCw className="w-3 h-3" />
          Ponów
        </button>
      )}
    </div>
  );
}
