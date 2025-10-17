'use client'

import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface DashboardMetricsProps {
  metrics: {
    total_optimizations: number
    active_users: number
    fuel_savings_total: number
    co2_reduction_total: number
    system_uptime: number
    api_response_time_avg: number
    optimizations_this_month: number
    success_rate: number
  }
}

export function DashboardMetrics({ metrics }: DashboardMetricsProps) {
  // Sample trend data (in real implementation, this would come from the API)
  const optimizationTrends = [
    { date: '2024-01-01', optimizations: 12, success_rate: 85 },
    { date: '2024-01-02', optimizations: 18, success_rate: 92 },
    { date: '2024-01-03', optimizations: 15, success_rate: 88 },
    { date: '2024-01-04', optimizations: 22, success_rate: 95 },
    { date: '2024-01-05', optimizations: 19, success_rate: 91 },
    { date: '2024-01-06', optimizations: 25, success_rate: 93 },
    { date: '2024-01-07', optimizations: 21, success_rate: 89 }
  ]

  const fuelSavingsData = [
    { name: 'Geometry Optimization', value: 35, fill: '#3B82F6' },
    { name: 'Material Optimization', value: 28, fill: '#10B981' },
    { name: 'Operating Conditions', value: 22, fill: '#F59E0B' },
    { name: 'Comprehensive', value: 15, fill: '#EF4444' }
  ]

  const systemHealthData = [
    { metric: 'CPU Usage', value: 65, color: '#3B82F6' },
    { metric: 'Memory Usage', value: 72, color: '#10B981' },
    { metric: 'Disk Usage', value: 45, color: '#F59E0B' },
    { metric: 'Network I/O', value: 38, color: '#8B5CF6' }
  ]

  const formatNumber = (num: number, decimals = 0) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num)
  }

  const formatPercent = (num: number, decimals = 1) => {
    return `${formatNumber(num, decimals)}%`
  }

  return (
    <div className="space-y-6">
      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Optimizations</p>
              <p className="text-3xl font-bold text-gray-900">{formatNumber(metrics.total_optimizations)}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <div className="text-2xl">⚙️</div>
            </div>
          </div>
          <div className="mt-4 flex items-center">
            <span className="text-sm text-green-600 font-medium">
              +{formatNumber(metrics.optimizations_this_month)} this month
            </span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Average Fuel Savings</p>
              <p className="text-3xl font-bold text-green-600">{formatPercent(metrics.fuel_savings_total)}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <div className="text-2xl">⛽</div>
            </div>
          </div>
          <div className="mt-4 flex items-center">
            <span className="text-sm text-gray-600">
              CO₂ reduction: {formatPercent(metrics.co2_reduction_total)}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-3xl font-bold text-blue-600">{formatPercent(metrics.success_rate)}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <div className="text-2xl">✅</div>
            </div>
          </div>
          <div className="mt-4 flex items-center">
            <span className="text-sm text-gray-600">
              Active users: {formatNumber(metrics.active_users)}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Uptime</p>
              <p className="text-3xl font-bold text-green-600">{formatPercent(metrics.system_uptime)}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <div className="text-2xl">🟢</div>
            </div>
          </div>
          <div className="mt-4 flex items-center">
            <span className="text-sm text-gray-600">
              Avg response: {formatNumber(metrics.api_response_time_avg)}ms
            </span>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Optimization Trends */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Trends (Last 7 Days)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={optimizationTrends}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  className="text-xs"
                />
                <YAxis className="text-xs" />
                <Tooltip
                  formatter={(value, name) => [
                    name === 'optimizations' ? `${value} optimizations` : `${value}%`,
                    name === 'optimizations' ? 'Optimizations' : 'Success Rate'
                  ]}
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Area
                  type="monotone"
                  dataKey="optimizations"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.1}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fuel Savings by Type */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Fuel Savings by Optimization Type</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={fuelSavingsData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {fuelSavingsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value}%`, 'Fuel Savings']} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* System Health and Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="space-y-4">
            {systemHealthData.map((item) => (
              <div key={item.metric} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">{item.metric}</span>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-300"
                      style={{
                        width: `${item.value}%`,
                        backgroundColor: item.color
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12 text-right">
                    {item.value}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Success Rate Trend */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Success Rate Trend</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={optimizationTrends}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  className="text-xs"
                />
                <YAxis
                  domain={[80, 100]}
                  className="text-xs"
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip
                  formatter={(value) => [`${value}%`, 'Success Rate']}
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Line
                  type="monotone"
                  dataKey="success_rate"
                  stroke="#10B981"
                  strokeWidth={3}
                  dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#10B981', strokeWidth: 2, fill: '#fff' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="text-lg">📊</span>
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">Generate Performance Report</p>
              <p className="text-sm text-gray-600">System performance analysis</p>
            </div>
          </button>

          <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-lg">⛽</span>
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">Fuel Savings Report</p>
              <p className="text-sm text-gray-600">Optimization impact analysis</p>
            </div>
          </button>

          <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-lg">👥</span>
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">User Activity Report</p>
              <p className="text-sm text-gray-600">User engagement metrics</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}