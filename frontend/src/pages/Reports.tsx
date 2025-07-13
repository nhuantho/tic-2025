import React, { useState } from 'react';
import { 
  Card, 
  Typography, 
  Select, 
  Space, 
  List, 
  Tag, 
  Button,
  Modal,
  Descriptions
} from 'antd';
import { 
  FileTextOutlined, 
  EyeOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { testExecutionService, apiSpecService } from '../services/api';
import { APISpec } from '../types';
import ReactMarkdown from 'react-markdown';

const { Title } = Typography;
const { Option } = Select;

const Reports: React.FC = () => {
  const [selectedApiSpec, setSelectedApiSpec] = useState<string>('');
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [isReportModalVisible, setIsReportModalVisible] = useState(false);

  const { data: apiSpecs } = useQuery('apiSpecs', () => apiSpecService.list());

  const { data: reports, isLoading } = useQuery(
    ['reports', selectedApiSpec],
    () => selectedApiSpec ? testExecutionService.getReports(selectedApiSpec) : null,
    { enabled: !!selectedApiSpec }
  );

  const handleViewReport = (report: any) => {
    setSelectedReport(report);
    setIsReportModalVisible(true);
  };

  const handleDownloadReport = (report: any) => {
    const blob = new Blob([report.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = report.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <Title level={2}>Test Reports</Title>

      <Card style={{ marginBottom: 16 }}>
        <Space>
          <span>Select API Specification:</span>
          <Select
            placeholder="Choose API specification"
            style={{ width: 300 }}
            onChange={setSelectedApiSpec}
            value={selectedApiSpec}
          >
            {apiSpecs?.map(spec => (
              <Option key={spec.name} value={spec.name}>
                {spec.name}
              </Option>
            ))}
          </Select>
        </Space>
      </Card>

      {selectedApiSpec && (
        <Card title={`Reports for ${selectedApiSpec}`}>
          {isLoading ? (
            <div>Loading reports...</div>
          ) : reports?.reports && reports.reports.length > 0 ? (
            <List
              dataSource={reports.reports}
              renderItem={(report) => (
                <List.Item
                  actions={[
                    <Button
                      type="link"
                      icon={<EyeOutlined />}
                      onClick={() => handleViewReport(report)}
                    >
                      View
                    </Button>,
                    <Button
                      type="link"
                      icon={<DownloadOutlined />}
                      onClick={() => handleDownloadReport(report)}
                    >
                      Download
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<FileTextOutlined style={{ fontSize: 24 }} />}
                    title={report.filename}
                    description={`Generated: ${new Date(report.created_at).toLocaleString()}`}
                  />
                </List.Item>
              )}
            />
          ) : (
            <div>No reports found for this API specification.</div>
          )}
        </Card>
      )}

      {/* Report Detail Modal */}
      <Modal
        title={`Report: ${selectedReport?.filename}`}
        open={isReportModalVisible}
        onCancel={() => setIsReportModalVisible(false)}
        width={1000}
        footer={[
          <Button key="download" icon={<DownloadOutlined />} onClick={() => handleDownloadReport(selectedReport)}>
            Download
          </Button>,
          <Button key="close" onClick={() => setIsReportModalVisible(false)}>
            Close
          </Button>
        ]}
      >
        {selectedReport && (
          <div>
            <Descriptions bordered column={2} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Filename">{selectedReport.filename}</Descriptions.Item>
              <Descriptions.Item label="Generated">
                {new Date(selectedReport.created_at).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>
            
            <div style={{ 
              maxHeight: '600px', 
              overflowY: 'auto', 
              border: '1px solid #d9d9d9', 
              borderRadius: '6px',
              padding: '16px',
              backgroundColor: '#fafafa'
            }}>
              <ReactMarkdown>{selectedReport.content}</ReactMarkdown>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Reports; 