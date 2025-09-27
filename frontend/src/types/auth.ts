/**
 * Authentication and authorization types.
 *
 * Typy uwierzytelniania i autoryzacji.
 */

// Import necessary types
import type { User, LoginData } from '@/lib/auth';

// Re-export types from auth lib for convenience
export type {
  User,
  LoginData,
  LoginResponse,
  PasswordChangeData
} from '@/lib/auth';

export { UserRole } from '@/lib/auth';

export type { Permission } from '@/lib/permissions';

// Dashboard metrics types
export interface DashboardMetricsType {
  total_optimizations: number;
  active_users: number;
  fuel_savings_total: number;
  co2_reduction_total: number;
  system_uptime: number;
  api_response_time_avg: number;
  optimizations_this_month: number;
  success_rate: number;
}

// Report types
export interface Report {
  id: string;
  title: string;
  description?: string;
  report_type: string;
  format: string;
  status: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  file_path?: string;
  download_url?: string;
  progress_percentage?: number;
  error_message?: string;
}

// Component prop types
export interface ReportCardProps {
  report: Report;
  onDelete?: (reportId: string) => void;
}

// Auth context types
export interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginData) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

// Page component types
export interface ProtectedPageProps {
  user: User;
}

// API response types
export interface ApiError {
  detail: string;
  type?: string;
}

export interface ApiResponse<T = any> {
  data?: T;
  error?: ApiError;
  message?: string;
}

// Form types
export interface CreateReportForm {
  title: string;
  description: string;
  report_type: string;
  format: string;
  date_range: {
    start_date: string;
    end_date: string;
  };
  report_config: any;
  filters: any;
}

// Configuration types
export interface RegeneratorConfig {
  id?: string;
  name: string;
  type: string;
  geometry: {
    length: number;
    width: number;
    height: number;
    wall_thickness: number;
  };
  materials: {
    wall_material: string;
    checker_material: string;
    thermal_conductivity: number;
    specific_heat: number;
    density: number;
  };
  thermal: {
    gas_temp_inlet: number;
    gas_temp_outlet: number;
    ambient_temp: number;
  };
  flow: {
    mass_flow_rate: number;
    cycle_time: number;
  };
}