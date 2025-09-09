/**
 * MCP Notebook客户端，用于与笔记本交互
 * 直接向Jupyter服务器发送请求，而不通过MCP服务器
 */

import axios from 'axios';

export interface INotebookCell {
  cell_type: string;
  source: string[];
  metadata: any;
  outputs?: any[];
  execution_count?: number;
}

export interface INotebookContent {
  cells: INotebookCell[];
  metadata: any;
  nbformat: number;
  nbformat_minor: number;
}

export class McpNotebookClient {
  private jupyterUrl: string;
  private notebookPath: string;
  private token?: string;

  constructor(jupyterUrl: string = 'http://localhost:8888', notebookPath: string, token?: string) {
    this.jupyterUrl = jupyterUrl;
    this.notebookPath = notebookPath;
    this.token = token;
  }

  private getHeaders() {
    const headers: any = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `token ${this.token}`;
    }
    // 获取当前页面的token（从URL或cookie中）
    const currentToken = this.getCurrentToken();
    if (currentToken) {
      headers['Authorization'] = `token ${currentToken}`;
    }
    return headers;
  }

  private getCurrentToken(): string | null {
    // 尝试从URL参数中获取token
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    if (tokenFromUrl) {
      return tokenFromUrl;
    }

    // 尝试从cookies中获取token
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === '_xsrf' || name === 'jupyter-session-token') {
        return value;
      }
    }

    return null;
  }

  /**
   * 获取笔记本内容
   */
  async getNotebook(): Promise<INotebookContent> {
    try {
      const response = await axios.get(
        `${this.jupyterUrl}/api/contents/${this.notebookPath}`,
        { headers: this.getHeaders() }
      );
      return response.data.content;
    } catch (error) {
      console.error('获取笔记本失败:', error);
      throw error;
    }
  }

  /**
   * 保存笔记本内容
   */
  async saveNotebook(content: INotebookContent): Promise<void> {
    try {
      await axios.put(
        `${this.jupyterUrl}/api/contents/${this.notebookPath}`,
        {
          type: 'notebook',
          format: 'json',
          content: content
        },
        { headers: this.getHeaders() }
      );
    } catch (error) {
      console.error('保存笔记本失败:', error);
      throw error;
    }
  }

  /**
   * 添加代码单元格到笔记本末尾
   */
  async appendCodeCell(code: string): Promise<string> {
    try {
      console.log('添加代码单元格:', code);
      
      const notebook = await this.getNotebook();
      
      const newCell: INotebookCell = {
        cell_type: 'code',
        source: code.split('\n').map(line => line + '\n'),
        metadata: {},
        outputs: [],
        execution_count: undefined
      };

      notebook.cells.push(newCell);
      await this.saveNotebook(notebook);
      
      console.log('代码单元格添加成功');
      return `代码单元格已添加到位置 ${notebook.cells.length - 1}`;
    } catch (error) {
      console.error('添加代码单元格失败:', error);
      throw error;
    }
  }

  /**
   * 添加Markdown单元格到笔记本末尾
   */
  async appendMarkdownCell(markdown: string): Promise<string> {
    try {
      console.log('添加Markdown单元格:', markdown);
      
      const notebook = await this.getNotebook();
      
      const newCell: INotebookCell = {
        cell_type: 'markdown',
        source: markdown.split('\n').map(line => line + '\n'),
        metadata: {}
      };

      notebook.cells.push(newCell);
      await this.saveNotebook(notebook);
      
      console.log('Markdown单元格添加成功');
      return `Markdown单元格已添加到位置 ${notebook.cells.length - 1}`;
    } catch (error) {
      console.error('添加Markdown单元格失败:', error);
      throw error;
    }
  }

  /**
   * 执行代码单元格（通过kernel API）
   */
  async executeCodeCell(code: string): Promise<string> {
    try {
      console.log('执行代码:', code);
      
      // 首先添加代码单元格
      await this.appendCodeCell(code);
      
      // 注意：实际的代码执行需要通过kernel WebSocket连接
      // 这里我们只是添加了代码单元格，用户需要手动执行
      // 或者通过其他方式触发执行
      
      return '代码单元格已添加，请手动执行或等待自动执行';
    } catch (error) {
      console.error('执行代码失败:', error);
      throw error;
    }
  }
}
