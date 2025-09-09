# 🚀 Jupyter MCP Server 扩展部署指南

这个文档详细说明了如何在不同设备上安装和部署 Jupyterchatzz 扩展。

## 📋 系统要求

### 基本要求
- **Python**: 3.8 或更高版本
- **Node.js**: 16.x 或更高版本
- **npm/yarn**: 最新版本
- **JupyterLab**: 4.0 或更高版本

### 推荐配置
- **内存**: 最少 4GB RAM
- **存储**: 最少 2GB 可用空间
- **网络**: 稳定的互联网连接（用于AI服务）

## 🎯 部署方案

### 方案一：开发模式安装（推荐用于开发/测试）

#### 1. 环境准备
```bash
# 安装Python依赖
pip install jupyterlab>=4.0
pip install fastapi uvicorn
pip install jupyter

# 安装Node.js依赖
npm install -g yarn
```

#### 2. 下载项目
```bash
# 方式1: 从Git仓库克隆
git clone <your-repository-url>
cd jupyter-mcp-server-main

# 方式2: 下载压缩包并解压
# 下载项目ZIP文件，解压到目标目录
```

#### 3. 安装扩展
```bash
# 进入扩展目录
cd Jupyterchatzz

# 安装Python包（开发模式）
pip install -e .

# 安装Node.js依赖
npm install

# 构建扩展
npm run build:prod

# 验证安装
jupyter labextension list
```

#### 4. 启动服务
```bash
# 启动JupyterLab
jupyter lab

# 在另一个终端启动MCP服务器
cd ..
python start_mcp_server.py
```

### 方案二：打包分发安装（推荐用于生产使用）

#### 1. 创建分发包
在开发机器上执行：

```bash
# 进入扩展目录
cd Jupyterchatzz

# 清理并构建
npm run clean
npm run build:prod

# 创建Python包
python setup.py sdist bdist_wheel

# 创建安装包
tar -czf jupyterchatzz-v0.2.2.tar.gz \
  --exclude=node_modules \
  --exclude=.git \
  --exclude=__pycache__ \
  .
```

#### 2. 在目标设备上安装
```bash
# 解压安装包
tar -xzf jupyterchatzz-v0.2.2.tar.gz
cd Jupyterchatzz

# 安装依赖
pip install jupyterlab>=4.0 fastapi uvicorn
npm install

# 安装扩展
pip install .

# 重新启动JupyterLab
jupyter lab
```

### 方案三：Docker容器化部署

#### 1. 创建Dockerfile
```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install -r requirements.txt

# 安装JupyterLab扩展
WORKDIR /app/Jupyterchatzz
RUN npm install && \
    npm run build:prod && \
    pip install .

# 暴露端口
EXPOSE 8888 4040

# 启动命令
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
```

#### 2. 构建和运行容器
```bash
# 构建镜像
docker build -t jupyterchatzz:v0.2.2 .

# 运行容器
docker run -p 8888:8888 -p 4040:4040 \
  -v $(pwd)/notebooks:/app/notebooks \
  jupyterchatzz:v0.2.2
```

## ⚙️ 配置说明

### 1. API配置
在使用前需要配置AI服务API：

```bash
# 在JupyterLab中打开MCP配置面板
# 设置以下参数：
# - API URL: https://api.aihubmix.com/v1/chat/completions
# - API Key: 您的API密钥
# - 模型: GPT-4o-mini 或其他支持的模型
```

### 2. 环境变量配置
可以通过环境变量预设配置：

```bash
export AIHUBMIX_API_URL="https://api.aihubmix.com/v1/chat/completions"
export AIHUBMIX_API_KEY="your-api-key-here"
export MCP_PORT="4040"
```

## 🔧 故障排除

### 常见问题

1. **扩展未显示**
   ```bash
   # 检查扩展状态
   jupyter labextension list
   
   # 重新安装
   pip uninstall Jupyterchatzz
   pip install -e .
   ```

2. **MCP连接失败**
   ```bash
   # 检查服务器状态
   curl http://localhost:4040/api/healthz
   
   # 重新启动MCP服务器
   python start_mcp_server.py
   ```

3. **构建失败**
   ```bash
   # 清理缓存
   npm run clean
   rm -rf node_modules
   npm install
   npm run build:prod
   ```

### 日志调试
```bash
# 查看JupyterLab日志
jupyter lab --debug

# 查看扩展日志
# 在浏览器开发者工具中查看控制台输出
```

## 📦 版本管理

### 更新扩展
```bash
# 获取最新代码
git pull origin main

# 重新构建
cd Jupyterchatzz
npm run build:prod

# 重新安装
pip install -e . --force-reinstall
```

### 版本回退
```bash
# 回退到特定版本
git checkout v0.1.3
npm run build:prod
pip install -e . --force-reinstall
```

## 🌐 网络部署

### 服务器部署
```bash
# 使用nginx反向代理
# /etc/nginx/sites-available/jupyterchatzz
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/mcp/ {
        proxy_pass http://localhost:4040;
        proxy_set_header Host $host;
    }
}
```

### SSL证书配置
```bash
# 使用Let's Encrypt
certbot --nginx -d your-domain.com
```

## 📱 移动设备支持

扩展的响应式设计支持移动设备访问，最小支持宽度为350px。

## 🔐 安全考虑

1. **API密钥安全**: 使用环境变量存储API密钥
2. **网络安全**: 在生产环境中使用HTTPS
3. **访问控制**: 配置JupyterLab的用户认证

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查项目的CHANGELOG.md了解已知问题
3. 在项目仓库中创建Issue

---

**当前版本**: v0.2.2  
**更新日期**: 2024-12-19  
**兼容性**: JupyterLab 4.0+
