/**
 * MCP管理器类，负责管理MCP客户端和状态
 */

import { McpClient } from './mcp-client';
import { ISignal, Signal } from '@lumino/signaling';

/**
 * MCP配置接口
 */
export interface IMcpConfig {
  serverUrl: string;
  documentToken: string;
  documentId: string;
  runtimeToken: string;
  model?: string;
  aihubmixApiUrl?: string;
  aihubmixApiKey?: string;
}

/**
 * MCP状态类型
 */
export type McpStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

/**
 * MCP管理器类
 */
export class McpManager {
  private _client: McpClient | null = null;
  private _config: IMcpConfig | null = null;
  private _status: McpStatus = 'disconnected';
  private _statusChanged = new Signal<this, McpStatus>(this);
  private _currentModel: string = 'gpt-4o-mini';

  /**
   * 获取当前状态
   */
  get status(): McpStatus {
    return this._status;
  }

  /**
   * 获取状态变化信号
   */
  get statusChanged(): ISignal<this, McpStatus> {
    return this._statusChanged;
  }

  /**
   * 获取当前配置
   */
  get config(): IMcpConfig | null {
    return this._config;
  }

  /**
   * 获取MCP客户端
   */
  get client(): McpClient | null {
    return this._client;
  }
  
  /**
   * 获取当前模型
   */
  get currentModel(): string {
    return this._currentModel;
  }
  
  /**
   * 设置当前模型
   */
  set currentModel(model: string) {
    this._currentModel = model;
    if (this._client) {
      this._client.setModel(model);
    }
  }

  /**
   * 连接到MCP服务器
   * @param config MCP配置
   */
  async connect(config: IMcpConfig): Promise<boolean> {
    this._setStatus('connecting');
    this._config = config;
    
    // 调试输出
    console.log('McpManager.connect被调用，配置：', {
      serverUrl: config.serverUrl,
      model: config.model,
      aihubmixApiUrl: config.aihubmixApiUrl,
      aihubmixApiKey: config.aihubmixApiKey ? '已设置' : '未设置'
    });

    try {
      // 创建新的MCP客户端
      this._client = new McpClient({
        serverUrl: config.serverUrl,
        token: config.documentToken,
        model: config.model || this._currentModel,
        aihubmixApiUrl: config.aihubmixApiUrl,
        aihubmixApiKey: config.aihubmixApiKey
      });
      
      // 更新当前模型
      if (config.model) {
        this._currentModel = config.model;
      }

      // 检查服务器健康状态
      try {
        await this._client.checkHealth();
      } catch (error) {
        console.error('MCP服务器健康检查失败:', error);
        this._setStatus('error');
        return false;
      }

      // 连接到MCP服务器
      const connected = await this._client.connect(
        config.documentId,
        window.location.origin,
        window.location.origin
      );

      if (connected) {
        this._setStatus('connected');
        return true;
      } else {
        this._setStatus('error');
        return false;
      }
    } catch (error) {
      console.error('连接MCP服务器时出错:', error);
      this._setStatus('error');
      return false;
    }
  }

  /**
   * 断开连接
   */
  async disconnect(): Promise<void> {
    if (this._client) {
      try {
        await this._client.stop();
      } catch (error) {
        console.error('断开MCP服务器连接时出错:', error);
      } finally {
        this._client = null;
        this._setStatus('disconnected');
      }
    }
  }
  
  /**
   * 发送聊天消息
   * @param messages 聊天消息数组
   * @param model 可选，使用的模型
   * @returns 聊天响应
   */
  async sendChatMessage(messages: any[], model?: string): Promise<any> {
    if (!this._client) {
      throw new Error('未连接到MCP服务器');
    }
    
    console.log('McpManager.sendChatMessage被调用，配置:', {
      model: model || this._currentModel,
      messageCount: messages.length,
      clientInitialized: !!this._client,
      clientHasAihubmixConfig: !!(this._client && 
        this._client.hasOwnProperty('aihubmixApiUrl') && 
        this._client.hasOwnProperty('aihubmixApiKey'))
    });
    
    try {
      return await this._client.chat(
        messages,
        model || this._currentModel
      );
    } catch (error) {
      console.error('发送聊天消息时出错:', error);
      throw error;
    }
  }
  
  /**
   * 执行代码
   * @param code 要执行的代码
   * @param cellId 可选，单元格ID
   * @returns 执行结果
   */
  async executeCode(code: string, cellId?: string): Promise<any> {
    if (!this._client) {
      throw new Error('未连接到MCP服务器');
    }
    
    return await this._client.executeCode(code, cellId);
  }
  
  /**
   * 创建新的笔记本单元格
   * @param code 单元格代码内容
   * @param position 可选，插入位置
   * @returns 操作结果
   */
  async createCell(code: string, position?: number): Promise<any> {
    if (!this._client) {
      throw new Error('未连接到MCP服务器');
    }
    
    return await this._client.createCell(code, position);
  }

  /**
   * 设置状态并发出信号
   * @param status 新状态
   */
  private _setStatus(status: McpStatus): void {
    if (this._status !== status) {
      this._status = status;
      this._statusChanged.emit(status);
    }
  }
}
