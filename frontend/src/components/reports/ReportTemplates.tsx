'use client'

import { useState, useEffect } from 'react'
import { ReportsAPI } from '@/lib/api-client'
import type { TemplatesResponse, ReportTemplate } from '@/types/api'

interface ReportTemplatesProps {
  onUseTemplate: (template: ReportTemplate) => void
}

const SYSTEM_TEMPLATES = [
  {
    id: 'weekly_performance',
    name: 'Weekly Performance Summary',
    description: 'Comprehensive weekly overview of system performance and optimization results',
    category: 'Performance',
    icon: '📊',
    usage_count: 245,
    rating_average: 4.7,
    is_featured: true
  },
  {
    id: 'monthly_fuel_savings',
    name: 'Monthly Fuel Savings Report',
    description: 'Detailed monthly analysis of fuel consumption improvements and cost savings',
    category: 'Financial',
    icon: '⛽',
    usage_count: 189,
    rating_average: 4.5,
    is_featured: true
  },
  {
    id: 'optimization_comparison',
    name: 'Optimization Comparison',
    description: 'Side-by-side comparison of different optimization scenarios and results',
    category: 'Analysis',
    icon: '⚙️',
    usage_count: 156,
    rating_average: 4.6,
    is_featured: false
  },
  {
    id: 'environmental_impact',
    name: 'Environmental Impact Report',
    description: 'CO₂ emissions reduction and environmental benefits tracking',
    category: 'Environmental',
    icon: '🌱',
    usage_count: 98,
    rating_average: 4.4,
    is_featured: false
  },
  {
    id: 'user_adoption',
    name: 'User Adoption Metrics',
    description: 'User engagement, feature adoption, and system usage analytics',
    category: 'Analytics',
    icon: '👥',
    usage_count: 87,
    rating_average: 4.3,
    is_featured: false
  },
  {
    id: 'technical_performance',
    name: 'Technical Performance Report',
    description: 'Detailed technical metrics including API performance and system health',
    category: 'Technical',
    icon: '🔧',
    usage_count: 76,
    rating_average: 4.5,
    is_featured: false
  }
]

export function ReportTemplates({ onUseTemplate }: ReportTemplatesProps) {
  const [templates, setTemplates] = useState<ReportTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')

  const categories = ['all', 'Performance', 'Financial', 'Analysis', 'Environmental', 'Analytics', 'Technical']

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      const data = await ReportsAPI.getTemplates({ limit: 100 }) as TemplatesResponse
      setTemplates(data.templates || [])
    } catch (error) {
      console.error('Error loading templates:', error)
      setTemplates([])
    } finally {
      setLoading(false)
    }
  }

  const handleUseTemplate = (template: any) => {
    // For system templates, create a mock template object
    const templateData = {
      id: template.id,
      name: template.name,
      description: template.description,
      template_config: {
        report_type: getReportTypeFromTemplate(template.id),
        default_filters: {},
        format: 'pdf'
      }
    }
    onUseTemplate(templateData as ReportTemplate)
  }

  const getReportTypeFromTemplate = (templateId: string) => {
    const typeMap: { [key: string]: string } = {
      'weekly_performance': 'system_performance',
      'monthly_fuel_savings': 'fuel_savings',
      'optimization_comparison': 'optimization_summary',
      'environmental_impact': 'environmental_impact',
      'user_adoption': 'user_activity',
      'technical_performance': 'system_performance'
    }
    return typeMap[templateId] || 'system_performance'
  }

  const filteredTemplates = SYSTEM_TEMPLATES.filter(template => {
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (template.description?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false)
    return matchesCategory && matchesSearch
  })

  const featuredTemplates = filteredTemplates.filter(t => t.is_featured)
  const regularTemplates = filteredTemplates.filter(t => !t.is_featured)

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i} className={i < Math.floor(rating) ? 'text-yellow-400' : 'text-gray-300'}>
        ⭐
      </span>
    ))
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-32 bg-gray-300 rounded-lg"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category === 'all' ? 'All Categories' : category}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Featured Templates */}
      {featuredTemplates.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            ⭐ Featured Templates
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {featuredTemplates.map((template) => (
              <div
                key={template.id}
                className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="text-3xl">{template.icon}</div>
                    <div>
                      <h4 className="font-semibold text-gray-900 text-lg">{template.name}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                          {template.category}
                        </span>
                        <div className="flex items-center gap-1">
                          {renderStars(template.rating_average)}
                          <span className="text-sm text-gray-600 ml-1">
                            ({template.rating_average})
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="text-2xl">⭐</div>
                </div>

                <p className="text-gray-700 mb-4 text-sm leading-relaxed">
                  {template.description}
                </p>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    Used {template.usage_count} times
                  </span>
                  <button
                    onClick={() => handleUseTemplate(template)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    Use Template
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Regular Templates */}
      {regularTemplates.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {featuredTemplates.length > 0 ? 'More Templates' : 'Available Templates'}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {regularTemplates.map((template) => (
              <div
                key={template.id}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="text-xl">{template.icon}</div>
                    <div>
                      <h4 className="font-medium text-gray-900">{template.name}</h4>
                      <span className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-full">
                        {template.category}
                      </span>
                    </div>
                  </div>
                </div>

                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                  {template.description}
                </p>

                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-1">
                    {renderStars(template.rating_average).slice(0, 3)}
                    <span className="text-gray-600 ml-1">
                      {template.rating_average}
                    </span>
                  </div>
                  <span className="text-gray-500">
                    {template.usage_count} uses
                  </span>
                </div>

                <button
                  onClick={() => handleUseTemplate(template)}
                  className="w-full mt-3 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Use Template
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredTemplates.length === 0 && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">📋</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || selectedCategory !== 'all'
              ? 'Try adjusting your search or filter criteria'
              : 'No report templates are available yet'
            }
          </p>
          {(searchTerm || selectedCategory !== 'all') && (
            <button
              onClick={() => {
                setSearchTerm('')
                setSelectedCategory('all')
              }}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Clear filters
            </button>
          )}
        </div>
      )}

      {/* Create Custom Template CTA */}
      <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <div className="text-3xl mb-3">➕</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Create Custom Template</h3>
        <p className="text-gray-600 mb-4">
          Build your own report template with custom configurations and filters
        </p>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors">
          Create Template
        </button>
      </div>
    </div>
  )
}