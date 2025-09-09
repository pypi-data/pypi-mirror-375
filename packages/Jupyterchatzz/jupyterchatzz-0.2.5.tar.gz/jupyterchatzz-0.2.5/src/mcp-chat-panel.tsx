import React, { useState, useEffect, useRef } from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { McpManager, IMcpConfig } from './mcp-manager';
import { SimpleChatClient, IChatMessage as ISimpleChatMessage } from './simple-chat-client';
// import { McpNotebookClient } from './mcp-notebook-client';
// import { executeCodeInNotebook } from './simple-execute';
import { insertCodeToNotebook, insertAndExecuteCodeToNotebook } from './simple-notebook-insert';
import { INotebookTracker } from '@jupyterlab/notebook';
import { IChatMessage as IMcpChatMessage } from './mcp-client';

/**
 * 聊天消息类型
 */
interface IChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  codeBlocks?: ICodeBlock[];
}

/**
 * 代码块类型
 */
interface ICodeBlock {
  id: string;
  code: string;
  language: string;
  executed: boolean;
  output?: string;
  error?: string;
}

/**
 * 聊天面板属性
 */
interface IChatPanelProps {
  mcpManager: McpManager;
  notebookTracker: INotebookTracker;
}

/**
 * 聊天面板组件
 */
const ChatPanel: React.FC<IChatPanelProps> = ({ mcpManager, notebookTracker }) => {
  const [messages, setMessages] = useState<IChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [model, setModel] = useState('gpt-4o-mini');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [connectionStatus, setConnectionStatus] = useState(mcpManager.status);
  const [isExecutingCode, setIsExecutingCode] = useState(false);
  const [autoExecuteCode, setAutoExecuteCode] = useState(true); // 默认开启自动执行

  // 监听MCP连接状态变化
  useEffect(() => {
    const onStatusChanged = (_: any, status: McpManager['status']) => {
      setConnectionStatus(status);
    };
    
    mcpManager.statusChanged.connect(onStatusChanged);
    
    return () => {
      mcpManager.statusChanged.disconnect(onStatusChanged);
    };
  }, [mcpManager]);

  // 自动滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 初始化系统消息
  useEffect(() => {
    setMessages([
      {
        id: '0',
        role: 'system',
        content: '欢迎使用AI助手！我可以帮助您编写和执行代码。AI生成的代码将自动插入到笔记本中并立即执行。您可以通过上方的开关控制是否启用自动执行。',
        timestamp: Date.now()
      }
    ]);
  }, []);

  // 从文本中提取代码块
  const extractCodeBlocks = (text: string): ICodeBlock[] => {
    const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
    const codeBlocks: ICodeBlock[] = [];
    let match;
    
    while ((match = codeBlockRegex.exec(text)) !== null) {
      const language = match[1].toLowerCase() || 'python';
      const code = match[2].trim();
      
      if (code) {
        codeBlocks.push({
          id: Date.now() + '-' + codeBlocks.length,
          code,
          language,
          executed: false
        });
      }
    }
    
    return codeBlocks;
  };

  // 简化的执行代码块函数
  const executeCodeBlock = async (codeBlock: ICodeBlock, messageId: string) => {
    setIsExecutingCode(true);
    try {
      console.log('执行代码块:', codeBlock.code);
      
      // 使用新的插入并执行函数
      const result = await insertAndExecuteCodeToNotebook(codeBlock.code, notebookTracker);
      
      // 更新消息状态
      setMessages(prev => prev.map(msg => {
        if (msg.id === messageId && msg.codeBlocks) {
          return {
            ...msg,
            codeBlocks: msg.codeBlocks.map(block => 
              block.id === codeBlock.id 
                ? { ...block, executed: true, output: result }
                : block
            )
          };
        }
        return msg;
      }));
      
      console.log(`代码执行成功: ${result}`);
    } catch (error) {
      console.error('执行代码失败:', error);
      
      // 更新消息状态显示错误
      setMessages(prev => prev.map(msg => {
        if (msg.id === messageId && msg.codeBlocks) {
          return {
            ...msg,
            codeBlocks: msg.codeBlocks.map(block => 
              block.id === codeBlock.id 
                ? { ...block, executed: true, error: error instanceof Error ? error.message : String(error) }
                : block
            )
          };
        }
        return msg;
      }));
    } finally {
      setIsExecutingCode(false);
    }
  };

  // 直接使用消息对象执行所有代码块
  const executeAllCodeBlocksWithMessage = async (message: IChatMessage) => {
    console.log('executeAllCodeBlocksWithMessage被调用，消息ID:', message.id);
    
    if (!message.codeBlocks || message.codeBlocks.length === 0) {
      console.log('消息中没有代码块');
      return;
    }
    
    setIsExecutingCode(true);
    console.log(`开始执行 ${message.codeBlocks.length} 个代码块`);
    
    try {
      for (let i = 0; i < message.codeBlocks.length; i++) {
        const codeBlock = message.codeBlocks[i];
        if (!codeBlock.executed) {
          console.log(`执行第 ${i + 1}/${message.codeBlocks.length} 个代码块:`, codeBlock.code.substring(0, 50) + '...');
          await executeCodeBlock(codeBlock, message.id);
          // 在代码块之间添加小延迟，避免并发问题
          await new Promise(resolve => setTimeout(resolve, 200));
        } else {
          console.log(`跳过第 ${i + 1} 个代码块（已执行）`);
        }
      }
      console.log('所有代码块执行完成');
    } catch (error) {
      console.error('执行代码块时出错:', error);
    } finally {
      setIsExecutingCode(false);
    }
  };

  // 执行所有代码块（通过消息ID查找）
  const executeAllCodeBlocks = async (messageId: string) => {
    console.log('executeAllCodeBlocks被调用，消息ID:', messageId);
    console.log('当前messages状态:', messages.length, '条消息');
    
    const message = messages.find(msg => msg.id === messageId);
    console.log('找到的消息:', message ? '存在' : '不存在');
    
    if (!message) {
      console.error('未找到指定ID的消息:', messageId);
      return;
    }
    
    await executeAllCodeBlocksWithMessage(message);
  };

  // 发送消息到MCP服务器
  const sendMessage = async () => {
    if (!input.trim() || isProcessing) return;
    
    // 检查MCP连接状态
    if (connectionStatus !== 'connected') {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'system',
          content: '未连接到MCP服务器，请先连接服务器。',
          timestamp: Date.now()
        }
      ]);
      return;
    }

    // 获取当前笔记本
    const notebook = notebookTracker.currentWidget?.content;
    if (!notebook) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'system',
          content: '未找到活动的笔记本，请打开一个笔记本。',
          timestamp: Date.now()
        }
      ]);
      return;
    }

    const userMessage: IChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: Date.now()
    };

    // 添加用户消息
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);

    try {
      // 准备发送给MCP服务器的消息
      const chatMessages: IMcpChatMessage[] = messages
        .filter(msg => msg.role !== 'system')
        .slice(-10)
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }));
      
      // 添加用户的新消息
      chatMessages.push({
        role: 'user',
        content: userMessage.content
      });

      // 使用SimpleChatClient进行聊天
      console.log('尝试使用SimpleChatClient进行聊天');
      
      // 从localStorage获取API配置
      const savedConfig = localStorage.getItem('mcp-config');
      let apiUrl = '';
      let apiKey = '';
      
      if (savedConfig) {
        try {
          const config = JSON.parse(savedConfig);
          apiUrl = config.aihubmixApiUrl || '';
          apiKey = config.aihubmixApiKey || '';
        } catch (e) {
          console.error('解析配置失败:', e);
        }
      }
      
      if (!apiUrl || !apiKey) {
        throw new Error('未找到API配置，请先在配置面板中设置');
      }
      
      const chatClient = new SimpleChatClient(apiUrl, apiKey, model);
      const simpleChatMessages: ISimpleChatMessage[] = chatMessages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      const response = await chatClient.chat(simpleChatMessages);
      
      if (response && response.choices && response.choices.length > 0) {
        const assistantContent = response.choices[0].message.content;
        
        // 提取代码块
        const codeBlocks = extractCodeBlocks(assistantContent);
        
        const assistantMessage: IChatMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content: assistantContent,
          timestamp: Date.now(),
          codeBlocks: codeBlocks.length > 0 ? codeBlocks : undefined
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        
        // 根据设置决定是否自动执行AI生成的代码块
        if (codeBlocks.length > 0 && autoExecuteCode) {
          console.log(`AI响应包含 ${codeBlocks.length} 个代码块，自动执行开关状态: ${autoExecuteCode}`);
          console.log('开始设置自动执行延迟...');
          // 延迟更长时间确保消息已经添加到状态中，并且React状态已经更新
          setTimeout(() => {
            console.log('开始执行自动执行代码块，消息ID:', assistantMessage.id);
            // 使用状态回调来获取最新的messages状态
            setMessages(currentMessages => {
              const targetMessage = currentMessages.find(msg => msg.id === assistantMessage.id);
              if (targetMessage && targetMessage.codeBlocks) {
                console.log('找到目标消息，开始执行代码块');
                // 异步执行代码块
                (async () => {
                  await executeAllCodeBlocksWithMessage(targetMessage);
                })();
              } else {
                console.error('未找到目标消息或代码块');
              }
              return currentMessages; // 返回原状态，不做修改
            });
          }, 500);
        } else if (codeBlocks.length > 0) {
          console.log(`AI响应包含 ${codeBlocks.length} 个代码块，等待手动执行（自动执行状态: ${autoExecuteCode}）`);
        }
        
      } else {
        throw new Error('无效的响应格式');
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'system',
          content: `发送消息失败: ${error instanceof Error ? error.message : String(error)}`,
          timestamp: Date.now()
        }
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  // 处理按键事件
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 渲染代码块
  const renderCodeBlock = (codeBlock: ICodeBlock, messageId: string) => {
    return (
      <div key={codeBlock.id} className="jp-mcp-code-block">
        <div className="jp-mcp-code-header">
          <span>{codeBlock.language}</span>
          <button
            className="jp-mcp-execute-button"
            onClick={() => executeCodeBlock(codeBlock, messageId)}
            disabled={isExecutingCode || codeBlock.executed}
          >
            {codeBlock.executed ? '已执行' : isExecutingCode ? '执行中...' : '插入并执行'}
          </button>
        </div>
        <pre>{codeBlock.code}</pre>
        {codeBlock.executed && (
          <div className={`jp-mcp-code-output ${codeBlock.error ? 'error' : ''}`}>
            <div className="jp-mcp-output-header">
              {codeBlock.error ? '错误' : '输出'}:
            </div>
            <pre>{codeBlock.error || codeBlock.output || '(无输出)'}</pre>
          </div>
        )}
      </div>
    );
  };

  // 渲染消息内容
  const renderMessageContent = (message: IChatMessage) => {
    if (!message.codeBlocks || message.codeBlocks.length === 0) {
      return <div className="jp-mcp-chat-message-content">{message.content}</div>;
    }

    // 替换消息中的代码块为自定义渲染
    let content = message.content;
    const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    let index = 0;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      // 添加代码块前的文本
      if (match.index > lastIndex) {
        parts.push(
          <span key={`text-${index}`}>
            {content.substring(lastIndex, match.index)}
          </span>
        );
      }

      // 添加代码块（使用占位符，实际代码块在下方单独渲染）
      parts.push(
        <div key={`placeholder-${index}`} className="jp-mcp-code-placeholder">
          [代码块 {index + 1}]
        </div>
      );

      lastIndex = match.index + match[0].length;
      index++;
    }

    // 添加最后一段文本
    if (lastIndex < content.length) {
      parts.push(
        <span key={`text-${index}`}>
          {content.substring(lastIndex)}
        </span>
      );
    }

    return (
      <>
        <div className="jp-mcp-chat-message-content">{parts}</div>
        <div className="jp-mcp-chat-code-blocks">
          {message.codeBlocks.map((block) => renderCodeBlock(block, message.id))}
          {message.codeBlocks.length > 0 && (
            <button
              className="jp-mcp-execute-all-button"
              onClick={() => executeAllCodeBlocks(message.id)}
              disabled={isExecutingCode || message.codeBlocks.every(block => block.executed)}
            >
              {isExecutingCode ? '执行中...' : '插入并执行所有代码'}
            </button>
          )}
        </div>
      </>
    );
  };

  return (
    <div className="jp-mcp-chat-panel">
      <div className="jp-mcp-chat-header">
        <h3>AI助手</h3>
        <div className="jp-mcp-chat-status">
          状态: <span className={`jp-mcp-status-${connectionStatus}`}>{connectionStatus}</span>
        </div>
        <div className="jp-mcp-chat-model">
          <label>模型: </label>
          <select 
            value={model} 
            onChange={(e) => {
              setModel(e.target.value);
              if (mcpManager.client) {
                mcpManager.currentModel = e.target.value;
              }
            }}
            disabled={isProcessing}
          >
            <option value="gpt-4o-mini">GPT-4o-mini (aihubmix推理时代)</option>
            <option value="gpt-4o">GPT-4o (aihubmix推理时代)</option>
            <option value="gpt-4">GPT-4 (aihubmix推理时代)</option>
            <option value="claude-3-opus">Claude-3-Opus (aihubmix推理时代)</option>
            <option value="claude-3-sonnet">Claude-3-Sonnet (aihubmix推理时代)</option>
          </select>
        </div>
        <div className="jp-mcp-chat-auto-execute">
          <label>
            <input 
              type="checkbox" 
              checked={autoExecuteCode}
              onChange={(e) => setAutoExecuteCode(e.target.checked)}
              disabled={isProcessing}
            />
            自动执行代码
          </label>
        </div>
      </div>
      
      <div className="jp-mcp-chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`jp-mcp-chat-message ${msg.role}`}>
            <div className="jp-mcp-chat-message-header">
              <span className="jp-mcp-chat-role">{msg.role === 'user' ? '用户' : msg.role === 'assistant' ? 'AI助手' : '系统'}</span>
              <span className="jp-mcp-chat-time">{new Date(msg.timestamp).toLocaleTimeString()}</span>
            </div>
            {renderMessageContent(msg)}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="jp-mcp-chat-input-container">
        <div className="jp-mcp-chat-input-row">
          <textarea
            className="jp-mcp-chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息，按Enter发送..."
            disabled={isProcessing || connectionStatus !== 'connected'}
          />
          <button 
            className="jp-mcp-chat-send-button" 
            onClick={sendMessage}
            disabled={isProcessing || !input.trim() || connectionStatus !== 'connected'}
          >
            {isProcessing ? '处理中...' : '发送'}
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * 聊天面板Widget
 */
export class McpChatPanelWidget extends ReactWidget {
  private _mcpManager: McpManager;
  private _notebookTracker: INotebookTracker;

  constructor(options: { mcpManager: McpManager; notebookTracker: INotebookTracker }) {
    super();
    this._mcpManager = options.mcpManager;
    this._notebookTracker = options.notebookTracker;
    this.id = 'mcp-chat-panel';
    this.title.label = 'AI助手';
    this.title.closable = true;
    this.addClass('jp-mcp-chat-panel-widget');
  }

  protected render(): React.ReactElement {
    return <ChatPanel mcpManager={this._mcpManager} notebookTracker={this._notebookTracker} />;
  }
}