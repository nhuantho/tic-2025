import React, { useState } from 'react';
import { 
  Table, 
  Button, 
  Upload, 
  Modal, 
  message, 
  Space, 
  Tag, 
  Typography,
  Card,
  Descriptions
} from 'antd';
import { UploadOutlined, EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiSpecService } from '../services/api';
import { APISpec, Endpoint } from '../types';

const { Title } = Typography;

const APISpecs: React.FC = () => {
  const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);
  const [selectedSpec, setSelectedSpec] = useState<APISpec | null>(null);
  const [isDetailModalVisible, setIsDetailModalVisible] = useState(false);
  const queryClient = useQueryClient();

  const { data: apiSpecs, isLoading } = useQuery('apiSpecs', () => apiSpecService.list());

  const importMutation = useMutation(apiSpecService.import, {
    onSuccess: () => {
      message.success('API specification imported successfully');
      setIsUploadModalVisible(false);
      queryClient.invalidateQueries('apiSpecs');
    },
    onError: (error: any) => {
      message.error(`Import failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const deleteMutation = useMutation(apiSpecService.delete, {
    onSuccess: () => {
      message.success('API specification deleted successfully');
      queryClient.invalidateQueries('apiSpecs');
    },
    onError: (error: any) => {
      message.error(`Delete failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleUpload = (file: File) => {
    importMutation.mutate(file);
    return false; // Prevent default upload behavior
  };

  const handleViewDetails = async (spec: APISpec) => {
    setSelectedSpec(spec);
    setIsDetailModalVisible(true);
  };

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: 'Are you sure you want to delete this API specification?',
      content: 'This action cannot be undone.',
      onOk: () => deleteMutation.mutate(id),
    });
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version',
    },
    {
      title: 'Type',
      dataIndex: 'file_type',
      key: 'file_type',
      render: (type: string) => (
        <Tag color={type === 'openapi' ? 'blue' : 'green'}>
          {type?.toUpperCase() || 'UNKNOWN'}
        </Tag>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : status === 'error' ? 'red' : 'orange'}>
          {status?.toUpperCase() || 'UNKNOWN'}
        </Tag>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: APISpec) => (
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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2}>API Specifications</Title>
        <Button
          type="primary"
          icon={<UploadOutlined />}
          onClick={() => setIsUploadModalVisible(true)}
        >
          Import API Spec
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={apiSpecs}
          loading={isLoading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />
      </Card>

      {/* Upload Modal */}
      <Modal
        title="Import API Specification"
        open={isUploadModalVisible}
        onCancel={() => setIsUploadModalVisible(false)}
        footer={null}
      >
        <Upload.Dragger
          name="file"
          beforeUpload={handleUpload}
          accept=".yaml,.yml,.json"
          disabled={importMutation.isLoading}
        >
          <p className="ant-upload-drag-icon">
            <UploadOutlined />
          </p>
          <p className="ant-upload-text">Click or drag file to this area to upload</p>
          <p className="ant-upload-hint">
            Support for OpenAPI (.yaml, .yml, .json) and Postman (.json) files
          </p>
        </Upload.Dragger>
      </Modal>

      {/* Detail Modal */}
      <Modal
        title={`API Specification Details - ${selectedSpec?.name}`}
        open={isDetailModalVisible}
        onCancel={() => setIsDetailModalVisible(false)}
        width={800}
        footer={null}
      >
        {selectedSpec && (
          <div>
            <Descriptions bordered column={2}>
              <Descriptions.Item label="Name">{selectedSpec.name}</Descriptions.Item>
              <Descriptions.Item label="Version">{selectedSpec.version}</Descriptions.Item>
              <Descriptions.Item label="Type">{selectedSpec.file_type}</Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={selectedSpec.status === 'active' ? 'green' : selectedSpec.status === 'error' ? 'red' : 'orange'}>
                  {selectedSpec.status?.toUpperCase() || 'UNKNOWN'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Description" span={2}>
                {selectedSpec.description}
              </Descriptions.Item>
              <Descriptions.Item label="File Path" span={2}>
                {selectedSpec.file_path}
              </Descriptions.Item>
              <Descriptions.Item label="Created" span={2}>
                {new Date(selectedSpec.created_at).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default APISpecs; 