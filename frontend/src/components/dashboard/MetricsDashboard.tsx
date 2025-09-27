'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import MetricCard from './MetricCard';
import DashboardChart from './DashboardChart';
import { ReportsAPI } from '@/lib/api-client';
import {
  Activity,
  Users,
  Fuel,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  Zap,
  RefreshCw
} from 'lucide-react';

interface DashboardMetrics {
  total_optimizations: number;
  active_users: number;
  fuel_savings_total: number;
  co2_reduction_total: number;
  system_uptime: number;
  api_response_time_avg: number;
  optimizations_this_month: number;
  success_rate: number;
}

interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Sample chart data - in production this would come from API
  const optimizationTrends: ChartDataPoint[] = [
    { name: 'Jan', value: 12, success: 10 },
    { name: 'Feb', value: 19, success: 16 },
    { name: 'Mar', value: 15, success: 14 },
    { name: 'Apr', value: 22, success: 20 },
    { name: 'May', value: 28, success: 25 },
    { name: 'Jun', value: 35, success: 32 }
  ];

  const fuelSavingsData: ChartDataPoint[] = [
    { name: 'Regenerator A', value: 12.5 },
    { name: 'Regenerator B', value: 8.3 },
    { name: 'Regenerator C', value: 15.7 },
    { name: 'Regenerator D', value: 6.2 },
    { name: 'Regenerator E', value: 11.9 }
  ];

  const systemHealthData: ChartDataPoint[] = [
    { name: 'API Response', value: 95 },
    { name: 'Database', value: 98 },
    { name: 'Celery Workers', value: 92 },
    { name: 'Redis Cache', value: 99 }
  ];

  const optimizationTypesData: ChartDataPoint[] = [
    { name: 'Fuel Efficiency', value: 45 },
    { name: 'Heat Transfer', value: 30 },
    { name: 'Material Selection', value: 15 },
    { name: 'Geometric', value: 10 }
  ];

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);

      // In production, this would be: const data = await ReportsAPI.getDashboard();
      // For now, simulating with realistic data
      const simulatedMetrics: DashboardMetrics = {
        total_optimizations: 156,
        active_users: 12,
        fuel_savings_total: 11.8,
        co2_reduction_total: 1250,
        system_uptime: 99.5,
        api_response_time_avg: 145,
        optimizations_this_month: 28,
        success_rate: 89.7
      };

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      setMetrics(simulatedMetrics);
      setLastRefresh(new Date());
    } catch (err) {
      console.error('Failed to fetch dashboard metrics:', err);
      setError('Failed to load dashboard metrics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchMetrics();
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchMetrics();
    }, 30000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  if (error) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-8">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Metrics</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={handleRefresh}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Dashboard Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">System Dashboard</h2>
          <p className="text-gray-600">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant={autoRefresh ? "default" : "outline"}
            size="sm"
            onClick={toggleAutoRefresh}
          >
            <Zap className="h-4 w-4 mr-1" />
            Auto-refresh
          </Button>
          <Button size="sm" onClick={handleRefresh} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Optimizations"
          value={metrics?.total_optimizations || 0}
          icon={<Activity />}
          color="blue"
          loading={loading}
          change={15.3}
          changeType="increase"
        />
        <MetricCard
          title="Active Users"
          value={metrics?.active_users || 0}
          icon={<Users />}
          color="green"
          loading={loading}
          change={8.1}
          changeType="increase"
        />
        <MetricCard
          title="Avg. Fuel Savings"
          value={metrics?.fuel_savings_total.toFixed(1) || '0.0'}
          unit="%"
          icon={<Fuel />}
          color="orange"
          loading={loading}
          change={2.4}
          changeType="increase"
        />
        <MetricCard
          title="Success Rate"
          value={metrics?.success_rate.toFixed(1) || '0.0'}
          unit="%"
          icon={<CheckCircle2 />}
          color="green"
          loading={loading}
          change={1.2}
          changeType="increase"
        />
      </div>

      {/* System Health Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="System Uptime"
          value={metrics?.system_uptime.toFixed(1) || '0.0'}
          unit="%"
          icon={<TrendingUp />}
          color="purple"
          loading={loading}
        />
        <MetricCard
          title="API Response Time"
          value={metrics?.api_response_time_avg || 0}
          unit="ms"
          icon={<Clock />}
          color="blue"
          loading={loading}
          change={5.2}
          changeType="decrease"
        />
        <MetricCard
          title="This Month"
          value={metrics?.optimizations_this_month || 0}
          icon={<Activity />}
          color="green"
          loading={loading}
          change={23.7}
          changeType="increase"
        />
        <MetricCard
          title="CO₂ Reduction"
          value={metrics?.co2_reduction_total || 0}
          unit="tons"
          icon={<CheckCircle2 />}
          color="green"
          loading={loading}
          change={18.9}
          changeType="increase"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DashboardChart
          title="Optimization Trends (Last 6 Months)"
          data={optimizationTrends}
          type="line"
          height={300}
          color="#3B82F6"
          dataKey="value"
          xAxisKey="name"
          yAxisLabel="Count"
          loading={loading}
        />

        <DashboardChart
          title="Fuel Savings by Regenerator"
          data={fuelSavingsData}
          type="bar"
          height={300}
          color="#10B981"
          dataKey="value"
          xAxisKey="name"
          yAxisLabel="Savings (%)"
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DashboardChart
          title="System Health Status"
          data={systemHealthData}
          type="area"
          height={300}
          color="#8B5CF6"
          dataKey="value"
          xAxisKey="name"
          yAxisLabel="Health (%)"
          loading={loading}
        />

        <DashboardChart
          title="Optimization Types Distribution"
          data={optimizationTypesData}
          type="pie"
          height={300}
          colors={['#3B82F6', '#10B981', '#F59E0B', '#EF4444']}
          dataKey="value"
          loading={loading}
          showLegend={true}
        />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="justify-start">
              <Activity className="h-4 w-4 mr-2" />
              View All Optimizations
            </Button>
            <Button variant="outline" className="justify-start">
              <Users className="h-4 w-4 mr-2" />
              Manage Users
            </Button>
            <Button variant="outline" className="justify-start">
              <TrendingUp className="h-4 w-4 mr-2" />
              Generate Report
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}