import React, { useState } from 'react';
import { 
  Table, 
  Button, 
  message, 
  Space, 
  Tag, 
  Typography,
  Card,
  Select,
  Modal,
  Descriptions,
  Divider,
  Row,
  Col,
  Statistic,
  Tooltip,
  Alert,
  Empty,
  Progress
} from 'antd';
import { 
  DownloadOutlined, 
  EyeOutlined,
  FileTextOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { testExecutionService } from '../services/api';
import ReactMarkdown from 'react-markdown';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

const TestReports: React.FC = () => {
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [isDetailModalVisible, setIsDetailModalVisible] = useState(false);
  const [selectedService, setSelectedService] = useState<string | undefined>(undefined);
  const [markdownContent, setMarkdownContent] = useState<string | null>(null);
  const [loadingContent, setLoadingContent] = useState(false);

  const { data: reportsData, isLoading, refetch } = useQuery(
    ['testReports', selectedService],
    () => testExecutionService.getReports(selectedService)
  );

  const reports = reportsData?.reports || [];

  const handleViewReport = async (report: any) => {
    setSelectedReport(report);
    setIsDetailModalVisible(true);
    setMarkdownContent(null);
    setLoadingContent(true);
    // Nếu report đã có content thì dùng luôn
    if (report.content) {
      setMarkdownContent(report.content);
      setLoadingContent(false);
      return;
    }
    // Nếu có api_spec_name thì lấy nội dung file
    if (report.service_name) {
      try {
        const apiSpecName = report.service_name;
        const res = await testExecutionService.getReportsByApiSpec(apiSpecName);
        // Tìm đúng file theo filename
        const found = res.reports.find((r: any) => r.filename === report.filename);
        setMarkdownContent(found ? found.content : 'No content found.');
      } catch (e) {
        setMarkdownContent('Error loading report content.');
      }
    } else {
      setMarkdownContent('No content available.');
    }
    setLoadingContent(false);
  };

  const handleDownloadReport = (filepath: string, filename: string) => {
    // Create a link to download the file
    const link = document.createElement('a');
    link.href = `http://localhost:8000/api/v1/test-execution/download-report?filepath=${encodeURIComponent(filepath)}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    message.success('Report downloaded successfully');
  };

  // Calculate statistics
  const totalReports = reports.length;
  const recentReports = reports.filter((r: any) => {
    const reportDate = new Date(r.created_at);
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    return reportDate > oneDayAgo;
  }).length;

  const columns = [
    {
      title: 'Service Name',
      dataIndex: 'service_name',
      key: 'service_name',
      render: (name: string) => (
        <Tag color="blue" style={{ fontWeight: 'bold' }}>
          {name}
        </Tag>
      ),
    },
    {
      title: 'Report File',
      dataIndex: 'filename',
      key: 'filename',
      render: (filename: string) => (
        <Space>
          <FileTextOutlined style={{ color: '#1890ff' }} />
          <Text code>{filename}</Text>
        </Space>
      ),
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => (
        <Space direction="vertical" size={0}>
          <Text strong>{new Date(date).toLocaleDateString()}</Text>
          <Text type="secondary">{new Date(date).toLocaleTimeString()}</Text>
        </Space>
      ),
      sorter: (a: any, b: any) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
      defaultSortOrder: 'descend' as const,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Tooltip title="View report details">
            <Button
              type="primary"
              icon={<EyeOutlined />}
              size="small"
              onClick={() => handleViewReport(record)}
            >
              View
            </Button>
          </Tooltip>
          <Tooltip title="Download report file">
            <Button
              icon={<DownloadOutlined />}
              size="small"
              onClick={() => handleDownloadReport(record.filepath, record.filename)}
            >
              Download
            </Button>
          </Tooltip>
        </Space>
      ),
    },
  ];

  // Get unique service names for filter
  const serviceNames = Array.from(new Set(reports.map((r: any) => r.service_name)));

  return (
    <div style={{ padding: '24px' }}>
      {/* Header Section */}
      <div style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Title level={2} style={{ margin: 0 }}>
              📊 Test Reports Dashboard
            </Title>
            <Text type="secondary">
              View and manage your API test execution reports
            </Text>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={() => refetch()}
              loading={isLoading}
            >
              Refresh Reports
            </Button>
          </Col>
        </Row>
      </div>

      {/* Statistics Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Reports"
              value={totalReports}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Reports Today"
              value={recentReports}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Services Tested"
              value={serviceNames.length}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Latest Report"
              value={reports.length > 0 ? new Date(reports[0]?.created_at).toLocaleDateString() : 'N/A'}
              prefix={<InfoCircleOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Help Information */}
      <Alert
        message="How to use Test Reports"
        description={
          <div>
            <Paragraph style={{ marginBottom: 8 }}>
              <strong>📋 What are Test Reports?</strong> Test reports contain detailed information about your API test executions, including:
            </Paragraph>
            <ul style={{ marginBottom: 8 }}>
              <li>✅ Passed tests and their performance metrics</li>
              <li>❌ Failed tests with detailed error information</li>
              <li>⚠️ Error tests with troubleshooting details</li>
              <li>📊 Performance analysis and response time breakdown</li>
              <li>🎯 Recommendations for improving your API</li>
            </ul>
            <Paragraph style={{ marginBottom: 0 }}>
              <strong>💡 Tip:</strong> Use the "View" button to see detailed test results, and "Download" to save reports for offline analysis.
            </Paragraph>
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      {/* Filters */}
      <Card 
        title={
          <Space>
            <InfoCircleOutlined />
            Filters & Search
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        <Row gutter={16} align="middle">
          <Col>
            <Text strong>Filter by Service:</Text>
          </Col>
          <Col>
            <Select
              placeholder="All Services"
              allowClear
              style={{ width: 250 }}
              value={selectedService}
              onChange={setSelectedService}
            >
              {serviceNames.map(name => (
                <Option key={name} value={name}>{name}</Option>
              ))}
            </Select>
          </Col>
          <Col>
            <Text type="secondary">
              {selectedService ? `Showing reports for: ${selectedService}` : 'Showing all reports'}
            </Text>
          </Col>
        </Row>
      </Card>

      {/* Reports Table */}
      <Card 
        title={
          <Space>
            <FileTextOutlined />
            Test Reports ({reports.length})
          </Space>
        }
      >
        {reports.length === 0 ? (
          <Empty
            description={
              <div>
                <Text>No test reports found</Text>
                <br />
                <Text type="secondary">
                  Run some tests first to generate reports
                </Text>
              </div>
            }
            style={{ padding: '40px 0' }}
          />
        ) : (
          <Table
            columns={columns}
            dataSource={reports}
            loading={isLoading}
            rowKey="filepath"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => 
                `${range[0]}-${range[1]} of ${total} reports`,
            }}
          />
        )}
      </Card>

      {/* Report Detail Modal */}
      <Modal
        title={
          <Space>
            <FileTextOutlined />
            Report Details - {selectedReport?.filename}
          </Space>
        }
        open={isDetailModalVisible}
        onCancel={() => setIsDetailModalVisible(false)}
        width={900}
        footer={[
          <Button
            key="download"
            type="primary"
            icon={<DownloadOutlined />}
            onClick={() => selectedReport && handleDownloadReport(selectedReport.filepath, selectedReport.filename)}
          >
            Download Report
          </Button>,
          <Button key="close" onClick={() => setIsDetailModalVisible(false)}>
            Close
          </Button>
        ]}
      >
        {selectedReport && (
          <div>
            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label="Service Name">
                <Tag color="blue">{selectedReport.service_name}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Filename">
                <Text code>{selectedReport.filename}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="Created At" span={2}>
                <Space>
                  <ClockCircleOutlined />
                  {new Date(selectedReport.created_at).toLocaleString()}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="File Path" span={2}>
                <Text code style={{ fontSize: '12px' }}>
                  {selectedReport.filepath}
                </Text>
              </Descriptions.Item>
            </Descriptions>
            
            <Divider />
            
            <Alert
              message="Report Contents"
              description={
                <div>
                  <Paragraph style={{ marginBottom: 8 }}>
                    This detailed report contains comprehensive information about your API test execution:
                  </Paragraph>
                  <Row gutter={16}>
                    <Col span={12}>
                      <ul>
                        <li><CheckCircleOutlined style={{ color: '#52c41a' }} /> Test execution summary</li>
                        <li><InfoCircleOutlined style={{ color: '#1890ff' }} /> Performance metrics</li>
                        <li><ClockCircleOutlined style={{ color: '#fa8c16' }} /> Response time analysis</li>
                      </ul>
                    </Col>
                    <Col span={12}>
                      <ul>
                        <li><CloseCircleOutlined style={{ color: '#ff4d4f' }} /> Failed test details</li>
                        <li><ExclamationCircleOutlined style={{ color: '#faad14' }} /> Error messages</li>
                        <li><FileTextOutlined style={{ color: '#722ed1' }} /> Curl commands used</li>
                      </ul>
                    </Col>
                  </Row>
                  <Paragraph style={{ marginBottom: 0 }}>
                    <strong>💡 Tip:</strong> Download the report to view the full markdown content with detailed test results and recommendations.
                  </Paragraph>
                </div>
              }
              type="info"
              showIcon
            />
            <Divider />
            <div style={{ maxHeight: 400, overflowY: 'auto', background: '#fafbfc', borderRadius: 8, padding: 16, marginBottom: 16 }}>
              {loadingContent ? (
                <div>Loading report content...</div>
              ) : (
                markdownContent ? (
                  <ReactMarkdown>{markdownContent}</ReactMarkdown>
                ) : (
                  <div>No content available.</div>
                )
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TestReports; 