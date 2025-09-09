/**
 * MCP工具封装，用于调用MCP服务器提供的工具
 */

import axios, { AxiosInstance } from 'axios';

/**
 * MCP工具接口
 */
export interface IMcpToolsOptions {
  serverUrl: string;
  token?: string;
}

/**
 * MCP工具类
 */
export class McpTools {
  private serverUrl: string;
  private token: string | undefined;
  private axiosInstance: AxiosInstance;

  /**
   * 构造函数
   * @param options MCP工具配置
   */
  constructor(options: IMcpToolsOptions) {
    this.serverUrl = options.serverUrl;
    this.token = options.token;

    // 创建axios实例
    this.axiosInstance = axios.create({
      baseURL: this.serverUrl,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {})
      }
    });
  }

  /**
   * 添加并执行代码单元格 (暂时不可用，直接使用JupyterLab API)
   * @param code 代码内容
   * @returns 执行结果
   */
  public async appendExecuteCodeCell(code: string): Promise<string[]> {
    // 这个方法现在不会被使用，因为我们直接使用JupyterLab的原生API
    throw new Error('请使用 insertCodeToNotebook 代替此方法');
  }

  /**
   * 添加Markdown单元格
   * @param markdown Markdown内容
   * @returns 执行结果
   */
  public async appendMarkdownCell(markdown: string): Promise<string> {
    try {
      // 打印请求信息
      console.log('发送appendMarkdownCell请求到:', `${this.serverUrl}/api/tools/append_markdown_cell`);
      
      // 修正API路径 - 直接使用工具名称，不带前缀
      const response = await this.axiosInstance.post('/api/tools/append_markdown_cell', {
        cell_source: markdown
      });
      return response.data;
    } catch (error) {
      console.error('添加Markdown单元格失败:', error);
      throw error;
    }
  }

  /**
   * 读取所有单元格
   * @returns 单元格列表
   */
  public async readAllCells(): Promise<any[]> {
    try {
      // 修正API路径
      const response = await this.axiosInstance.post('/api/tools/read_all_cells', {});
      return response.data;
    } catch (error) {
      console.error('读取所有单元格失败:', error);
      throw error;
    }
  }

  /**
   * 读取特定单元格
   * @param cellIndex 单元格索引
   * @returns 单元格信息
   */
  public async readCell(cellIndex: number): Promise<any> {
    try {
      // 修正API路径
      const response = await this.axiosInstance.post('/api/tools/read_cell', {
        cell_index: cellIndex
      });
      return response.data;
    } catch (error) {
      console.error('读取单元格失败:', error);
      throw error;
    }
  }

  /**
   * 执行单元格
   * @param cellIndex 单元格索引
   * @param timeout 超时时间（秒）
   * @returns 执行结果
   */
  public async executeCell(cellIndex: number, timeout: number = 300): Promise<string[]> {
    try {
      // 修正API路径
      const response = await this.axiosInstance.post('/api/tools/execute_cell_with_progress', {
        cell_index: cellIndex,
        timeout_seconds: timeout
      });
      return response.data;
    } catch (error) {
      console.error('执行单元格失败:', error);
      throw error;
    }
  }

  /**
   * 插入并执行代码单元格
   * @param cellIndex 单元格索引
   * @param code 代码内容
   * @returns 执行结果
   */
  public async insertExecuteCodeCell(cellIndex: number, code: string): Promise<string[]> {
    try {
      // 修正API路径
      const response = await this.axiosInstance.post('/api/tools/insert_execute_code_cell', {
        cell_index: cellIndex,
        cell_source: code
      });
      return response.data;
    } catch (error) {
      console.error('插入并执行代码单元格失败:', error);
      throw error;
    }
  }

  /**
   * 覆盖单元格内容
   * @param cellIndex 单元格索引
   * @param source 新内容
   * @returns 执行结果
   */
  public async overwriteCellSource(cellIndex: number, source: string): Promise<string> {
    try {
      // 修正API路径
      const response = await this.axiosInstance.post('/api/tools/overwrite_cell_source', {
        cell_index: cellIndex,
        cell_source: source
      });
      return response.data;
    } catch (error) {
      console.error('覆盖单元格内容失败:', error);
      throw error;
    }
  }

  /**
   * 获取笔记本信息
   * @returns 笔记本信息
   */
  public async getNotebookInfo(): Promise<any> {
    try {
      // 修正API路径
      const response = await this.axiosInstance.post('/api/tools/get_notebook_info', {});
      return response.data;
    } catch (error) {
      console.error('获取笔记本信息失败:', error);
      throw error;
    }
  }
}
