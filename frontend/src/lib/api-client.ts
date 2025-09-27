/**
 * Centralized API client for all backend requests.
 *
 * Scentralizowany klient API dla wszystkich żądań do backend-u.
 */

// API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Generic API client with proper base URL and credentials
 */
export class ApiClient {
  private static baseURL = `${API_BASE_URL}/api/v1`;

  /**
   * Make authenticated API request
   */
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Include HttpOnly cookies
      ...options,
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API request failed: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * GET request
   */
  static async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const searchParams = params ? new URLSearchParams(params).toString() : '';
    const url = searchParams ? `${endpoint}?${searchParams}` : endpoint;

    return this.request<T>(url, { method: 'GET' });
  }

  /**
   * POST request
   */
  static async post<T>(endpoint: string, data?: any): Promise<T> {
    const options: RequestInit = {
      method: 'POST',
    };
    if (data) {
      options.body = JSON.stringify(data);
    }
    return this.request<T>(endpoint, options);
  }

  /**
   * PUT request
   */
  static async put<T>(endpoint: string, data?: any): Promise<T> {
    const options: RequestInit = {
      method: 'PUT',
    };
    if (data) {
      options.body = JSON.stringify(data);
    }
    return this.request<T>(endpoint, options);
  }

  /**
   * DELETE request
   */
  static async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

/**
 * Materials API
 */
export class MaterialsAPI {
  /**
   * Get materials with optional filters
   */
  static async getMaterials(params?: {
    search?: string;
    material_type?: string;
    category?: string;
    application?: string;
    manufacturer?: string;
    is_active?: boolean;
    is_standard?: boolean;
    limit?: number;
    offset?: number;
  }) {
    return ApiClient.get('/materials/', params);
  }

  /**
   * Get material by ID
   */
  static async getMaterial(materialId: string) {
    return ApiClient.get(`/materials/${materialId}`);
  }

  /**
   * Get materials by type
   */
  static async getMaterialsByType(materialType: string, isActive: boolean = true) {
    return ApiClient.get(`/materials/types/${materialType}`, { is_active: isActive });
  }

  /**
   * Get popular/standard materials
   */
  static async getPopularMaterials(limit: number = 20) {
    return ApiClient.get('/materials/popular/standard', { limit });
  }

  /**
   * Create new material (Engineer/Admin only)
   */
  static async createMaterial(materialData: any) {
    return ApiClient.post('/materials/', materialData);
  }

  /**
   * Update material (Engineer/Admin only)
   */
  static async updateMaterial(materialId: string, materialData: any) {
    return ApiClient.put(`/materials/${materialId}`, materialData);
  }

  /**
   * Delete material (Engineer/Admin only)
   */
  static async deleteMaterial(materialId: string) {
    return ApiClient.delete(`/materials/${materialId}`);
  }
}

/**
 * Regenerators API
 */
export class RegeneratorsAPI {
  /**
   * Get user's regenerator configurations
   */
  static async getRegenerators(params?: {
    skip?: number;
    limit?: number;
  }) {
    return ApiClient.get('/regenerators/', params);
  }

  /**
   * Get regenerator by ID
   */
  static async getRegenerator(regeneratorId: string) {
    return ApiClient.get(`/regenerators/${regeneratorId}`);
  }

  /**
   * Create new regenerator configuration
   */
  static async createRegenerator(configData: any) {
    return ApiClient.post('/regenerators/', configData);
  }

  /**
   * Update regenerator configuration
   */
  static async updateRegenerator(regeneratorId: string, configData: any) {
    return ApiClient.put(`/regenerators/${regeneratorId}`, configData);
  }

  /**
   * Delete regenerator configuration
   */
  static async deleteRegenerator(regeneratorId: string) {
    return ApiClient.delete(`/regenerators/${regeneratorId}`);
  }
}

/**
 * Optimization API
 */
export class OptimizationAPI {
  /**
   * Create optimization scenario
   */
  static async createScenario(scenarioData: any) {
    return ApiClient.post('/optimize/scenarios', scenarioData);
  }

  /**
   * Get optimization scenarios
   */
  static async getScenarios(params?: { skip?: number; limit?: number }) {
    return ApiClient.get('/optimize/scenarios', params);
  }

  /**
   * Get optimization scenario by ID
   */
  static async getScenario(scenarioId: string) {
    return ApiClient.get(`/optimize/scenarios/${scenarioId}`);
  }

  /**
   * Create optimization job
   */
  static async createJob(scenarioId: string, jobData?: any) {
    return ApiClient.post(`/optimize/scenarios/${scenarioId}/jobs`, jobData);
  }

  /**
   * Get optimization jobs
   */
  static async getJobs(scenarioId: string, params?: { skip?: number; limit?: number }) {
    return ApiClient.get(`/optimize/scenarios/${scenarioId}/jobs`, params);
  }

  /**
   * Get optimization job by ID
   */
  static async getJob(scenarioId: string, jobId: string) {
    return ApiClient.get(`/optimize/scenarios/${scenarioId}/jobs/${jobId}`);
  }

  /**
   * Cancel optimization job
   */
  static async cancelJob(scenarioId: string, jobId: string) {
    return ApiClient.post(`/optimize/scenarios/${scenarioId}/jobs/${jobId}/cancel`);
  }

  /**
   * Get optimization results
   */
  static async getResults(scenarioId: string, params?: { skip?: number; limit?: number }) {
    return ApiClient.get(`/optimize/scenarios/${scenarioId}/results`, params);
  }
}

/**
 * Import API
 */
export class ImportAPI {
  /**
   * Preview uploaded file
   */
  static async previewFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/v1/import/preview`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to preview file');
    }

    return await response.json();
  }

  /**
   * Run dry-run import validation
   */
  static async dryRun(file: File, importType: string, columnMapping: any[]) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('import_type', importType);
    formData.append('column_mapping', JSON.stringify(columnMapping));

    const response = await fetch(`${API_BASE_URL}/api/v1/import/dry-run-simple`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Dry run failed');
    }

    return await response.json();
  }

  /**
   * Create import job
   */
  static async createJob(file: File, jobData: any) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_data', JSON.stringify(jobData));

    const response = await fetch(`${API_BASE_URL}/api/v1/import/jobs`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Import failed');
    }

    return await response.json();
  }

  /**
   * Get import jobs
   */
  static async getJobs(params?: { skip?: number; limit?: number }) {
    return ApiClient.get('/import/jobs', params);
  }

  /**
   * Get import job by ID
   */
  static async getJob(jobId: string) {
    return ApiClient.get(`/import/jobs/${jobId}`);
  }

  /**
   * Get import templates
   */
  static async getTemplates() {
    return ApiClient.get('/import/templates');
  }
}

/**
 * Reports API
 */
export class ReportsAPI {
  /**
   * Generate report
   */
  static async generateReport(reportData: any) {
    return ApiClient.post('/reports/', reportData);
  }

  /**
   * Get reports
   */
  static async getReports(params?: { skip?: number; limit?: number }) {
    return ApiClient.get('/reports/', params);
  }

  /**
   * Get report by ID
   */
  static async getReport(reportId: string) {
    return ApiClient.get(`/reports/${reportId}`);
  }

  /**
   * Get dashboard metrics
   */
  static async getDashboard() {
    return ApiClient.get('/reports/dashboard/metrics');
  }

  /**
   * Download report file
   */
  static async downloadReport(reportId: string, format: 'pdf' | 'xlsx' | 'csv') {
    const response = await fetch(`${API_BASE_URL}/api/v1/reports/${reportId}/download/${format}`, {
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Download failed: ${response.status}`);
    }

    return response.blob();
  }
}