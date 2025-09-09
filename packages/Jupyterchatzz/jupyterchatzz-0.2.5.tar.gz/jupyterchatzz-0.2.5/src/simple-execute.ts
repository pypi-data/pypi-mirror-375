/**
 * 简化的代码执行功能
 */

import { McpNotebookClient } from './mcp-notebook-client';

export async function executeCodeInNotebook(code: string): Promise<string> {
  try {
    // 从URL中获取笔记本路径
    const path = window.location.pathname;
    const match = path.match(/\/lab\/tree\/(.+\.ipynb)/);
    if (!match || !match[1]) {
      throw new Error('无法确定笔记本路径');
    }

    const notebookPath = match[1];
    console.log('执行代码到笔记本:', notebookPath);
    
    // 创建notebook客户端
    const notebookClient = new McpNotebookClient('http://localhost:8888', notebookPath);
    
    // 添加代码单元格
    const result = await notebookClient.appendCodeCell(code);
    
    return result;
  } catch (error) {
    console.error('执行代码失败:', error);
    throw error;
  }
}
