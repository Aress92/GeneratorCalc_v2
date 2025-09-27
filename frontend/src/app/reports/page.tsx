'use client'

import { useState, useEffect } from 'react'
import { withAuth } from '@/lib/auth'
import { hasPermission } from '@/lib/permissions'
import { User } from '@/types/auth'
import { ReportCard } from '@/components/reports/ReportCard'
import { ReportCreateModal } from '@/components/reports/ReportCreateModal'
import { DashboardMetrics } from '@/components/reports/DashboardMetrics'
import { ReportTemplates } from '@/components/reports/ReportTemplates'
import { ReportsAPI } from '@/lib/api-client'

interface Report {
  id: string
  title: string
  description?: string
  report_type: string
  status: 'pending' | 'generating' | 'completed' | 'failed'
  format: string
  progress_percentage: number
  generated_at?: string
  file_size_bytes?: number
  download_url?: string
  created_at: string
  updated_at: string
}

interface DashboardMetricsType {
  total_optimizations: number
  active_users: number
  fuel_savings_total: number
  co2_reduction_total: number
  system_uptime: number
  api_response_time_avg: number
  optimizations_this_month: number
  success_rate: number
}

function ReportsPage({ user }: { user: User }) {
  const [reports, setReports] = useState<Report[]>([])
  const [metrics, setMetrics] = useState<DashboardMetricsType | null>(null)
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'dashboard' | 'reports' | 'templates'>('dashboard')

  const canCreateReports = hasPermission(user, 'engineer')

  useEffect(() => {
    loadReports()
    loadDashboardMetrics()
  }, [])

  const loadReports = async () => {
    try {
      const data = await ReportsAPI.getReports()
      setReports(data.reports || [])
    } catch (error) {
      console.error('Error loading reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadDashboardMetrics = async () => {
    try {
      const data = await ReportsAPI.getDashboard()
      setMetrics(data)
    } catch (error) {
      console.error('Error loading dashboard metrics:', error)
    }
  }

  const handleCreateReport = async (reportData: any) => {
    try {
      await ReportsAPI.generateReport(reportData);
      setShowCreateModal(false);
      loadReports(); // Reload reports
    } catch (error) {
      console.error('Error creating report:', error);
    }
  };

  const handleDeleteReport = async (reportId: string) => {
    if (!confirm('Are you sure you want to delete this report?')) {
      return
    }

    try {
      await ReportsAPI.deleteReport(reportId)
      loadReports() // Reload reports
    } catch (error) {
      console.error('Error deleting report:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-64 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-300 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">System Reporting</h1>
              <p className="text-gray-600 mt-2">
                Monitor system performance, optimization results, and generate detailed reports
              </p>
            </div>
            {canCreateReports && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Create Report
              </button>
            )}
          </div>

          {/* Navigation Tabs */}
          <div className="mt-6 border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'dashboard', name: 'Dashboard', icon: '📊' },
                { id: 'reports', name: 'My Reports', icon: '📄' },
                { id: 'templates', name: 'Templates', icon: '📋' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span>{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'dashboard' && (
          <div>
            {metrics && <DashboardMetrics metrics={metrics} />}

            {/* Recent Reports */}
            <div className="mt-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Reports</h2>
              {reports.length === 0 ? (
                <div className="bg-white rounded-lg p-8 text-center">
                  <div className="text-4xl mb-4">📄</div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No reports yet</h3>
                  <p className="text-gray-600 mb-4">
                    Create your first report to start monitoring system performance
                  </p>
                  {canCreateReports && (
                    <button
                      onClick={() => setShowCreateModal(true)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                    >
                      Create Report
                    </button>
                  )}
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {reports.slice(0, 6).map((report) => (
                    <ReportCard
                      key={report.id}
                      report={report}
                      onDelete={canCreateReports ? handleDeleteReport : undefined}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'reports' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">My Reports</h2>
            {reports.length === 0 ? (
              <div className="bg-white rounded-lg p-8 text-center">
                <div className="text-4xl mb-4">📄</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No reports yet</h3>
                <p className="text-gray-600 mb-4">
                  Create your first report to start monitoring system performance
                </p>
                {canCreateReports && (
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                  >
                    Create Report
                  </button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {reports.map((report) => (
                  <ReportCard
                    key={report.id}
                    report={report}
                    onDelete={canCreateReports ? handleDeleteReport : undefined}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'templates' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Report Templates</h2>
            <ReportTemplates onUseTemplate={(template) => {
              // Pre-fill create modal with template data
              setSelectedTemplate(template)
              setShowCreateModal(true)
            }} />
          </div>
        )}

        {/* Create Report Modal */}
        {showCreateModal && (
          <ReportCreateModal
            onClose={() => {
              setShowCreateModal(false)
              setSelectedTemplate(null)
            }}
            onCreate={handleCreateReport}
            initialTemplate={selectedTemplate}
          />
        )}
      </div>
    </div>
  )
}

export default withAuth(ReportsPage)