import React, { useState } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  Typography, 
  Progress, 
  Tag, 
  Space, 
  Button, 
  List, 
  Avatar, 
  Divider,
  Alert,
  Timeline,
  Badge,
  Tooltip,
  Modal,
  message
} from 'antd';
import { useQuery } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { 
  ApiOutlined, 
  BugOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  FileTextOutlined,
  PlayCircleOutlined,
  TrophyOutlined,
  RiseOutlined,
  UserOutlined,
  SettingOutlined,
  RocketOutlined,
  BarChartOutlined,
  PlusOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { apiSpecService, testCaseService, testExecutionService } from '../services/api';

const { Title, Text, Paragraph } = Typography;

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [isRunAllModalVisible, setIsRunAllModalVisible] = useState(false);
  const [isImportModalVisible, setIsImportModalVisible] = useState(false);

  const { data: apiSpecs, isLoading: apiSpecsLoading, refetch: refetchApiSpecs } = useQuery(
    'apiSpecs',
    () => apiSpecService.list()
  );

  const { data: testCases, isLoading: testCasesLoading, refetch: refetchTestCases } = useQuery(
    'testCases',
    () => testCaseService.list()
  );

  const { data: testResults, isLoading: resultsLoading, refetch: refetchResults } = useQuery(
    'testResults',
    () => testExecutionService.getResults()
  );

  // Calculate statistics
  const totalApiSpecs = apiSpecs?.length || 0;
  const totalTestCases = testCases?.length || 0;
  const totalResults = testResults?.length || 0;
  const passedTests = testResults?.filter(r => r.status === 'passed').length || 0;
  const failedTests = testResults?.filter(r => r.status === 'failed').length || 0;
  const errorTests = testResults?.filter(r => r.status === 'error').length || 0;
  const successRate = totalResults > 0 ? (passedTests / totalResults) * 100 : 0;

  // Get recent activity
  const recentApiSpecs = apiSpecs?.slice(0, 3) || [];
  const recentResults = testResults?.slice(0, 5) || [];

  // Calculate test case distribution by priority
  const priorityStats = testCases?.reduce((acc, testCase) => {
    const priority = testCase.priority?.toLowerCase() || 'medium';
    acc[priority] = (acc[priority] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

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
      default: return <ClockCircleOutlined />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'blue';
      case 'low': return 'green';
      default: return 'default';
    }
  };

  // Action handlers
  const handleRunTests = () => {
    if (totalTestCases === 0) {
      message.warning('No test cases available. Please generate test cases first.');
      return;
    }
    setIsRunAllModalVisible(true);
  };

  const handleImportApiSpec = () => {
    navigate('/api-specs');
    message.info('Navigate to API Specifications page to import new APIs');
  };

  const handleGenerateTests = () => {
    if (totalApiSpecs === 0) {
      message.warning('No API specifications available. Please import an API spec first.');
      return;
    }
    navigate('/test-cases');
    message.info('Navigate to Test Cases page to generate tests');
  };

  const handleViewReports = () => {
    navigate('/test-reports');
  };

  const handleViewDetails = () => {
    navigate('/test-execution');
  };

  const handleViewAllApiSpecs = () => {
    navigate('/api-specs');
  };

  const handleViewAllResults = () => {
    navigate('/test-execution');
  };

  const handleRefreshData = () => {
    refetchApiSpecs();
    refetchTestCases();
    refetchResults();
    message.success('Dashboard data refreshed!');
  };

  const handleRunAllTests = () => {
    if (totalTestCases === 0) {
      message.warning('No test cases available to run.');
      setIsRunAllModalVisible(false);
      return;
    }
    
    message.info('This would run all available test cases. Navigate to Test Cases page for detailed execution.');
    setIsRunAllModalVisible(false);
    navigate('/test-cases');
  };

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh', position: 'relative' }}>
      {/* Floating Mountain Button */}
      <a
        href="http://43.199.148.44:8080/dashboard"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          position: 'fixed',
          top: 24,
          right: 24,
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          background: 'rgba(255,255,255,0.95)',
          borderRadius: 24,
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          padding: '8px 16px',
          cursor: 'pointer',
          textDecoration: 'none',
          transition: 'box-shadow 0.2s',
        }}
      >
        <img src="/mountain.svg" alt="Mountain" style={{ width: 32, height: 32, marginRight: 10 }} />
        <span style={{ fontWeight: 600, color: '#2D3A4A', fontSize: 16 }}>
          Try Super API Test Gen
        </span>
      </a>
      {/* Header Section */}
      <div style={{ marginBottom: 32 }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Title level={1} style={{ margin: 0, color: '#1890ff' }}>
              🚀 APITestGen Dashboard
            </Title>
            <Text type="secondary" style={{ fontSize: '16px' }}>
              Automated API Testing Platform
            </Text>
          </Col>
          <Col>
            <Space>
              <Button 
                type="primary" 
                icon={<PlayCircleOutlined />} 
                size="large"
                onClick={handleRunTests}
              >
                Run Tests
              </Button>
              <Button 
                icon={<ReloadOutlined />} 
                size="large"
                onClick={handleRefreshData}
                loading={apiSpecsLoading || testCasesLoading || resultsLoading}
              >
                Refresh
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* Welcome Alert */}
      <Alert
        message="Welcome to APITestGen!"
        description="Monitor your API testing progress, view recent activities, and manage your test suites from this comprehensive dashboard."
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
        icon={<RocketOutlined />}
      />

      {/* Main Statistics Cards */}
      <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card 
            hoverable 
            style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white'
            }}
            onClick={() => navigate('/api-specs')}
          >
            <Statistic
              title={<span style={{ color: 'white' }}>API Specifications</span>}
              value={totalApiSpecs}
              prefix={<ApiOutlined style={{ color: 'white' }} />}
              loading={apiSpecsLoading}
              valueStyle={{ color: 'white', fontSize: '32px' }}
            />
            <Text style={{ color: 'rgba(255,255,255,0.8)' }}>
              {apiSpecsLoading ? 'Loading...' : 'Total imported APIs'}
            </Text>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card 
            hoverable 
            style={{ 
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white'
            }}
            onClick={() => navigate('/test-cases')}
          >
            <Statistic
              title={<span style={{ color: 'white' }}>Test Cases</span>}
              value={totalTestCases}
              prefix={<BugOutlined style={{ color: 'white' }} />}
              loading={testCasesLoading}
              valueStyle={{ color: 'white', fontSize: '32px' }}
            />
            <Text style={{ color: 'rgba(255,255,255,0.8)' }}>
              {testCasesLoading ? 'Loading...' : 'Generated test cases'}
            </Text>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card 
            hoverable 
            style={{ 
              background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
              color: 'white'
            }}
          >
            <Statistic
              title={<span style={{ color: 'white' }}>Success Rate</span>}
              value={successRate}
              suffix="%"
              prefix={<RiseOutlined style={{ color: 'white' }} />}
              loading={resultsLoading}
              valueStyle={{ color: 'white', fontSize: '32px' }}
            />
            <Text style={{ color: 'rgba(255,255,255,0.8)' }}>
              {resultsLoading ? 'Loading...' : 'Test execution success'}
            </Text>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card 
            hoverable 
            style={{ 
              background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
              color: 'white'
            }}
            onClick={() => navigate('/test-execution')}
          >
            <Statistic
              title={<span style={{ color: 'white' }}>Total Executions</span>}
              value={totalResults}
              prefix={<BarChartOutlined style={{ color: 'white' }} />}
              loading={resultsLoading}
              valueStyle={{ color: 'white', fontSize: '32px' }}
            />
            <Text style={{ color: 'rgba(255,255,255,0.8)' }}>
              {resultsLoading ? 'Loading...' : 'Tests executed'}
            </Text>
          </Card>
        </Col>
      </Row>

      {/* Test Results Overview */}
      <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
        <Col xs={24} lg={16}>
          <Card 
            title={
              <Space>
                <TrophyOutlined style={{ color: '#1890ff' }} />
                <span>Test Execution Overview</span>
              </Space>
            }
            extra={
              <Button type="link" icon={<BarChartOutlined />} onClick={handleViewDetails}>
                View Details
              </Button>
            }
          >
            <Row gutter={16}>
              <Col span={8}>
                <div style={{ textAlign: 'center' }}>
                  <Progress
                    type="circle"
                    percent={successRate}
                    format={percent => `${percent}%`}
                    strokeColor="#52c41a"
                    size={120}
                  />
                  <div style={{ marginTop: 16 }}>
                    <Text strong>Success Rate</Text>
                  </div>
                </div>
              </Col>
              <Col span={16}>
                <Row gutter={[16, 16]}>
                  <Col span={8}>
                    <Card size="small" style={{ textAlign: 'center', background: '#f6ffed' }}>
                      <Statistic
                        title="Passed"
                        value={passedTests}
                        prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                        valueStyle={{ color: '#52c41a' }}
                      />
                    </Card>
                  </Col>
                  <Col span={8}>
                    <Card size="small" style={{ textAlign: 'center', background: '#fff2f0' }}>
                      <Statistic
                        title="Failed"
                        value={failedTests}
                        prefix={<CloseCircleOutlined style={{ color: '#ff4d4f' }} />}
                        valueStyle={{ color: '#ff4d4f' }}
                      />
                    </Card>
                  </Col>
                  <Col span={8}>
                    <Card size="small" style={{ textAlign: 'center', background: '#fffbe6' }}>
                      <Statistic
                        title="Errors"
                        value={errorTests}
                        prefix={<ExclamationCircleOutlined style={{ color: '#faad14' }} />}
                        valueStyle={{ color: '#faad14' }}
                      />
                    </Card>
                  </Col>
                </Row>
              </Col>
            </Row>
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card 
            title={
              <Space>
                <BugOutlined style={{ color: '#722ed1' }} />
                <span>Test Case Priority</span>
              </Space>
            }
          >
            <div style={{ marginBottom: 16 }}>
              {Object.entries(priorityStats).map(([priority, count]) => (
                <div key={priority} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Space>
                      <Tag color={getPriorityColor(priority)}>
                        {priority.toUpperCase()}
                      </Tag>
                      <Text>{count} cases</Text>
                    </Space>
                    <Text type="secondary">
                      {((count / totalTestCases) * 100).toFixed(1)}%
                    </Text>
                  </div>
                  <Progress 
                    percent={((count / totalTestCases) * 100)} 
                    strokeColor={getPriorityColor(priority)}
                    showInfo={false}
                    size="small"
                  />
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>

      {/* Recent Activity and Quick Actions */}
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card 
            title={
              <Space>
                <FileTextOutlined style={{ color: '#13c2c2' }} />
                <span>Recent API Specifications</span>
              </Space>
            }
            extra={
              <Button type="link" size="small" onClick={handleViewAllApiSpecs}>
                View All
              </Button>
            }
          >
            <List
              loading={apiSpecsLoading}
              dataSource={recentApiSpecs}
              renderItem={(spec) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar icon={<ApiOutlined />} style={{ backgroundColor: '#1890ff' }} />}
                    title={<Text strong>{spec.name}</Text>}
                    description={
                      <Space>
                        <Tag color="blue">{spec.file_type}</Tag>
                        <Text type="secondary">
                          {spec.status === 'success' ? '✅ Imported' : '❌ Failed'}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card 
            title={
              <Space>
                <ClockCircleOutlined style={{ color: '#fa8c16' }} />
                <span>Recent Test Results</span>
              </Space>
            }
            extra={
              <Button type="link" size="small" onClick={handleViewAllResults}>
                View All
              </Button>
            }
          >
            <Timeline>
              {recentResults.map((result) => (
                <Timeline.Item 
                  key={result.id}
                  color={getStatusColor(result.status)}
                  dot={getStatusIcon(result.status)}
                >
                  <div>
                    <Text strong>Test Case #{result.test_case_id}</Text>
                    <br />
                    <Space>
                      <Tag color={getStatusColor(result.status)}>
                        {result.status.toUpperCase()}
                      </Tag>
                      <Text type="secondary">
                        {new Date(result.created_at).toLocaleString()}
                      </Text>
                    </Space>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Row gutter={[24, 24]} style={{ marginTop: 32 }}>
        <Col span={24}>
          <Card title="Quick Actions">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={6}>
                <Button 
                  type="primary" 
                  icon={<PlayCircleOutlined />} 
                  size="large" 
                  block
                  style={{ height: '60px' }}
                  onClick={handleRunTests}
                >
                  Run All Tests
                </Button>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Button 
                  icon={<FileTextOutlined />} 
                  size="large" 
                  block
                  style={{ height: '60px' }}
                  onClick={handleImportApiSpec}
                >
                  Import API Spec
                </Button>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Button 
                  icon={<BugOutlined />} 
                  size="large" 
                  block
                  style={{ height: '60px' }}
                  onClick={handleGenerateTests}
                >
                  Generate Tests
                </Button>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Button 
                  icon={<BarChartOutlined />} 
                  size="large" 
                  block
                  style={{ height: '60px' }}
                  onClick={handleViewReports}
                >
                  View Reports
                </Button>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Run All Tests Modal */}
      <Modal
        title="Run All Test Cases"
        open={isRunAllModalVisible}
        onCancel={() => setIsRunAllModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setIsRunAllModalVisible(false)}>
            Cancel
          </Button>,
          <Button 
            key="run" 
            type="primary" 
            onClick={handleRunAllTests}
            disabled={totalTestCases === 0}
          >
            Run All Tests
          </Button>
        ]}
      >
        <div>
          <p>This will run all available test cases ({totalTestCases} total).</p>
          {totalTestCases === 0 && (
            <Alert
              message="No test cases available"
              description="Please generate test cases first before running tests."
              type="warning"
              showIcon
            />
          )}
        </div>
      </Modal>
    </div>
  );
};

export default Dashboard; 