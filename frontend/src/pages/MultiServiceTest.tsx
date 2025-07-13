import React, { useState } from 'react';
import { 
  Card, 
  Button, 
  Modal, 
  message, 
  Space, 
  Tag, 
  Typography,
  Select,
  Input,
  Form,
  Descriptions,
  Collapse,
  Progress,
  Alert,
  Divider,
  Row,
  Col,
  Statistic,
  Table,
  Tooltip,
  Badge
} from 'antd';
import { 
  PlayCircleOutlined, 
  EyeOutlined,
  ApiOutlined,
  LinkOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { testExecutionService, apiSpecService } from '../services/api';
import { APISpec } from '../types';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Panel } = Collapse;

const MultiServiceTest: React.FC = () => {
  const [isRunModalVisible, setIsRunModalVisible] = useState(false);
  const [runResults, setRunResults] = useState<any>(null);
  const [isDetailModalVisible, setIsDetailModalVisible] = useState(false);
  const [selectedService, setSelectedService] = useState<string>('');
  const queryClient = useQueryClient();

  const { data: apiSpecs, isLoading: apiSpecsLoading } = useQuery(
    'apiSpecs',
    () => apiSpecService.list()
  );

  const runMultiServiceMutation = useMutation(testExecutionService.runMultiService, {
    onSuccess: (data) => {
      message.success('Multi-service test execution completed successfully');
      setRunResults(data);
      setIsRunModalVisible(true);
      queryClient.invalidateQueries('testResults');
    },
    onError: (error: any) => {
      message.error(`Multi-service test execution failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleRunMultiServiceTests = (values: any) => {
    const serviceConfigs: Record<string, { base_url: string; api_spec_id?: number }> = {};
    
    // Convert form values to service configs
    Object.keys(values).forEach(key => {
      if (key.startsWith('service_') && values[key]) {
        const serviceName = key.replace('service_', '');
        const baseUrlKey = `base_url_${serviceName}`;
        const apiSpecKey = `api_spec_${serviceName}`;
        
        serviceConfigs[serviceName] = {
          base_url: values[baseUrlKey] || '',
          api_spec_id: values[apiSpecKey] ? parseInt(values[apiSpecKey]) : undefined
        };
      }
    });

    if (Object.keys(serviceConfigs).length === 0) {
      message.warning('Please configure at least one service');
      return;
    }

    runMultiServiceMutation.mutate({
      service_configs: serviceConfigs,
      test_case_ids: values.test_case_ids || []
    });
  };

  const handleViewServiceDetails = (serviceName: string) => {
    setSelectedService(serviceName);
    setIsDetailModalVisible(true);
  };

  const handleDownloadReport = (filepath: string) => {
    const link = document.createElement('a');
    link.href = `http://localhost:8000/api/v1/test-execution/download-report?filepath=${encodeURIComponent(filepath)}`;
    link.download = filepath.split('/').pop() || 'multi_service_report.md';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    message.success('Report downloaded successfully');
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

  const renderServiceCallTable = (serviceCalls: any[]) => {
    const columns = [
      {
        title: 'Source Service',
        dataIndex: 'source_service',
        key: 'source_service',
        render: (text: string) => <Tag color="blue">{text}</Tag>
      },
      {
        title: 'Target Service',
        dataIndex: 'target_service',
        key: 'target_service',
        render: (text: string) => <Tag color="green">{text}</Tag>
      },
      {
        title: 'Endpoint',
        dataIndex: 'endpoint',
        key: 'endpoint',
        render: (text: string) => <Text code>{text}</Text>
      },
      {
        title: 'Method',
        dataIndex: 'method',
        key: 'method',
        render: (text: string) => <Tag color="purple">{text}</Tag>
      },
      {
        title: 'Status',
        dataIndex: 'status',
        key: 'status',
        render: (status: string) => (
          <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
            {status.toUpperCase()}
          </Tag>
        )
      },
      {
        title: 'Response Time',
        dataIndex: 'response_time',
        key: 'response_time',
        render: (time: number) => `${time}ms`
      }
    ];

    return <Table columns={columns} dataSource={serviceCalls} rowKey={(record, index) => index?.toString() || '0'} pagination={false} size="small" />;
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <ApiOutlined /> Multi-Service Testing
        </Title>
        <Paragraph>
          Test multiple services simultaneously and analyze inter-service communication patterns.
        </Paragraph>
      </div>

      <Card>
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <ApiOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
          <Title level={3}>Multi-Service Test Execution</Title>
          <Paragraph>
            Configure multiple services and run tests to analyze inter-service communication,
            dependencies, and performance patterns.
          </Paragraph>
          <Button
            type="primary"
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={() => setIsRunModalVisible(true)}
            loading={runMultiServiceMutation.isLoading}
          >
            Run Multi-Service Tests
          </Button>
        </div>
      </Card>

      {/* Run Multi-Service Tests Modal */}
      <Modal
        title="Run Multi-Service Tests"
        open={isRunModalVisible}
        onCancel={() => setIsRunModalVisible(false)}
        footer={null}
        width={800}
      >
        {!runResults ? (
          <Form onFinish={handleRunMultiServiceTests} layout="vertical">
            <Alert
              message="Service Configuration"
              description="Configure the services you want to test. Each service needs a base URL and optionally an API spec ID."
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
            
            {/* Service 1 */}
            <Card title="Service 1" size="small" style={{ marginBottom: 16 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    name="service_1"
                    label="Service Name"
                    rules={[{ required: true, message: 'Please enter service name' }]}
                  >
                    <Input placeholder="e.g., user-api" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="base_url_1"
                    label="Base URL"
                    rules={[{ required: true, message: 'Please enter base URL' }]}
                  >
                    <Input placeholder="http://localhost:8001" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="api_spec_1"
                    label="API Spec ID (Optional)"
                  >
                    <Select placeholder="Select API spec" allowClear>
                      {apiSpecs?.map(spec => (
                        <Option key={spec.id} value={spec.id}>{spec.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </Card>

            {/* Service 2 */}
            <Card title="Service 2" size="small" style={{ marginBottom: 16 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    name="service_2"
                    label="Service Name"
                  >
                    <Input placeholder="e.g., ecommerce-api" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="base_url_2"
                    label="Base URL"
                  >
                    <Input placeholder="http://localhost:8002" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="api_spec_2"
                    label="API Spec ID (Optional)"
                  >
                    <Select placeholder="Select API spec" allowClear>
                      {apiSpecs?.map(spec => (
                        <Option key={spec.id} value={spec.id}>{spec.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </Card>

            {/* Service 3 */}
            <Card title="Service 3" size="small" style={{ marginBottom: 24 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    name="service_3"
                    label="Service Name"
                  >
                    <Input placeholder="e.g., payment-api" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="base_url_3"
                    label="Base URL"
                  >
                    <Input placeholder="http://localhost:8003" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="api_spec_3"
                    label="API Spec ID (Optional)"
                  >
                    <Select placeholder="Select API spec" allowClear>
                      {apiSpecs?.map(spec => (
                        <Option key={spec.id} value={spec.id}>{spec.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </Card>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={runMultiServiceMutation.isLoading}
                block
                size="large"
              >
                Run Multi-Service Tests
              </Button>
            </Form.Item>
          </Form>
        ) : (
          <div>
            <Alert
              message="Test Execution Completed"
              description={`Successfully executed tests across ${Object.keys(runResults.results.service_results).length} services`}
              type="success"
              showIcon
              style={{ marginBottom: 24 }}
            />

            {/* Summary Statistics */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Statistic
                  title="Total Tests"
                  value={runResults.results_count}
                  prefix={<ApiOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Services Tested"
                  value={Object.keys(runResults.results.service_results).length}
                  prefix={<LinkOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Service Calls"
                  value={runResults.results.inter_service_report.total_service_calls}
                  prefix={<LinkOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Success Rate"
                  value={(() => {
                    const allResults = runResults.results.results;
                    const passed = allResults.filter((r: any) => r.status === 'passed').length;
                    return allResults.length > 0 ? Math.round((passed / allResults.length) * 100) : 0;
                  })()}
                  suffix="%"
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
            </Row>

            {/* Service Results */}
            <Collapse defaultActiveKey={['summary']}>
              <Panel header="Service Results Summary" key="summary">
                {Object.entries(runResults.results.service_results).map(([serviceName, results]: [string, any]) => {
                  const passed = results.filter((r: any) => r.status === 'passed').length;
                  const failed = results.filter((r: any) => r.status === 'failed').length;
                  const errors = results.filter((r: any) => r.status === 'error').length;
                  const total = results.length;
                  const successRate = total > 0 ? (passed / total) * 100 : 0;

                  return (
                    <Card key={serviceName} size="small" style={{ marginBottom: 8 }}>
                      <Row gutter={16} align="middle">
                        <Col span={6}>
                          <Text strong>{serviceName}</Text>
                        </Col>
                        <Col span={4}>
                          <Badge count={total} showZero />
                        </Col>
                        <Col span={4}>
                          <Tag color="green">{passed} Passed</Tag>
                        </Col>
                        <Col span={4}>
                          <Tag color="red">{failed} Failed</Tag>
                        </Col>
                        <Col span={4}>
                          <Tag color="orange">{errors} Errors</Tag>
                        </Col>
                        <Col span={2}>
                          <Button
                            type="link"
                            icon={<EyeOutlined />}
                            onClick={() => handleViewServiceDetails(serviceName)}
                          />
                        </Col>
                      </Row>
                      <Progress percent={successRate} size="small" />
                    </Card>
                  );
                })}
              </Panel>

              {/* Inter-Service Communication */}
              {runResults.results.inter_service_report.total_service_calls > 0 && (
                <Panel header="Inter-Service Communication Analysis" key="communication">
                  <Descriptions column={2} size="small">
                    <Descriptions.Item label="Total Service Calls">
                      {runResults.results.inter_service_report.total_service_calls}
                    </Descriptions.Item>
                    <Descriptions.Item label="Synchronous Calls">
                      {runResults.results.inter_service_report.communication_patterns.synchronous_calls}
                    </Descriptions.Item>
                    <Descriptions.Item label="Asynchronous Calls">
                      {runResults.results.inter_service_report.communication_patterns.asynchronous_calls}
                    </Descriptions.Item>
                    <Descriptions.Item label="Error Propagation">
                      {runResults.results.inter_service_report.communication_patterns.error_propagation}
                    </Descriptions.Item>
                  </Descriptions>

                  <Divider />

                  <Title level={5}>Service Dependencies</Title>
                  {Object.entries(runResults.results.inter_service_report.service_dependencies).map(([service, dependencies]: [string, any]) => (
                    <div key={service} style={{ marginBottom: 8 }}>
                      <Text strong>{service}:</Text>
                      {dependencies.length > 0 ? (
                        dependencies.map((dep: string) => (
                          <Tag key={dep} color="blue" style={{ marginLeft: 8 }}>{dep}</Tag>
                        ))
                      ) : (
                        <Text type="secondary" style={{ marginLeft: 8 }}>No external dependencies</Text>
                      )}
                    </div>
                  ))}

                  <Divider />

                  <Title level={5}>Detailed Service Calls</Title>
                  {renderServiceCallTable(runResults.results.inter_service_report.service_calls)}
                </Panel>
              )}
            </Collapse>

            <div style={{ marginTop: 24, textAlign: 'center' }}>
              <Space>
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  onClick={() => handleDownloadReport(runResults.report_filepath)}
                >
                  Download Report
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={() => {
                    setRunResults(null);
                    setIsRunModalVisible(false);
                  }}
                >
                  Run Another Test
                </Button>
              </Space>
            </div>
          </div>
        )}
      </Modal>

      {/* Service Details Modal */}
      <Modal
        title={`Service Details - ${selectedService}`}
        open={isDetailModalVisible}
        onCancel={() => setIsDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {runResults && selectedService && runResults.results.service_results[selectedService] && (
          <div>
            <Descriptions column={2} size="small" style={{ marginBottom: 24 }}>
              <Descriptions.Item label="Service Name">{selectedService}</Descriptions.Item>
              <Descriptions.Item label="Total Tests">
                {runResults.results.service_results[selectedService].length}
              </Descriptions.Item>
              <Descriptions.Item label="Passed">
                {runResults.results.service_results[selectedService].filter((r: any) => r.status === 'passed').length}
              </Descriptions.Item>
              <Descriptions.Item label="Failed">
                {runResults.results.service_results[selectedService].filter((r: any) => r.status === 'failed').length}
              </Descriptions.Item>
            </Descriptions>

            <Table
              dataSource={runResults.results.service_results[selectedService]}
              columns={[
                {
                  title: 'Test Name',
                  dataIndex: ['test_case', 'name'],
                  key: 'name',
                },
                {
                  title: 'Status',
                  dataIndex: 'status',
                  key: 'status',
                  render: (status: string) => (
                    <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
                      {status.toUpperCase()}
                    </Tag>
                  )
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
                  render: (time: number) => `${time}ms`
                }
              ]}
              rowKey={(record, index) => index?.toString() || '0'}
              pagination={false}
              size="small"
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default MultiServiceTest; 