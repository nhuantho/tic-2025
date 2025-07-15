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
  Row,
  Col,
  Statistic
} from 'antd';
import { 
  PlayCircleOutlined, 
  EyeOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { testExecutionService, testCaseService } from '../services/api';
import { TestResult, TestCase } from '../types';

const { Title } = Typography;
const { Option } = Select;
const { Panel } = Collapse;

const TestExecution: React.FC = () => {
  const [isExecuteModalVisible, setIsExecuteModalVisible] = useState(false);
  const [selectedResult, setSelectedResult] = useState<TestResult | null>(null);
  const [isDetailModalVisible, setIsDetailModalVisible] = useState(false);
  const [filters, setFilters] = useState({
    test_case_id: undefined,
    status: undefined,
  });
  const queryClient = useQueryClient();

  const { data: testResults, isLoading } = useQuery(
    ['testResults', filters],
    () => testExecutionService.getResults(filters)
  );

  const { data: testCases } = useQuery('testCases', () => testCaseService.list());

  const executeMutation = useMutation(testExecutionService.execute, {
    onSuccess: (data) => {
      message.success(`Executed ${data.results_count} test cases successfully`);
      setIsExecuteModalVisible(false);
      queryClient.invalidateQueries('testResults');
    },
    onError: (error: any) => {
      message.error(`Execution failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleExecute = (values: any) => {
    executeMutation.mutate(values);
  };

  const handleViewDetails = (result: TestResult) => {
    setSelectedResult(result);
    setIsDetailModalVisible(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed': return '#52c41a';
      case 'failed': return '#ff4d4f';
      case 'error': return '#faad14';
      default: return '#d9d9d9';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed': return <CheckCircleOutlined />;
      case 'failed': return <CloseCircleOutlined />;
      case 'error': return <ExclamationCircleOutlined />;
      default: return null;
    }
  };

  const columns = [
    {
      title: 'Test Case ID',
      dataIndex: 'test_case_id',
      key: 'test_case_id',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Response Code',
      dataIndex: 'response_status_code',
      key: 'response_status_code',
    },
    {
      title: 'Response Time',
      dataIndex: 'response_time',
      key: 'response_time',
      render: (time: number) => `${time}ms`,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: TestResult) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetails(record)}
        >
          View
        </Button>
      ),
    },
  ];

  const totalResults = testResults?.length || 0;
  const passedResults = testResults?.filter(r => r.status === 'passed').length || 0;
  const failedResults = testResults?.filter(r => r.status === 'failed').length || 0;
  const errorResults = testResults?.filter(r => r.status === 'error').length || 0;
  const successRate = totalResults > 0 ? (passedResults / totalResults) * 100 : 0;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2}>Test Execution</Title>
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={() => setIsExecuteModalVisible(true)}
        >
          Execute Tests
        </Button>
      </div>

      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Results"
              value={totalResults}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Passed"
              value={passedResults}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Failed"
              value={failedResults}
              valueStyle={{ color: '#ff4d4f' }}
              prefix={<CloseCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Success Rate"
              value={successRate}
              suffix="%"
              valueStyle={{ color: successRate >= 80 ? '#52c41a' : '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filters */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Select
            placeholder="Filter by Test Case"
            allowClear
            style={{ width: 200 }}
            onChange={(value) => setFilters(prev => ({ ...prev, test_case_id: value }))}
          >
            {testCases?.map(testCase => (
              <Option key={testCase.id} value={testCase.id}>
                {testCase.name}
              </Option>
            ))}
          </Select>
          <Select
            placeholder="Filter by Status"
            allowClear
            style={{ width: 150 }}
            onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
          >
            <Option value="passed">Passed</Option>
            <Option value="failed">Failed</Option>
            <Option value="error">Error</Option>
          </Select>
        </Space>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={testResults}
          loading={isLoading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />
      </Card>

      {/* Execute Modal */}
      <Modal
        title="Execute Test Cases"
        open={isExecuteModalVisible}
        onCancel={() => setIsExecuteModalVisible(false)}
        footer={null}
      >
        <Form onFinish={handleExecute} layout="vertical">
          <Form.Item
            name="test_case_ids"
            label="Test Cases"
            rules={[{ required: true, message: 'Please select test cases' }]}
          >
            <Select
              mode="multiple"
              placeholder="Select test cases to execute"
              style={{ width: '100%' }}
            >
              {testCases?.map(testCase => (
                <Option key={testCase.id} value={testCase.id}>
                  {testCase.name}
                </Option>
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
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={executeMutation.isLoading}>
              Execute
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Detail Modal */}
      <Modal
        title="Test Result Details"
        open={isDetailModalVisible}
        onCancel={() => setIsDetailModalVisible(false)}
        width={800}
        footer={null}
      >
        {selectedResult && (
          <div>
            <Descriptions bordered column={2}>
              <Descriptions.Item label="Test Case ID">
                {selectedResult.test_case_id}
              </Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={getStatusColor(selectedResult.status)} icon={getStatusIcon(selectedResult.status)}>
                  {selectedResult.status.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Response Code">
                {selectedResult.response_status_code}
              </Descriptions.Item>
              <Descriptions.Item label="Response Time">
                {selectedResult.response_time}ms
              </Descriptions.Item>
              <Descriptions.Item label="Created" span={2}>
                {new Date(selectedResult.created_at).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>

            <Collapse style={{ marginTop: 16 }}>
              {selectedResult.response_body && (
                <Panel header="Response Body" key="response">
                  <pre className="json-viewer">
                    {selectedResult.response_body}
                  </pre>
                </Panel>
              )}
              {selectedResult.error_message && (
                <Panel header="Error Message" key="error">
                  <pre className="json-viewer">
                    {selectedResult.error_message}
                  </pre>
                </Panel>
              )}
              {selectedResult.execution_log && (
                <Panel header="Execution Log" key="log">
                  <pre className="json-viewer">
                    {selectedResult.execution_log}
                  </pre>
                </Panel>
              )}
            </Collapse>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TestExecution; 