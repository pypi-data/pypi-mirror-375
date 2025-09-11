/**
 * HLA-Compass UI Module Template
 * 
 * This template provides a complete React UI for your module.
 * Replace the TODOs with your actual implementation.
 * 
 * This template follows the HLA-Compass platform design system
 * with Tailwind CSS classes and scientific styling patterns.
 */

import React, { useState, useCallback } from 'react';
import './styles.css';
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
import { SearchOutlined, ClearOutlined, ExperimentOutlined } from '@ant-design/icons';

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
   * Table columns configuration - Scientific styling
   */
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      render: (text: string) => (
        <Text className="scientific-number font-mono text-sm">{text}</Text>
      )
    },
    {
      title: 'Result',
      dataIndex: 'displayValue',
      key: 'displayValue',
      render: (text: string) => (
        <Text className="text-base">{text}</Text>
      )
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      width: 120,
      render: (score: number) => (
        <Text 
          strong 
          className={`scientific-number font-mono ${
            score > 0.8 
              ? 'text-data-accent' 
              : score > 0.5 
              ? 'text-data-warning' 
              : 'text-data-danger'
          }`}
        >
          {(score * 100).toFixed(1)}%
        </Text>
      )
    }
  ];

  return (
    <div className="module-container max-w-screen-lg mx-auto p-5 space-y-5">
      {/* Header */}
      <Card className="bg-surface-primary shadow-soft border border-gray-200">
        <div className="flex items-center space-x-3 mb-4">
          <ExperimentOutlined className="text-2xl text-primary-500" />
          <Title level={3} className="m-0">Module Name</Title>
        </div>
        <Paragraph className="text-gray-600 mb-0">
          TODO: Add your module description here.
          Explain what your module does and how to use it.
        </Paragraph>
      </Card>

      {/* Input Form */}
      <Card className="bg-surface-primary shadow-soft border border-gray-200">
        <div className="mb-4">
          <Title level={4} className="text-gray-800 mb-2">Input Parameters</Title>
          <Text className="text-gray-600">Configure your analysis parameters</Text>
        </div>
        
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={initialParams}
          className="space-y-4"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Form.Item
              label={<span className="text-gray-700 font-medium">Parameter 1</span>}
              name="param1"
              rules={[{ required: true, message: 'This field is required' }]}
            >
              <Input 
                placeholder="Enter value for parameter 1"
                disabled={loading}
                className="scientific-input"
              />
            </Form.Item>
            
            <Form.Item
              label={<span className="text-gray-700 font-medium">Parameter 2</span>}
              name="param2"
            >
              <Input 
                placeholder="Optional parameter"
                disabled={loading}
                className="scientific-input"
              />
            </Form.Item>
          </div>

          {/* TODO: Add more form fields as needed */}

          {/* Action Buttons */}
          <div className="flex items-center space-x-3 pt-4 border-t border-gray-100">
            <Button
              type="primary"
              icon={<SearchOutlined />}
              htmlType="submit"
              loading={loading}
              size="large"
              className="bg-primary-500 hover:bg-primary-600 border-primary-500"
            >
              Process
            </Button>
            <Button
              icon={<ClearOutlined />}
              onClick={handleClear}
              disabled={loading}
              size="large"
              className="border-gray-300 text-gray-600 hover:border-gray-400"
            >
              Clear
            </Button>
          </div>
        </Form>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert
          message="Analysis Error"
          description={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          className="shadow-soft border-red-200 bg-red-50"
        />
      )}

      {/* Loading State */}
      {loading && (
        <Card className="text-center bg-surface-primary shadow-soft border border-gray-200">
          <div className="py-8">
            <Spin size="large" className="mb-4" />
            <div className="space-y-2">
              <Text className="block text-lg font-medium text-gray-700">
                Processing your request...
              </Text>
              <Text className="block text-sm text-gray-500">
                This may take a few moments depending on your data size
              </Text>
            </div>
          </div>
        </Card>
      )}

      {/* Results Display */}
      {results && !loading && (
        <Card className="bg-surface-primary shadow-soft border border-gray-200">
          <div className="mb-6">
            <Title level={4} className="text-gray-800 mb-2 flex items-center space-x-2">
              <ExperimentOutlined className="text-primary-500" />
              <span>Analysis Results</span>
            </Title>
            <Text className="text-gray-600">Your analysis has completed successfully</Text>
          </div>

          {/* Summary Statistics */}
          {summary && (
            <Alert
              message="Summary Statistics"
              description={
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                  <div className="text-center">
                    <div className="scientific-number font-mono text-2xl font-bold text-primary-600">
                      {summary.total}
                    </div>
                    <div className="text-sm text-gray-600">Total Items</div>
                  </div>
                  <div className="text-center">
                    <div className="scientific-number font-mono text-2xl font-bold text-data-accent">
                      {(summary.average_score * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Average Score</div>
                  </div>
                  <div className="text-center">
                    <div className="scientific-number font-mono text-2xl font-bold text-data-accent">
                      {(summary.max_score * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Max Score</div>
                  </div>
                  <div className="text-center">
                    <div className="scientific-number font-mono text-2xl font-bold text-data-warning">
                      {(summary.min_score * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Min Score</div>
                  </div>
                </div>
              }
              type="success"
              className="mb-6 border-green-200 bg-green-50"
            />
          )}

          {/* Results Table */}
          <div className="scientific-table-container">
            <Table
              dataSource={results}
              columns={columns}
              rowKey="id"
              className="scientific-table"
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (total, range) => 
                  `${range[0]}-${range[1]} of ${total} items`,
                className: "text-sm"
              }}
              expandable={{
                expandedRowRender: (record: ResultItem) => (
                  <div className="p-4 bg-gray-50 border-l-4 border-primary-300">
                    <Text strong className="text-gray-700 block mb-2">Metadata:</Text>
                    <pre className="bg-white p-3 rounded border text-sm font-mono overflow-auto max-h-64">
                      {JSON.stringify(record.metadata, null, 2)}
                    </pre>
                  </div>
                ),
                rowExpandable: (record) => Object.keys(record.metadata).length > 0
              }}
            />
          </div>
        </Card>
      )}
    </div>
  );
};

export default ModuleUI;