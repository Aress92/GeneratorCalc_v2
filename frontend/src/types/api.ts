/**
 * API response types for Forglass Regenerator Optimizer
 */

// Base API response structure
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  success?: boolean;
}

// Optimization types
export interface OptimizationScenario {
  id: string;
  name: string;
  description?: string;
  scenario_type: string;
  base_configuration_id: string;
  objective: string;
  algorithm: string;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OptimizationJob {
  id: string;
  scenario_id: string;
  job_name: string | null;
  status: string;
  progress_percentage: number;
  current_iteration: number;
  started_at: string | null;
  completed_at: string | null;
  runtime_seconds: number | null;
  estimated_completion_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface ScenariosResponse {
  scenarios: OptimizationScenario[];
  total: number;
}

export interface JobsResponse {
  jobs: OptimizationJob[];
  total: number;
}

// Optimization Results types
export interface PerformanceMetrics {
  thermal_efficiency: number;
  heat_transfer_rate: number;
  pressure_drop: number;
  ntu_value: number;
  effectiveness: number;
  heat_transfer_coefficient: number;
  surface_area: number;
  wall_heat_loss?: number;
}

export interface EconomicAnalysis {
  fuel_savings_percentage?: number;
  co2_reduction_percentage?: number;
  annual_cost_savings?: number;
  payback_period_months?: number;
  capital_cost_estimate?: number;
  net_present_value?: number;
}

export interface SensitivityAnalysis {
  variable_sensitivities: Record<string, number>;
  critical_variables: string[];
  robustness_score: number;
  uncertainty_range: Record<string, number>;
}

export interface OptimizationResult {
  id: string;
  job_id: string;
  optimized_configuration: Record<string, any>;
  design_variables_final: Record<string, number>;
  objective_value: number;
  objective_components?: Record<string, number>;
  constraint_violations?: Record<string, number>;
  baseline_metrics: PerformanceMetrics;
  optimized_metrics: PerformanceMetrics;
  improvement_percentages: Record<string, number>;
  economic_analysis?: EconomicAnalysis;
  thermal_efficiency?: number;
  pressure_drop?: number;
  heat_transfer_coefficient?: number;
  ntu_value?: number;
  optimized_geometry?: Record<string, any>;
  volume_changes?: Record<string, number>;
  surface_area_changes?: Record<string, number>;
  material_recommendations?: Array<Record<string, any>>;
  material_cost_impact?: Record<string, number>;
  sensitivity_analysis?: SensitivityAnalysis;
  solution_feasibility?: number;
  optimization_confidence?: number;
  created_at: string;
  updated_at: string;
}

export interface OptimizationIteration {
  id: string;
  job_id: string;
  iteration_number: number;
  function_evaluation: number;
  design_variables: Record<string, number>;
  objective_value: number;
  objective_components?: Record<string, number>;
  constraint_values?: Record<string, number>;
  constraint_violations?: Record<string, number>;
  performance_metrics?: Record<string, any>;
  evaluation_time_seconds?: number;
  is_feasible: boolean;
  is_improvement: boolean;
  created_at: string;
}

// Reports types
export interface Report {
  id: string;
  title: string;
  description?: string;
  report_type: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  format: string;
  progress_percentage: number;
  generated_at?: string;
  file_size_bytes?: number;
  download_url?: string;
  created_at: string;
  updated_at: string;
}

export interface ReportsResponse {
  reports: Report[];
  total: number;
}

export interface DashboardMetrics {
  total_optimizations: number;
  active_users: number;
  fuel_savings_total: number;
  co2_reduction_total: number;
  system_uptime: number;
  api_response_time_avg: number;
  optimizations_this_month: number;
  success_rate: number;
}

// Chart data types
export interface ChartDataPoint {
  name: string;
  value: number;
  percent?: number;
  [key: string]: any;
}

// Templates types
export interface ReportTemplate {
  id: string;
  name: string;
  description?: string;
  category?: string;
  template_config: any;
  default_filters?: any;
  usage_count: number;
  rating_average?: number;
  rating_count: number;
  is_active: boolean;
  is_public: boolean;
  is_system: boolean;
  version: string;
  created_at: string;
  updated_at: string;
}

export interface TemplatesResponse {
  templates: ReportTemplate[];
  total: number;
}

// Generic pagination response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}