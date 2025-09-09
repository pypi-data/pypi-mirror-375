/**
 * 简化的聊天客户端，仅处理AI聊天，不涉及MCP工具
 */

import axios from 'axios';

export interface IChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface IChatResponse {
  choices: Array<{
    message: {
      content: string;
    };
  }>;
}

export class SimpleChatClient {
  private apiUrl: string;
  private apiKey: string;
  private model: string;

  constructor(apiUrl: string, apiKey: string, model: string = 'gpt-4o-mini') {
    this.apiUrl = apiUrl;
    this.apiKey = apiKey;
    this.model = model;
  }

  async chat(messages: IChatMessage[]): Promise<IChatResponse> {
    console.log('=== SimpleChatClient 开始聊天 ===');
    console.log('配置:', {
      apiUrl: this.apiUrl,
      hasApiKey: !!this.apiKey,
      model: this.model,
      messageCount: messages.length
    });

    if (!this.apiUrl || !this.apiKey) {
      throw new Error('API配置不完整');
    }

    try {
      const response = await axios({
        method: 'post',
        url: `${this.apiUrl}/v1/chat/completions`,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        data: {
          model: this.model,
          messages: messages,
          temperature: 0.7,
          max_tokens: 500
        },
        timeout: 30000
      });

      console.log('API响应:', {
        status: response.status,
        hasData: !!response.data,
        hasChoices: !!(response.data && response.data.choices)
      });

      if (response.data && response.data.choices && response.data.choices[0]) {
        console.log('聊天成功');
        return response.data;
      } else {
        throw new Error('API响应格式无效');
      }

    } catch (error: any) {
      console.error('聊天失败:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
      
      if (error.response?.status === 401) {
        throw new Error('API密钥无效');
      } else if (error.response?.status === 404) {
        throw new Error('API端点不存在');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('请求超时');
      } else {
        throw new Error(`聊天失败: ${error.message}`);
      }
    }
  }
}
