import React, { useState } from 'react';
import { 
  Table, 
  Button, 
  Modal, 
  message, 
  Space, 
  Tag, 
  Typography,
  Card,
  Select,
  Input,
  Form,
  Descriptions,
  Collapse,
  Progress,
  Alert,
  Divider,
  Radio
} from 'antd';
import { 
  PlusOutlined, 
  EyeOutlined, 
  DeleteOutlined,
  PlayCircleOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { testCaseService, testExecutionService, apiSpecService } from '../services/api';
import { TestCase, APISpec } from '../types';

const { Title } = Typography;
const { Option } = Select;
const { Panel } = Collapse;

const TestCases: React.FC = () => {
  const [isGenerateModalVisible, setIsGenerateModalVisible] = useState(false);
  const [isRAGGeneration, setIsRAGGeneration] = useState(false);
  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(null);
  const [isDetailModalVisible, setIsDetailModalVisible] = useState(false);
  const [isRunModalVisible, setIsRunModalVisible] = useState(false);
  const [runResults, setRunResults] = useState<any>(null);
  const [filters, setFilters] = useState({
    api_spec_id: undefined,
    test_type: undefined,
    priority: undefined,
  });
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([]);
  const queryClient = useQueryClient();

  const { data: testCases, isLoading } = useQuery(
    ['testCases', filters],
    () => testCaseService.list({ ...filters, sort: 'priority' })
  );

  const { data: apiSpecs } = useQuery('apiSpecs', () => apiSpecService.list());

  const generateMutation = useMutation(testCaseService.generate, {
    onSuccess: () => {
      message.success('Test cases generated successfully');
      setIsGenerateModalVisible(false);
      queryClient.invalidateQueries('testCases');
    },
    onError: (error: any) => {
      message.error(`Generation failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const generateRAGMutation = useMutation(testCaseService.generateRAG, {
    onSuccess: () => {
      message.success('Smart test cases generated successfully! (Automated + AI if available)');
      setIsGenerateModalVisible(false);
      queryClient.invalidateQueries('testCases');
    },
    onError: (error: any) => {
      message.error(`Smart generation failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const generateRAGBulkMutation = useMutation(testCaseService.generateRAGBulk, {
    onSuccess: () => {
      message.success('Smart test cases generated successfully for all endpoints! (Automated + AI if available)');
      setIsGenerateModalVisible(false);
      queryClient.invalidateQueries('testCases');
    },
    onError: (error: any) => {
      message.error(`Bulk smart generation failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const deleteMutation = useMutation(testCaseService.delete, {
    onSuccess: () => {
      message.success('Test case deleted successfully');
      queryClient.invalidateQueries('testCases');
    },
    onError: (error: any) => {
      message.error(`Delete failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const runTestsMutation = useMutation(testExecutionService.run, {
    onSuccess: (data) => {
      message.success('Test execution completed successfully');
      setRunResults(data);
      setIsRunModalVisible(true);
      queryClient.invalidateQueries('testCases');
    },
    onError: (error: any) => {
      message.error(`Test execution failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleGenerate = (values: any) => {
    // Always use smart generation (automated first, then AI if available)
    if (values.generation_mode === 'bulk') {
      // Use bulk generation for all endpoints
      const bulkValues = {
        api_spec_id: values.api_spec_id,
        base_url: values.base_url
      };
      generateRAGBulkMutation.mutate(bulkValues);
    } else {
      // Use specific endpoint generation
      generateRAGMutation.mutate(values);
    }
  };

  const handleViewDetails = (testCase: TestCase) => {
    setSelectedTestCase(testCase);
    setIsDetailModalVisible(true);
  };

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: 'Are you sure you want to delete this test case?',
      content: 'This action cannot be undone.',
      onOk: () => deleteMutation.mutate(id),
    });
  };

  const handleRunTests = (values: any) => {
    if (selectedRowKeys.length === 0) {
      message.warning('Please select at least one test case to run');
      return;
    }
    
    runTestsMutation.mutate({
      test_case_ids: selectedRowKeys,
      base_url: values.base_url,
      service_name: values.service_name
    });
  };

  const handleDownloadReport = (filepath: string) => {
    // Create a link to download the file
    const link = document.createElement('a');
    link.href = `${process.env.REACT_APP_API_URL}/api/v1/test-execution/download-report?filepath=${encodeURIComponent(filepath)}`;
    link.download = filepath.split('/').pop() || 'report.md';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Type',
      dataIndex: 'test_type',
      key: 'test_type',
      render: (type: string) => (
        <Tag color={
          type === 'automated' ? 'blue' : 
          type === 'ai_generated' ? 'purple' : 'orange'
        }>
          {type.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: string) => (
        <Tag color={
          priority === 'critical' ? 'red' :
          priority === 'high' ? 'orange' :
          priority === 'medium' ? 'blue' : 'green'
        }>
          {priority.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Expected Status',
      dataIndex: 'expected_status_code',
      key: 'expected_status_code',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'red'}>
          {active ? 'Active' : 'Inactive'}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: TestCase) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record)}
          >
            View
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  const rowSelection = {
    selectedRowKeys,
    onChange: (selectedKeys: React.Key[]) => setSelectedRowKeys(selectedKeys as number[]),
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2}>Test Cases</Title>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setIsRAGGeneration(true);
              setIsGenerateModalVisible(true);
            }}
            style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              color: 'white'
            }}
          >
            Generate Test Cases (Smart)
          </Button>
        </Space>
      </div>

      {/* Filters */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Select
            placeholder="Filter by API Spec"
            allowClear
            style={{ width: 200 }}
            onChange={(value) => setFilters(prev => ({ ...prev, api_spec_id: value }))}
          >
            {apiSpecs?.map(spec => (
              <Option key={spec.id} value={spec.id}>{spec.name}</Option>
            ))}
          </Select>
          <Select
            placeholder="Filter by Type"
            allowClear
            style={{ width: 150 }}
            onChange={(value) => setFilters(prev => ({ ...prev, test_type: value }))}
          >
            <Option value="automated">Automated</Option>
            <Option value="manual">Manual</Option>
            <Option value="ai_generated">AI Generated</Option>
          </Select>
          <Select
            placeholder="Filter by Priority"
            allowClear
            style={{ width: 150 }}
            onChange={(value) => setFilters(prev => ({ ...prev, priority: value }))}
          >
            <Option value="low">Low</Option>
            <Option value="medium">Medium</Option>
            <Option value="high">High</Option>
            <Option value="critical">Critical</Option>
          </Select>
        </Space>
      </Card>

      <Card>
        <div style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            disabled={selectedRowKeys.length === 0}
            onClick={() => setIsRunModalVisible(true)}
          >
            Run Selected Test Cases ({selectedRowKeys.length})
          </Button>
        </div>
        <Table
          columns={columns}
          dataSource={testCases}
          loading={isLoading}
          rowKey="id"
          rowSelection={rowSelection}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
          onRow={record => ({
            onClick: () => handleViewDetails(record),
          })}
        />
      </Card>

      {/* Run Tests Modal */}
      <Modal
        title="Run Test Cases"
        open={isRunModalVisible}
        onCancel={() => setIsRunModalVisible(false)}
        footer={null}
      >
        {!runResults ? (
          <Form onFinish={handleRunTests} layout="vertical">
            <Form.Item
              name="base_url"
              label="Base URL"
              rules={[{ required: true, message: 'Please enter base URL' }]}
            >
              <Input placeholder="https://api.example.com" />
            </Form.Item>
            <Form.Item
              name="service_name"
              label="Service Name (Optional)"
            >
              <Input placeholder="Leave empty to auto-detect" />
            </Form.Item>
            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={runTestsMutation.isLoading}
                block
              >
                Run {selectedRowKeys.length} Test Cases
              </Button>
            </Form.Item>
          </Form>
        ) : (
          <div>
            <Alert
              message="Test Execution Completed"
              description={`Successfully ran ${runResults.execution_summary.total_tests} test cases`}
              type="success"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Card title="Execution Summary" size="small" style={{ marginBottom: 16 }}>
              <Descriptions column={2} size="small">
                <Descriptions.Item label="Total Tests">{runResults.execution_summary.total_tests}</Descriptions.Item>
                <Descriptions.Item label="Passed">{runResults.execution_summary.passed}</Descriptions.Item>
                <Descriptions.Item label="Failed">{runResults.execution_summary.failed}</Descriptions.Item>
                <Descriptions.Item label="Errors">{runResults.execution_summary.errors}</Descriptions.Item>
                <Descriptions.Item label="Success Rate">{runResults.execution_summary.success_rate.toFixed(1)}%</Descriptions.Item>
                <Descriptions.Item label="Avg Response Time">{runResults.execution_summary.average_response_time.toFixed(2)}ms</Descriptions.Item>
              </Descriptions>
            </Card>

            <Divider />

            <div style={{ textAlign: 'center' }}>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={() => handleDownloadReport(runResults.report_filepath)}
              >
                Download Report
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Detail Modal */}
      <Modal
        title={`Test Case Details - ${selectedTestCase?.name}`}
        open={isDetailModalVisible}
        onCancel={() => setIsDetailModalVisible(false)}
        width={800}
        footer={null}
      >
        {selectedTestCase && (
          <div>
            <Descriptions bordered column={2}>
              <Descriptions.Item label="Name">{selectedTestCase.name}</Descriptions.Item>
              <Descriptions.Item label="Type">{selectedTestCase.test_type}</Descriptions.Item>
              <Descriptions.Item label="Priority">{selectedTestCase.priority}</Descriptions.Item>
              <Descriptions.Item label="Expected Status Code">{selectedTestCase.expected_status_code}</Descriptions.Item>
              <Descriptions.Item label="Description" span={2}>{selectedTestCase.description}</Descriptions.Item>
              <Descriptions.Item label="Input Data" span={2}>
                <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(selectedTestCase.input_data, null, 2)}</pre>
              </Descriptions.Item>
              <Descriptions.Item label="Expected Output" span={2}>
                <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(selectedTestCase.expected_output, null, 2)}</pre>
              </Descriptions.Item>
              <Descriptions.Item label="Curl Command" span={2}>
                <pre style={{ whiteSpace: 'pre-wrap' }}>{selectedTestCase.curl_command}</pre>
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Modal>

      {/* Generate Modal */}
      <Modal
        title="Generate Test Cases (Smart Generation)"
        open={isGenerateModalVisible}
        onCancel={() => {
          setIsGenerateModalVisible(false);
          setIsRAGGeneration(false);
        }}
        footer={null}
      >
        <Form onFinish={handleGenerate} layout="vertical">
          <Alert
            message="Smart Test Generation"
            description="This will generate automated test cases first (guaranteed), then optionally add AI-powered test cases if available. If AI services are limited or unavailable, you'll still get comprehensive automated test coverage."
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <Form.Item
            name="api_spec_id"
            label="API Specification"
            rules={[{ required: true, message: 'Please select an API specification' }]}
          >
            <Select placeholder="Select API specification">
              {apiSpecs?.map(spec => (
                <Option key={spec.id} value={spec.id}>{spec.name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="base_url"
            label="Base URL"
            rules={[{ required: true, message: 'Please enter base URL' }]}
          >
            <Input placeholder="https://api.example.com" />
          </Form.Item>
          
          <Form.Item
            name="generation_mode"
            label="Generation Mode"
            initialValue="bulk"
          >
            <Radio.Group>
              <Radio value="bulk">Generate for All Endpoints (Recommended)</Radio>
              <Radio value="specific">Generate for Specific Endpoint</Radio>
            </Radio.Group>
          </Form.Item>
          
          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) => prevValues.generation_mode !== currentValues.generation_mode}
          >
            {({ getFieldValue }) => {
              const mode = getFieldValue('generation_mode');
              if (mode === 'specific') {
                return (
                  <>
                    <Form.Item
                      name="endpoint_path"
                      label="Endpoint Path"
                      rules={[{ required: true, message: 'Please enter endpoint path' }]}
                    >
                      <Input placeholder="/users" />
                    </Form.Item>
                    <Form.Item
                      name="method"
                      label="HTTP Method"
                      rules={[{ required: true, message: 'Please select HTTP method' }]}
                    >
                      <Select placeholder="Select HTTP method">
                        <Option value="GET">GET</Option>
                        <Option value="POST">POST</Option>
                        <Option value="PUT">PUT</Option>
                        <Option value="DELETE">DELETE</Option>
                        <Option value="PATCH">PATCH</Option>
                      </Select>
                    </Form.Item>
                  </>
                );
              }
              return null;
            }}
          </Form.Item>
          
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={generateRAGBulkMutation.isLoading || generateRAGMutation.isLoading}
              block
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                color: 'white',
                height: '40px'
              }}
            >
              Generate Smart Test Cases
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TestCases; 