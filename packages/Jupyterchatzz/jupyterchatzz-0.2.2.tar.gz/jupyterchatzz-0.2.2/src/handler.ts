/**
 * 处理与MCP服务器的请求
 */

import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';

/**
 * 调用API端点
 * @param endPoint API端点
 * @param init 请求选项
 * @returns 响应数据
 */
export async function requestAPI<T>(
  endPoint = '',
  init: RequestInit = {}
): Promise<T> {
  // 获取服务器连接设置
  const settings = ServerConnection.makeSettings();
  
  // 构建请求URL
  const requestUrl = URLExt.join(
    settings.baseUrl,
    'jupyterchatzz', // 扩展名称
    endPoint
  );
  
  // 发送请求
  let response: Response;
  try {
    response = await ServerConnection.makeRequest(requestUrl, init, settings);
  } catch (error) {
    throw new ServerConnection.NetworkError(error as any);
  }

  // 处理错误响应
  if (!response.ok) {
    const data = await response.json();
    throw new ServerConnection.ResponseError(response, data.message || data);
  }

  // 返回响应数据
  return await response.json();
}
