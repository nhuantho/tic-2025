import axios from 'axios';
import {
  APISpec,
  Endpoint,
  TestCase,
  TestResult,
  TestReport,
  GenerateTestCasesRequest,
  ExecuteTestRequest,
  ExecuteCurlRequest,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL + '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Specifications
export const apiSpecService = {
  import: async (file: File): Promise<APISpec> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api-specs/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (): Promise<APISpec[]> => {
    const response = await api.get('/api-specs/');
    return response.data;
  },

  get: async (id: number): Promise<APISpec> => {
    const response = await api.get(`/api-specs/${id}`);
    return response.data;
  },

  update: async (id: number, data: Partial<APISpec>): Promise<APISpec> => {
    const response = await api.put(`/api-specs/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api-specs/${id}`);
  },

  getEndpoints: async (id: number): Promise<Endpoint[]> => {
    const response = await api.get(`/api-specs/${id}/endpoints`);
    return response.data;
  },
};

// Test Cases
export const testCaseService = {
  generate: async (request: GenerateTestCasesRequest): Promise<TestCase[]> => {
    const response = await api.post('/test-cases/generate', request);
    return response.data;
  },

  generateRAG: async (request: GenerateTestCasesRequest): Promise<TestCase[]> => {
    const response = await api.post('/test-cases/generate-rag', request);
    return response.data;
  },

  generateRAGBulk: async (request: GenerateTestCasesRequest): Promise<TestCase[]> => {
    const response = await api.post('/test-cases/generate-rag-bulk', request);
    return response.data;
  },

  list: async (params?: {
    api_spec_id?: number;
    endpoint_id?: number;
    test_type?: string;
    priority?: string;
    sort?: string;
  }): Promise<TestCase[]> => {
    const response = await api.get('/test-cases/', { params });
    return response.data;
  },

  get: async (id: number): Promise<TestCase> => {
    const response = await api.get(`/test-cases/${id}`);
    return response.data;
  },

  update: async (id: number, data: Partial<TestCase>): Promise<TestCase> => {
    const response = await api.put(`/test-cases/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/test-cases/${id}`);
  },

  getResults: async (id: number): Promise<TestResult[]> => {
    const response = await api.get(`/test-cases/${id}/results`);
    return response.data;
  },
};

// Test Execution
export const testExecutionService = {
  run: async (request: {
    test_case_ids: number[];
    base_url: string;
    service_name?: string;
  }): Promise<{
    status: string;
    service_name: string;
    report_filepath: string;
    execution_summary: {
      total_tests: number;
      passed: number;
      failed: number;
      errors: number;
      success_rate: number;
      average_response_time: number;
    };
    results: any[];
    results_count: number;
  }> => {
    const response = await api.post('/test-execution/run', request);
    return response.data;
  },

  runMultiService: async (request: {
    service_configs: Record<string, { base_url: string; api_spec_id?: number }>;
    test_case_ids?: number[];
  }): Promise<{
    status: string;
    report_filepath: string;
    results: {
      results: any[];
      service_results: Record<string, any[]>;
      inter_service_report: {
        total_service_calls: number;
        service_calls: any[];
        service_dependencies: Record<string, string[]>;
        communication_patterns: {
          synchronous_calls: number;
          asynchronous_calls: number;
          error_propagation: number;
          circular_dependencies: string[];
        };
      };
    };
    results_count: number;
  }> => {
    const response = await api.post('/test-execution/multi-service', request);
    return response.data;
  },

  execute: async (request: ExecuteTestRequest): Promise<{
    report: TestReport;
    results_count: number;
  }> => {
    const response = await api.post('/test-execution/execute', request);
    return response.data;
  },

  executeCurl: async (request: ExecuteCurlRequest): Promise<{
    status: string;
    output?: string;
    error?: string;
    response_time: number;
  }> => {
    const response = await api.post('/test-execution/execute-curl', request);
    return response.data;
  },

  getResults: async (params?: {
    test_case_id?: number;
    status?: string;
  }): Promise<TestResult[]> => {
    const response = await api.get('/test-execution/results', { params });
    return response.data;
  },

  getResult: async (id: number): Promise<TestResult> => {
    const response = await api.get(`/test-execution/results/${id}`);
    return response.data;
  },

  getReports: async (serviceName?: string): Promise<{
    reports: Array<{
      service_name: string;
      filename: string;
      filepath: string;
      created_at: string;
    }>;
  }> => {
    const response = await api.get('/test-execution/reports', { 
      params: serviceName ? { service_name: serviceName } : {} 
    });
    return response.data;
  },

  getReportsByApiSpec: async (apiSpecName: string): Promise<{
    reports: Array<{
      filename: string;
      content: string;
      created_at: string;
    }>;
  }> => {
    const response = await api.get(`/test-execution/reports/${apiSpecName}`);
    return response.data;
  },
}; 