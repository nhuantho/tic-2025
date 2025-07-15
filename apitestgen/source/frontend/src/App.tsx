import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import APISpecs from './pages/APISpecs';
import TestCases from './pages/TestCases';
import TestExecution from './pages/TestExecution';
import Reports from './pages/Reports';
import TestReports from './pages/TestReports';
import MultiServiceTest from './pages/MultiServiceTest';

const { Content } = Layout;

function App() {
  return (
    <Layout>
      <Header />
      <Content className="ant-layout-content">
        <div className="site-layout-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/api-specs" element={<APISpecs />} />
            <Route path="/test-cases" element={<TestCases />} />
            <Route path="/test-execution" element={<TestExecution />} />
            <Route path="/multi-service-test" element={<MultiServiceTest />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/test-reports" element={<TestReports />} />
          </Routes>
        </div>
      </Content>
    </Layout>
  );
}

export default App; 