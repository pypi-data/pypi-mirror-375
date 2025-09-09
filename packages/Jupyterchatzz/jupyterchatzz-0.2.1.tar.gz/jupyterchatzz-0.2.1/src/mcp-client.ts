/**
 * MCP客户端类，处理与Jupyter MCP Server的通信
 */

import axios, { AxiosInstance } from 'axios';
import { McpTools } from './mcp-tools';

/**
 * 聊天消息接口
 */
export interface IChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

/**
 * 聊天请求接口
 */
export interface IChatRequest {
  model: string;
  messages: IChatMessage[];
  max_tokens?: number;
  temperature?: number;
  stream?: boolean;
  provider?: string; // 添加provider字段以支持aihubmix推理时代
}

/**
 * 聊天响应接口
 */
export interface IChatResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: {
    index: number;
    message: IChatMessage;
    finish_reason: string;
  }[];
}

/**
 * 代码执行请求接口
 */
export interface IExecuteRequest {
  code: string;
  cell_id?: string;
}

/**
 * 代码执行响应接口
 */
export interface IExecuteResponse {
  success: boolean;
  output?: any;
  error?: string;
}

/**
 * MCP客户端配置接口
 */
export interface IMcpClientOptions {
  serverUrl: string;
  token?: string;
  model?: string;
  aihubmixApiUrl?: string;
  aihubmixApiKey?: string;
}

/**
 * MCP客户端类
 */
export class McpClient {
  private serverUrl: string;
  private token: string | undefined;
  private axiosInstance: AxiosInstance;
  private model: string;
  private aihubmixApiUrl: string | undefined;
  private aihubmixApiKey: string | undefined;
  private tools: McpTools;

  /**
   * 构造函数
   * @param options MCP客户端配置
   */
  constructor(options: IMcpClientOptions) {
    this.serverUrl = options.serverUrl;
    this.token = options.token;
    this.model = options.model || 'gpt-4o-mini';
    this.aihubmixApiUrl = options.aihubmixApiUrl;
    this.aihubmixApiKey = options.aihubmixApiKey;

    // 创建axios实例
    this.axiosInstance = axios.create({
      baseURL: this.serverUrl,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {})
      }
    });
    
    // 创建MCP工具实例
    this.tools = new McpTools({
      serverUrl: this.serverUrl,
      token: this.token
    });
  }
  
  /**
   * 设置使用的模型
   * @param model 模型名称
   */
  public setModel(model: string): void {
    this.model = model;
  }

  /**
   * 连接到MCP服务器
   * @param documentId 文档ID
   * @param documentUrl 文档URL
   * @param runtimeUrl 运行时URL
   * @returns 连接是否成功
   */
  public async connect(
    documentId: string,
    documentUrl: string = window.location.origin,
    runtimeUrl: string = window.location.origin
  ): Promise<boolean> {
    try {
      const response = await this.axiosInstance.put('/api/connect', {
        provider: 'jupyter',
        runtime_url: runtimeUrl,
        runtime_token: this.token,
        runtime_id: documentId, // 添加runtime_id字段
        document_url: documentUrl,
        document_id: documentId,
        document_token: this.token
      });

      return response.data.success === true;
    } catch (error) {
      console.error('Failed to connect to MCP server:', error);
      return false;
    }
  }

  /**
   * 检查MCP服务器健康状态
   * @returns 健康状态
   */
  public async checkHealth(): Promise<any> {
    try {
      const response = await this.axiosInstance.get('/api/healthz');
      return response.data;
    } catch (error) {
      console.error('Failed to check MCP server health:', error);
      throw error;
    }
  }

  /**
   * 停止MCP服务器
   * @returns 操作结果
   */
  public async stop(): Promise<boolean> {
    try {
      const response = await this.axiosInstance.delete('/api/stop');
      return response.data.success === true;
    } catch (error) {
      console.error('Failed to stop MCP server:', error);
      return false;
    }
  }
  
  /**
   * 发送聊天请求
   * @param messages 聊天消息数组
   * @param model 可选，使用的模型
   * @param temperature 可选，温度参数
   * @param maxTokens 可选，最大生成令牌数
   * @returns 聊天响应
   */
  public async chat(
    messages: IChatMessage[],
    model?: string,
    temperature?: number,
    maxTokens?: number
  ): Promise<IChatResponse> {
    try {
      // 调试输出
      console.log('Chat方法被调用，API配置：', {
        model: model || this.model,
        aihubmixApiUrl: this.aihubmixApiUrl || '未设置',
        aihubmixApiKey: this.aihubmixApiKey ? '已设置' : '未设置'
      });
      
      // 检查API配置是否为空字符串
      if (!this.aihubmixApiUrl || this.aihubmixApiUrl.trim() === '') {
        throw new Error('未配置aihubmix API URL，请在配置面板中填写API URL');
      }
      
      if (!this.aihubmixApiKey || this.aihubmixApiKey.trim() === '') {
        throw new Error('未配置aihubmix API密钥，请在配置面板中填写API密钥');
      }
      
      // 使用aihubmix API进行聊天
      if (this.aihubmixApiUrl && this.aihubmixApiKey) {
        // 创建aihubmix API的axios实例
        const aihubmixAxios = axios.create({
          baseURL: this.aihubmixApiUrl,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.aihubmixApiKey}`
          }
        });
        
        const request: IChatRequest = {
          model: model || this.model,
          messages,
          temperature,
          max_tokens: maxTokens
        };
        
        console.log('发送请求到aihubmix API:', {
          url: `${this.aihubmixApiUrl}/v1/chat/completions`,
          model: request.model,
          messageCount: request.messages.length
        });
        
        // 发送请求到aihubmix API
        const response = await aihubmixAxios.post('/v1/chat/completions', request);
        
        console.log('收到aihubmix API响应:', {
          status: response.status,
          hasData: !!response.data,
          hasChoices: response.data && Array.isArray(response.data.choices)
        });
        
        // 获取助手回复
        if (!response.data || !response.data.choices || !response.data.choices[0] || !response.data.choices[0].message) {
          console.error('API响应格式错误:', response.data);
          throw new Error('API响应格式错误，请检查API配置');
        }
        
        const assistantMessage = response.data.choices[0].message.content;
        console.log('AI助手回复:', assistantMessage);
        
        // 暂时注释掉添加Markdown单元格，先确保聊天功能正常工作
        // await this.tools.appendMarkdownCell(`**AI助手**: ${assistantMessage}`);
        
        return response.data;
      } else {
        throw new Error('未配置aihubmix API，无法进行聊天');
      }
    } catch (error) {
      console.error('聊天请求失败:', error);
      throw error;
    }
  }
  
  /**
   * 执行代码
   * @param code 要执行的代码
   * @param cellId 可选，单元格ID
   * @returns 执行结果
   */
  public async executeCode(code: string, cellId?: string): Promise<IExecuteResponse> {
    try {
      // 使用MCP工具添加并执行代码单元格
      const outputs = await this.tools.appendExecuteCodeCell(code);
      
      return {
        success: true,
        output: outputs
      };
    } catch (error) {
      console.error('代码执行失败:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
  
  /**
   * 创建新的笔记本单元格
   * @param code 单元格代码内容
   * @param position 可选，插入位置
   * @returns 操作结果
   */
  public async createCell(code: string, position?: number): Promise<any> {
    try {
      if (position !== undefined) {
        // 插入代码单元格
        await this.tools.insertExecuteCodeCell(position, code);
      } else {
        // 添加代码单元格
        await this.tools.appendExecuteCodeCell(code);
      }
      return { success: true };
    } catch (error) {
      console.error('创建单元格失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取当前文档内容
   * @returns 文档内容
   */
  public async getDocument(): Promise<any> {
    try {
      // 使用MCP工具获取笔记本信息和所有单元格
      const notebookInfo = await this.tools.getNotebookInfo();
      const cells = await this.tools.readAllCells();
      
      return {
        ...notebookInfo,
        cells
      };
    } catch (error) {
      console.error('获取文档失败:', error);
      throw error;
    }
  }
}
