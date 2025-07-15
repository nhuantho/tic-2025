import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  DashboardOutlined, 
  ApiOutlined, 
  BugOutlined, 
  PlayCircleOutlined, 
  FileTextOutlined,
  HistoryOutlined,
  LinkOutlined
} from '@ant-design/icons';

const { Header: AntHeader } = Layout;

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/api-specs',
      icon: <ApiOutlined />,
      label: 'API Specifications',
    },
    {
      key: '/test-cases',
      icon: <BugOutlined />,
      label: 'Test Cases',
    },
    {
      key: '/test-execution',
      icon: <PlayCircleOutlined />,
      label: 'Test Execution',
    },
    {
      key: '/multi-service-test',
      icon: <LinkOutlined />,
      label: 'Multi-Service Test',
    },
    {
      key: '/reports',
      icon: <FileTextOutlined />,
      label: 'Reports',
    },
    {
      key: '/test-reports',
      icon: <HistoryOutlined />,
      label: 'Test Reports',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <AntHeader className="ant-layout-header">
      <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
        <div className="logo" style={{ marginRight: 48 }}>
          APITestGen
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ flex: 1, minWidth: 0 }}
        />
      </div>
    </AntHeader>
  );
};

export default Header; 