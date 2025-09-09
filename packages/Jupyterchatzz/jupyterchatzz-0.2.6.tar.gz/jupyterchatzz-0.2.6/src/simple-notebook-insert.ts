/**
 * 简化的笔记本代码插入功能
 * 直接使用JupyterLab的API而不是HTTP请求
 */

import { INotebookTracker } from '@jupyterlab/notebook';
import { NotebookActions } from '@jupyterlab/notebook';

export async function insertCodeToNotebook(
  code: string, 
  notebookTracker: INotebookTracker
): Promise<string> {
  try {
    console.log('插入代码到当前笔记本:', code);
    
    // 获取当前活动的笔记本
    const widget = notebookTracker.currentWidget;
    if (!widget) {
      throw new Error('没有找到活动的笔记本');
    }

    const notebook = widget.content;
    
    // 在当前单元格下方插入新的代码单元格
    NotebookActions.insertBelow(notebook);
    
    // 获取刚刚插入的单元格
    const activeCell = notebook.activeCell;
    if (!activeCell) {
      throw new Error('无法获取活动单元格');
    }

    // 设置单元格内容
    activeCell.model.sharedModel.setSource(code);
    
    // 确保单元格类型是code
    if (activeCell.model.type !== 'code') {
      // 如果不是代码单元格，转换为代码单元格
      NotebookActions.changeCellType(notebook, 'code');
    }
    
    console.log(`代码已成功插入到笔记本`);
    return `代码已成功插入到笔记本`;
    
  } catch (error) {
    console.error('插入代码失败:', error);
    throw error;
  }
}

export async function insertAndExecuteCodeToNotebook(
  code: string, 
  notebookTracker: INotebookTracker
): Promise<string> {
  try {
    console.log('插入并执行代码到当前笔记本:', code);
    
    // 获取当前活动的笔记本
    const widget = notebookTracker.currentWidget;
    if (!widget) {
      throw new Error('没有找到活动的笔记本');
    }

    const notebook = widget.content;
    
    // 在当前单元格下方插入新的代码单元格
    NotebookActions.insertBelow(notebook);
    
    // 获取刚刚插入的单元格
    const activeCell = notebook.activeCell;
    if (!activeCell) {
      throw new Error('无法获取活动单元格');
    }

    // 设置单元格内容
    activeCell.model.sharedModel.setSource(code);
    
    // 确保单元格类型是code
    if (activeCell.model.type !== 'code') {
      // 如果不是代码单元格，转换为代码单元格
      NotebookActions.changeCellType(notebook, 'code');
    }
    
    console.log(`代码已成功插入到笔记本，开始执行...`);
    
    // 等待一小段时间确保单元格完全设置完成
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // 执行当前单元格
    await NotebookActions.run(notebook, widget.sessionContext);
    
    console.log(`代码已成功执行`);
    return `代码已成功插入并执行`;
    
  } catch (error) {
    console.error('插入并执行代码失败:', error);
    throw error;
  }
}

export async function insertMarkdownToNotebook(
  markdown: string, 
  notebookTracker: INotebookTracker
): Promise<string> {
  try {
    console.log('插入Markdown到当前笔记本:', markdown);
    
    // 获取当前活动的笔记本
    const widget = notebookTracker.currentWidget;
    if (!widget) {
      throw new Error('没有找到活动的笔记本');
    }

    const notebook = widget.content;
    
    // 在当前单元格下方插入新的单元格
    NotebookActions.insertBelow(notebook);
    
    // 获取刚刚插入的单元格
    const activeCell = notebook.activeCell;
    if (!activeCell) {
      throw new Error('无法获取活动单元格');
    }

    // 转换为Markdown单元格
    NotebookActions.changeCellType(notebook, 'markdown');
    
    // 设置单元格内容
    activeCell.model.sharedModel.setSource(markdown);
    
    console.log(`Markdown已成功插入到笔记本`);
    return `Markdown已成功插入到笔记本`;
    
  } catch (error) {
    console.error('插入Markdown失败:', error);
    throw error;
  }
}
