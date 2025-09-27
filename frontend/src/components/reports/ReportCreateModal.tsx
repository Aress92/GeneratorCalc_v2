'use client'

import { useState, useEffect } from 'react'
import { OptimizationAPI } from '@/lib/api-client'

interface ReportCreateModalProps {
  onClose: () => void
  onCreate: (reportData: any) => void
  initialTemplate?: any
}

interface OptimizationScenario {
  id: string
  name: string
  scenario_type: string
  created_at: string
}

const REPORT_TYPES = [
  {
    id: 'optimization_summary',
    name: 'Optimization Summary',
    description: 'Comprehensive analysis of optimization results and performance metrics',
    icon: '⚙️'
  },
  {
    id: 'fuel_savings',
    name: 'Fuel Savings Analysis',
    description: 'Detailed breakdown of fuel consumption improvements and cost savings',
    icon: '⛽'
  },
  {
    id: 'system_performance',
    name: 'System Performance',
    description: 'System health, uptime, and performance metrics overview',
    icon: '📊'
  },
  {
    id: 'user_activity',
    name: 'User Activity',
    description: 'User engagement, activity patterns, and system usage statistics',
    icon: '👥'
  },
  {
    id: 'import_analytics',
    name: 'Import Analytics',
    description: 'Data import success rates, processing times, and quality metrics',
    icon: '📈'
  },
  {
    id: 'environmental_impact',
    name: 'Environmental Impact',
    description: 'CO₂ emissions reduction and environmental benefits analysis',
    icon: '🌱'
  },
  {
    id: 'financial_analysis',
    name: 'Financial Analysis',
    description: 'Cost-benefit analysis, ROI calculations, and financial impact',
    icon: '💰'
  }
]

const REPORT_FORMATS = [
  { id: 'pdf', name: 'PDF Document', icon: '📄' },
  { id: 'excel', name: 'Excel Spreadsheet', icon: '📊' },
  { id: 'csv', name: 'CSV Data', icon: '📋' },
  { id: 'json', name: 'JSON Data', icon: '🔧' }
]

export function ReportCreateModal({ onClose, onCreate, initialTemplate }: ReportCreateModalProps) {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    report_type: '',
    format: 'pdf',
    date_range: {
      start_date: '',
      end_date: ''
    },
    report_config: {} as any,
    filters: {}
  })

  const [scenarios, setScenarios] = useState<OptimizationScenario[]>([])
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([])

  useEffect(() => {
    loadScenarios()

    // Set default date range (last 30 days)
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - 30)

    // Initialize form with template data if provided
    const initialData = {
      title: initialTemplate?.name ? `${initialTemplate.name} - ${new Date().toLocaleDateString()}` : '',
      description: initialTemplate?.description || '',
      report_type: initialTemplate?.template_config?.report_type || '',
      format: initialTemplate?.template_config?.format || 'pdf',
      date_range: {
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
      },
      report_config: initialTemplate?.template_config || {},
      filters: initialTemplate?.default_filters || {}
    }

    setFormData(initialData)
  }, [initialTemplate])

  const loadScenarios = async () => {
    try {
      const data = await OptimizationAPI.getScenarios()
      setScenarios(data.scenarios || [])
    } catch (error) {
      console.error('Error loading scenarios:', error)
    }
  }

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1)
    } else {
      handleCreate()
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  const handleCreate = () => {
    // Build report config based on report type
    let reportConfig = { ...formData.report_config }

    if (formData.report_type === 'optimization_summary') {
      reportConfig = {
        scenario_ids: selectedScenarios,
        metrics: ['fuel_savings', 'co2_reduction', 'thermal_efficiency'],
        include_iterations: false,
        include_comparison: true
      }
    } else if (formData.report_type === 'fuel_savings') {
      reportConfig = {
        baseline_period: {
          start_date: formData.date_range.start_date,
          end_date: formData.date_range.end_date
        },
        comparison_period: {
          start_date: formData.date_range.start_date,
          end_date: formData.date_range.end_date
        },
        include_economic_analysis: true,
        currency: 'USD'
      }
    } else if (formData.report_type === 'system_performance') {
      reportConfig = {
        metrics: ['api_response_time', 'optimization_success_rate', 'user_activity'],
        time_period: formData.date_range,
        aggregation: 'daily',
        include_trends: true
      }
    }

    const reportData = {
      ...formData,
      report_config: reportConfig
    }

    onCreate(reportData)
  }

  const selectedReportType = REPORT_TYPES.find(type => type.id === formData.report_type)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Create New Report</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              ✕
            </button>
          </div>

          {/* Progress indicator */}
          <div className="mt-4 flex items-center gap-2">
            {[1, 2, 3].map((stepNum) => (
              <div key={stepNum} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  stepNum === step ? 'bg-blue-600 text-white' :
                  stepNum < step ? 'bg-green-500 text-white' :
                  'bg-gray-200 text-gray-600'
                }`}>
                  {stepNum < step ? '✓' : stepNum}
                </div>
                {stepNum < 3 && (
                  <div className={`w-12 h-1 mx-2 ${stepNum < step ? 'bg-green-500' : 'bg-gray-200'}`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Step 1: Report Type Selection */}
          {step === 1 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Report Type</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {REPORT_TYPES.map((type) => (
                  <button
                    key={type.id}
                    onClick={() => setFormData(prev => ({ ...prev, report_type: type.id }))}
                    className={`p-4 border-2 rounded-lg text-left transition-colors ${
                      formData.report_type === type.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">{type.icon}</span>
                      <h4 className="font-medium text-gray-900">{type.name}</h4>
                    </div>
                    <p className="text-sm text-gray-600">{type.description}</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Basic Information */}
          {step === 2 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Report Details</h3>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Report Title *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder={`${selectedReportType?.name} Report - ${new Date().toLocaleDateString()}`}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Optional description for this report..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Export Format
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {REPORT_FORMATS.map((format) => (
                    <button
                      key={format.id}
                      onClick={() => setFormData(prev => ({ ...prev, format: format.id }))}
                      className={`p-3 border-2 rounded-lg text-center transition-colors ${
                        formData.format === format.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="text-xl mb-1">{format.icon}</div>
                      <div className="text-sm font-medium">{format.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.date_range.start_date}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      date_range: { ...prev.date_range, start_date: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={formData.date_range.end_date}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      date_range: { ...prev.date_range, end_date: e.target.value }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Configuration */}
          {step === 3 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Configuration</h3>

              {formData.report_type === 'optimization_summary' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Optimization Scenarios
                  </label>
                  <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-lg">
                    {scenarios.map((scenario) => (
                      <label
                        key={scenario.id}
                        className="flex items-center p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                      >
                        <input
                          type="checkbox"
                          checked={selectedScenarios.includes(scenario.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedScenarios(prev => [...prev, scenario.id])
                            } else {
                              setSelectedScenarios(prev => prev.filter(id => id !== scenario.id))
                            }
                          }}
                          className="mr-3"
                        />
                        <div>
                          <div className="font-medium text-gray-900">{scenario.name}</div>
                          <div className="text-sm text-gray-600">
                            {scenario.scenario_type} • Created {new Date(scenario.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      </label>
                    ))}
                    {scenarios.length === 0 && (
                      <div className="p-8 text-center text-gray-500">
                        No optimization scenarios found. Create some scenarios first to include in reports.
                      </div>
                    )}
                  </div>
                  {selectedScenarios.length === 0 && scenarios.length > 0 && (
                    <p className="text-sm text-amber-600 mt-2">
                      ⚠️ Select at least one scenario to include in the report
                    </p>
                  )}
                </div>
              )}

              {formData.report_type === 'fuel_savings' && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Fuel Savings Analysis Configuration</h4>
                  <p className="text-sm text-blue-700">
                    This report will analyze fuel savings and cost benefits from optimizations
                    within the selected date range. Economic analysis will be included with USD currency.
                  </p>
                </div>
              )}

              {formData.report_type === 'system_performance' && (
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-900 mb-2">System Performance Configuration</h4>
                  <p className="text-sm text-green-700">
                    This report will include API response times, optimization success rates,
                    user activity metrics, and performance trends for the selected period.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 flex items-center justify-between">
          <button
            onClick={handleBack}
            disabled={step === 1}
            className="px-4 py-2 text-gray-600 disabled:text-gray-400 disabled:cursor-not-allowed"
          >
            Back
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>

            <button
              onClick={handleNext}
              disabled={
                !formData.report_type ||
                (step === 2 && !formData.title) ||
                (step === 3 && formData.report_type === 'optimization_summary' && selectedScenarios.length === 0)
              }
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-medium transition-colors"
            >
              {step === 3 ? 'Create Report' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}