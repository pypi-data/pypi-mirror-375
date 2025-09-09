/**
 * MCP配置面板组件
 */

import React, { useState, useEffect } from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { McpClient } from './mcp-client';

/**
 * 配置项接口
 */
interface IConfig {
  serverUrl: string;
  documentToken: string;
  documentId: string;
  runtimeToken: string;
  model?: string;
  aihubmixApiUrl?: string;
  aihubmixApiKey?: string;
}

/**
 * 配置面板属性接口
 */
interface IConfigPanelProps {
  onConnect: (config: IConfig) => void;
  onStatusChange: (status: string) => void;
}

/**
 * 配置面板组件
 */
function ConfigPanel(props: IConfigPanelProps): React.ReactElement {
  const [config, setConfig] = useState<IConfig>({
    serverUrl: 'http://localhost:4040',
    documentToken: '',
    documentId: '',
    runtimeToken: '',
    model: 'gpt-4o-mini',
    aihubmixApiUrl: '',
    aihubmixApiKey: ''
  });
  const [connecting, setConnecting] = useState<boolean>(false);
  const [status, setStatus] = useState<string>('未连接');

  // 处理输入变化
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 处理连接按钮点击
  const handleConnect = async () => {
    setConnecting(true);
    setStatus('正在连接...');
    props.onStatusChange('正在连接...');
    
    // 调试输出
    console.log('配置面板中的API配置：', {
      model: config.model,
      aihubmixApiUrl: config.aihubmixApiUrl,
      aihubmixApiKey: config.aihubmixApiKey ? '已设置' : '未设置'
    });

    try {
      // 打印配置信息
      console.log('准备连接MCP服务器，配置信息:', {
        serverUrl: config.serverUrl,
        documentId: config.documentId,
        token: config.documentToken ? '已设置' : '未设置',
        model: config.model,
        aihubmixApiUrl: config.aihubmixApiUrl ? '已设置' : '未设置',
        aihubmixApiKey: config.aihubmixApiKey ? '已设置' : '未设置'
      });
      
      const mcpClient = new McpClient({
        serverUrl: config.serverUrl,
        token: config.documentToken,
        model: config.model,
        aihubmixApiUrl: config.aihubmixApiUrl,
        aihubmixApiKey: config.aihubmixApiKey
      });

      // 检查服务器健康状态
      try {
        await mcpClient.checkHealth();
      } catch (error) {
        setStatus('MCP服务器未运行或无法访问');
        props.onStatusChange('MCP服务器未运行或无法访问');
        setConnecting(false);
        return;
      }

      // 连接到MCP服务器
      const connected = await mcpClient.connect(
        config.documentId,
        window.location.origin,
        window.location.origin
      );

      if (connected) {
        setStatus('已连接');
        props.onStatusChange('已连接');
        props.onConnect(config);
      } else {
        setStatus('连接失败');
        props.onStatusChange('连接失败');
      }
    } catch (error) {
      console.error('连接过程中出错:', error);
      setStatus('连接错误');
      props.onStatusChange('连接错误');
    } finally {
      setConnecting(false);
    }
  };

  // 自动填充当前笔记本路径
  useEffect(() => {
    // 从URL中获取当前笔记本路径
    const path = window.location.pathname;
    const match = path.match(/\/lab\/tree\/(.+\.ipynb)/);
    if (match && match[1]) {
      setConfig(prev => ({
        ...prev,
        documentId: match[1]
      }));
    }

    // 从localStorage中获取保存的配置
    const savedConfig = localStorage.getItem('mcp-config');
    if (savedConfig) {
      try {
        const parsedConfig = JSON.parse(savedConfig);
        setConfig(prev => ({
          ...prev,
          ...parsedConfig
        }));
      } catch (e) {
        console.error('解析保存的配置失败:', e);
      }
    }
  }, []);

  // 保存配置到localStorage
  useEffect(() => {
    localStorage.setItem('mcp-config', JSON.stringify(config));
  }, [config]);

  return (
    <div className="jp-mcp-config-panel">
      <h3>MCP服务器配置</h3>
      <div className="jp-mcp-config-status">
        状态: <span className={`jp-mcp-status-${status === '已连接' ? 'connected' : 'disconnected'}`}>{status}</span>
      </div>
      <div className="jp-mcp-config-form">
        <div className="jp-mcp-config-field">
          <label htmlFor="serverUrl">服务器URL:</label>
          <input
            type="text"
            id="serverUrl"
            name="serverUrl"
            value={config.serverUrl}
            onChange={handleChange}
            placeholder="http://localhost:4040"
          />
        </div>
        <div className="jp-mcp-config-field">
          <label htmlFor="documentId">笔记本路径:</label>
          <input
            type="text"
            id="documentId"
            name="documentId"
            value={config.documentId}
            onChange={handleChange}
            placeholder="notebook.ipynb"
          />
        </div>
        <div className="jp-mcp-config-field">
          <label htmlFor="documentToken">文档令牌:</label>
          <input
            type="text"
            id="documentToken"
            name="documentToken"
            value={config.documentToken}
            onChange={handleChange}
            placeholder="Jupyter令牌"
          />
        </div>
        <div className="jp-mcp-config-field">
          <label htmlFor="runtimeToken">运行时令牌:</label>
          <input
            type="text"
            id="runtimeToken"
            name="runtimeToken"
            value={config.runtimeToken}
            onChange={handleChange}
            placeholder="与文档令牌相同"
          />
        </div>
        
        <h4>AihubMix推理时代API配置</h4>
        
        <div className="jp-mcp-config-field">
          <label htmlFor="model">AI模型:</label>
          <select
            id="model"
            name="model"
            value={config.model}
            onChange={(e) => setConfig(prev => ({
              ...prev,
              model: e.target.value
            }))}
          >
            <option value="gpt-4o-mini">GPT-4o-mini</option>
            <option value="gpt-4o">GPT-4o</option>
            <option value="gpt-4">GPT-4</option>
            <option value="claude-3-opus">Claude-3-Opus</option>
            <option value="claude-3-sonnet">Claude-3-Sonnet</option>
          </select>
        </div>
        
        <div className="jp-mcp-config-field">
          <label htmlFor="aihubmixApiUrl">AihubMix API URL:</label>
          <input
            type="text"
            id="aihubmixApiUrl"
            name="aihubmixApiUrl"
            value={config.aihubmixApiUrl}
            onChange={handleChange}
            placeholder="https://api.aihubmix.com"
          />
        </div>
        
        <div className="jp-mcp-config-field">
          <label htmlFor="aihubmixApiKey">AihubMix API密钥:</label>
          <input
            type="password"
            id="aihubmixApiKey"
            name="aihubmixApiKey"
            value={config.aihubmixApiKey}
            onChange={handleChange}
            placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
          />
        </div>
        <div className="jp-mcp-config-actions">
          <button
            className="jp-mod-styled jp-mod-accept"
            onClick={handleConnect}
            disabled={
              connecting || 
              !config.serverUrl || 
              !config.documentId || 
              !config.aihubmixApiUrl || 
              !config.aihubmixApiKey
            }
          >
            {connecting ? '连接中...' : '连接'}
          </button>
        </div>
      </div>
      <div className="jp-mcp-config-help">
        <p>
          <strong>提示:</strong> 请确保MCP服务器已经启动，并且可以通过上面的URL访问。
        </p>
        <p>
          启动MCP服务器的命令示例:
        </p>
        <pre>
          python -m jupyter_mcp_server.server --transport streamable-http --document-url http://localhost:8888 --document-token &lt;token&gt; --document-id notebook.ipynb --runtime-url http://localhost:8888 --runtime-token &lt;token&gt; --port 4040
        </pre>
      </div>
    </div>
  );
}

/**
 * 配置面板Widget类
 */
export class McpConfigPanelWidget extends ReactWidget {
  private _onConnect: (config: IConfig) => void;
  private _onStatusChange: (status: string) => void;

  constructor(options: { onConnect: (config: IConfig) => void, onStatusChange: (status: string) => void }) {
    super();
    this.addClass('jp-mcp-config-panel-widget');
    this._onConnect = options.onConnect;
    this._onStatusChange = options.onStatusChange;
  }

  protected render(): React.ReactElement {
    return <ConfigPanel onConnect={this._onConnect} onStatusChange={this._onStatusChange} />;
  }
}
