'use client'

import { useState } from 'react'

import type { Report } from '@/types/api'

interface ReportCardProps {
  report: Report
  onDelete?: ((reportId: string) => Promise<void> | void) | undefined
}

export function ReportCard({ report, onDelete }: ReportCardProps) {
  const [isDownloading, setIsDownloading] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'generating':
        return 'bg-blue-100 text-blue-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
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

  const getReportTypeIcon = (type: string) => {
    switch (type) {
      case 'optimization_summary':
        return '⚙️'
      case 'fuel_savings':
        return '⛽'
      case 'system_performance':
        return '📊'
      case 'user_activity':
        return '👥'
      case 'import_analytics':
        return '📈'
      case 'environmental_impact':
        return '🌱'
      case 'financial_analysis':
        return '💰'
      default:
        return '📄'
    }
  }

  const formatReportType = (type: string) => {
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A'
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleDownload = async () => {
    if (report.status !== 'completed') return

    setIsDownloading(true)
    try {
      const response = await fetch(`/api/v1/reports/reports/${report.id}/download`, {
        credentials: 'include'
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `${report.title}.${report.format}`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        console.error('Download failed')
      }
    } catch (error) {
      console.error('Error downloading report:', error)
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="text-2xl">
            {getReportTypeIcon(report.report_type)}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-lg">{report.title}</h3>
            <p className="text-sm text-gray-600">{formatReportType(report.report_type)}</p>
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
            <span>{getStatusIcon(report.status)}</span>
            {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Description */}
      {report.description && (
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">{report.description}</p>
      )}

      {/* Progress Bar (for generating reports) */}
      {report.status === 'generating' && (
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Generation Progress</span>
            <span>{Math.round(report.progress_percentage)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${report.progress_percentage}%` }}
            />
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Format:</span>
          <span className="font-medium text-gray-900">{report.format.toUpperCase()}</span>
        </div>

        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Created:</span>
          <span className="font-medium text-gray-900">{formatDate(report.created_at)}</span>
        </div>

        {report.generated_at && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Generated:</span>
            <span className="font-medium text-gray-900">{formatDate(report.generated_at)}</span>
          </div>
        )}

        {report.file_size_bytes && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Size:</span>
            <span className="font-medium text-gray-900">{formatFileSize(report.file_size_bytes)}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-4 border-t border-gray-100">
        {report.status === 'completed' && (
          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
          >
            {isDownloading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Downloading...
              </>
            ) : (
              <>
                <span>📥</span>
                Download
              </>
            )}
          </button>
        )}

        {report.status === 'generating' && (
          <button
            disabled
            className="flex-1 bg-gray-100 text-gray-500 px-4 py-2 rounded-lg text-sm font-medium cursor-not-allowed flex items-center justify-center gap-2"
          >
            <div className="w-4 h-4 border-2 border-gray-500 border-t-transparent rounded-full animate-spin" />
            Generating...
          </button>
        )}

        {report.status === 'failed' && (
          <button
            className="flex-1 bg-red-100 text-red-700 px-4 py-2 rounded-lg text-sm font-medium cursor-not-allowed flex items-center justify-center gap-2"
          >
            <span>❌</span>
            Failed
          </button>
        )}

        {report.status === 'pending' && (
          <button
            disabled
            className="flex-1 bg-yellow-100 text-yellow-700 px-4 py-2 rounded-lg text-sm font-medium cursor-not-allowed flex items-center justify-center gap-2"
          >
            <span>⏳</span>
            Queued
          </button>
        )}

        {/* Delete Button */}
        {onDelete && (
          <button
            onClick={() => onDelete(report.id)}
            className="px-3 py-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Delete report"
          >
            🗑️
          </button>
        )}
      </div>
    </div>
  )
}