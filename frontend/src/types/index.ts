export interface APISpec {
  id: number;
  name: string;
  version?: string;
  description?: string;
  file_path: string;
  file_type: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Endpoint {
  id: number;
  api_spec_id: number;
  path: string;
  method: string;
  summary: string;
  description: string;
  parameters: any[];
  request_body: any;
  responses: any;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface TestCase {
  id: number;
  api_spec_id: number;
  endpoint_id: number;
  name: string;
  description: string;
  test_type: 'manual' | 'automated' | 'ai_generated';
  priority: 'low' | 'medium' | 'high' | 'critical';
  input_data: any;
  expected_output: any;
  expected_status_code: number;
  curl_command: string;
  test_script: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TestResult {
  id: number;
  test_case_id: number;
  status: 'passed' | 'failed' | 'error';
  response_status_code: number;
  response_body: string;
  response_time: number;
  error_message: string;
  execution_log: string;
  created_at: string;
  updated_at: string;
}

export interface TestReport {
  summary: {
    total_tests: number;
    passed: number;
    failed: number;
    errors: number;
    success_rate: number;
    average_response_time: number;
  };
  results: any[];
  timestamp: string;
}

export interface GenerateTestCasesRequest {
  api_spec_id: number;
  base_url: string;
}

export interface ExecuteTestRequest {
  test_case_ids: number[];
  base_url: string;
}

export interface ExecuteCurlRequest {
  curl_command: string;
} 