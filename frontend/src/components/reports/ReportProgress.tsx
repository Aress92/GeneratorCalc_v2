'use client'

import { useState, useEffect, useRef } from 'react'

interface ReportProgressProps {
  reportId: string
  onComplete?: (reportId: string) => void
  onError?: (error: string) => void
}

interface ProgressEvent {
  type: 'progress' | 'error' | 'log' | 'checkpoint'
  report_id: string
  data: {
    status?: string
    progress_percentage?: number
    current_step?: string
    estimated_completion?: string
    error?: string
    message?: string
  }
}

export function ReportProgress({ reportId, onComplete, onError }: ReportProgressProps) {
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<string>('pending')
  const [currentStep, setCurrentStep] = useState<string>('')
  const [estimatedCompletion, setEstimatedCompletion] = useState<string>('')
  const [logs, setLogs] = useState<string[]>([])
  const [error, setError] = useState<string>('')

  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!reportId) return

    // Connect to Server-Sent Events
    const eventSource = new EventSource(`/api/v1/reports/reports/${reportId}/events`)
    eventSourceRef.current = eventSource

    eventSource.onmessage = (event) => {
      try {
        const progressEvent: ProgressEvent = JSON.parse(event.data)
        handleProgressEvent(progressEvent)
      } catch (error) {
        console.error('Error parsing progress event:', error)
      }
    }

    eventSource.onerror = (error) => {
      console.error('EventSource error:', error)
      eventSource.close()
    }

    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [reportId])

  const handleProgressEvent = (event: ProgressEvent) => {
    const { type, data } = event

    switch (type) {
      case 'progress':
        if (data.progress_percentage !== undefined) {
          setProgress(data.progress_percentage)
        }
        if (data.status) {
          setStatus(data.status)

          // Check if completed
          if (data.status === 'completed' && onComplete) {
            onComplete(reportId)
            eventSourceRef.current?.close()
          }
        }
        if (data.current_step) {
          setCurrentStep(data.current_step)
        }
        if (data.estimated_completion) {
          setEstimatedCompletion(data.estimated_completion)
        }
        break

      case 'error':
        const errorMessage = data.error || 'Unknown error occurred'
        setError(errorMessage)
        if (onError) {
          onError(errorMessage)
        }
        eventSourceRef.current?.close()
        break

      case 'log':
        if (data.message) {
          setLogs(prev => [...prev, data.message!])
        }
        break

      case 'checkpoint':
        if (data.message) {
          setLogs(prev => [...prev, `✓ ${data.message}`])
        }
        break
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600'
      case 'generating':
        return 'text-blue-600'
      case 'pending':
        return 'text-yellow-600'
      case 'failed':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅'
      case 'generating':
        return '⚙️'
      case 'pending':
        return '⏳'
      case 'failed':
        return '❌'
      default:
        return '📄'
    }
  }

  const formatEstimatedCompletion = (isoString: string) => {
    if (!isoString) return ''
    try {
      const date = new Date(isoString)
      const now = new Date()
      const diff = date.getTime() - now.getTime()

      if (diff <= 0) return 'Soon'

      const minutes = Math.ceil(diff / (1000 * 60))
      if (minutes < 60) {
        return `${minutes} minute${minutes === 1 ? '' : 's'}`
      }

      const hours = Math.ceil(minutes / 60)
      return `${hours} hour${hours === 1 ? '' : 's'}`
    } catch {
      return ''
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getStatusIcon(status)}</span>
          <div>
            <h3 className="font-medium text-gray-900">Report Generation</h3>
            <p className={`text-sm font-medium ${getStatusColor(status)}`}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </p>
          </div>
        </div>

        {status === 'generating' && (
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-600">{Math.round(progress)}%</div>
            {estimatedCompletion && (
              <div className="text-sm text-gray-600">
                ~{formatEstimatedCompletion(estimatedCompletion)} remaining
              </div>
            )}
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {status === 'generating' && (
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-blue-500 h-full rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Current Step */}
      {currentStep && status === 'generating' && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-blue-900">Current Step:</span>
          </div>
          <p className="text-sm text-blue-700 mt-1">{currentStep}</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-red-500">❌</span>
            <span className="text-sm font-medium text-red-900">Error:</span>
          </div>
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Completion Message */}
      {status === 'completed' && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-green-500">✅</span>
            <span className="text-sm font-medium text-green-900">Completed Successfully</span>
          </div>
          <p className="text-sm text-green-700">
            Your report has been generated and is ready for download.
          </p>
        </div>
      )}

      {/* Activity Log */}
      {logs.length > 0 && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-900">Activity Log</h4>
            <button
              onClick={() => setLogs([])}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              Clear
            </button>
          </div>

          <div className="max-h-32 overflow-y-auto bg-gray-50 rounded-lg p-3 space-y-1">
            {logs.slice(-10).map((log, index) => (
              <div key={index} className="text-xs text-gray-600 font-mono">
                <span className="text-gray-400">
                  {new Date().toLocaleTimeString()}
                </span>
                {' '}{log}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="mt-6 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-500">
            Report ID: {reportId}
          </div>

          {status === 'generating' && (
            <button
              onClick={() => {
                // Cancel report generation
                fetch(`/api/v1/reports/reports/${reportId}/cancel`, {
                  method: 'POST',
                  credentials: 'include'
                }).catch(console.error)
              }}
              className="text-xs text-red-600 hover:text-red-700 font-medium"
            >
              Cancel Generation
            </button>
          )}

          {status === 'completed' && (
            <button
              onClick={() => {
                // Trigger download
                window.open(`/api/v1/reports/reports/${reportId}/download`, '_blank')
              }}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium"
            >
              Download Report
            </button>
          )}
        </div>
      </div>
    </div>
  )
}