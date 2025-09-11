/**
 * HLA-Compass UI Module Template
 * 
 * This template provides a complete React UI for your module.
 * Replace the TODOs with your actual implementation.
 */

import React, { useState, useCallback } from 'react';
import { 
  Button, 
  Input, 
  Card, 
  Alert, 
  Space, 
  Typography, 
  Spin, 
  Table,
  Form,
  Row,
  Col,
  message 
} from 'antd';
import { SearchOutlined, ClearOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

// Module props interface
interface ModuleProps {
  onExecute: (params: any) => Promise<any>;
  initialParams?: any;
}

// Result data interface
interface ResultItem {
  id: string;
  displayValue: string;
  score: number;
  metadata: Record<string, any>;
}

/**
 * Main UI Component
 */
const ModuleUI: React.FC<ModuleProps> = ({ onExecute, initialParams }) => {
  // State management
  const [form] = Form.useForm();
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<ResultItem[] | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(async (values: any) => {
    // Clear previous state
    setError(null);
    setResults(null);
    setSummary(null);
    setLoading(true);

    try {
      // TODO: Prepare your input parameters
      const params = {
        param1: values.param1,
        param2: values.param2
        // Add more parameters as needed
      };

      // Execute the module
      const result = await onExecute(params);

      // Handle the response
      if (result.status === 'success') {
        setResults(result.results);
        setSummary(result.summary);
        message.success('Processing completed successfully');
      } else {
        setError(result.error?.message || 'Processing failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  }, [onExecute]);

  /**
   * Clear form and results
   */
  const handleClear = useCallback(() => {
    form.resetFields();
    setResults(null);
    setSummary(null);
    setError(null);
  }, [form]);

  /**
   * Table columns configuration
   */
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 150
    },
    {
      title: 'Result',
      dataIndex: 'displayValue',
      key: 'displayValue',
      render: (text: string) => <Text>{text}</Text>
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      width: 100,
      render: (score: number) => (
        <Text strong style={{ color: score > 0.8 ? 'green' : 'orange' }}>
          {(score * 100).toFixed(1)}%
        </Text>
      )
    }
  ];

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <Card>
        <Title level={3}>Module Name</Title>
        <Paragraph>
          TODO: Add your module description here.
          Explain what your module does and how to use it.
        </Paragraph>
      </Card>

      {/* Input Form */}
      <Card style={{ marginTop: '20px' }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={initialParams}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Parameter 1"
                name="param1"
                rules={[{ required: true, message: 'This field is required' }]}
              >
                <Input 
                  placeholder="Enter value for parameter 1"
                  disabled={loading}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Parameter 2"
                name="param2"
              >
                <Input 
                  placeholder="Optional parameter"
                  disabled={loading}
                />
              </Form.Item>
            </Col>
          </Row>

          {/* TODO: Add more form fields as needed */}

          {/* Action Buttons */}
          <Space>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              htmlType="submit"
              loading={loading}
              size="large"
            >
              Process
            </Button>
            <Button
              icon={<ClearOutlined />}
              onClick={handleClear}
              disabled={loading}
              size="large"
            >
              Clear
            </Button>
          </Space>
        </Form>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          style={{ marginTop: '20px' }}
        />
      )}

      {/* Loading State */}
      {loading && (
        <Card style={{ marginTop: '20px', textAlign: 'center' }}>
          <Spin size="large" />
          <div style={{ marginTop: '10px' }}>
            <Text>Processing your request...</Text>
          </div>
        </Card>
      )}

      {/* Results Display */}
      {results && !loading && (
        <Card style={{ marginTop: '20px' }}>
          <Title level={4}>Results</Title>

          {/* Summary Statistics */}
          {summary && (
            <Alert
              message="Summary"
              description={
                <Space>
                  <Text>Total: {summary.total}</Text>
                  <Text>|</Text>
                  <Text>Average Score: {(summary.average_score * 100).toFixed(1)}%</Text>
                  <Text>|</Text>
                  <Text>Max: {(summary.max_score * 100).toFixed(1)}%</Text>
                  <Text>|</Text>
                  <Text>Min: {(summary.min_score * 100).toFixed(1)}%</Text>
                </Space>
              }
              type="success"
              style={{ marginBottom: '20px' }}
            />
          )}

          {/* Results Table */}
          <Table
            dataSource={results}
            columns={columns}
            rowKey="id"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} items`
            }}
            expandable={{
              expandedRowRender: (record: ResultItem) => (
                <div style={{ padding: '10px' }}>
                  <Text strong>Metadata:</Text>
                  <pre>{JSON.stringify(record.metadata, null, 2)}</pre>
                </div>
              ),
              rowExpandable: (record) => Object.keys(record.metadata).length > 0
            }}
          />
        </Card>
      )}
    </div>
  );
};

export default ModuleUI;