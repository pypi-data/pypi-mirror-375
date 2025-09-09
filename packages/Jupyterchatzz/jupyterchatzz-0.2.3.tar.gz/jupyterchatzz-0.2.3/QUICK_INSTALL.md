# 🚀 快速安装指南

## 一键安装（推荐）

### Linux/macOS
```bash
# 下载项目
git clone <repository-url>
cd jupyter-mcp-server-main/Jupyterchatzz

# 给安装脚本执行权限
chmod +x install.sh

# 运行安装脚本
./install.sh

# 启动服务
./start_jupyterchatzz.sh
```

### Windows
```cmd
# 下载项目
git clone <repository-url>
cd jupyter-mcp-server-main\Jupyterchatzz

# 运行安装脚本
install.bat

# 启动服务
start_jupyterchatzz.bat
```

## 手动安装

### 1. 系统要求
- Python 3.8+
- Node.js 16+
- JupyterLab 4.0+

### 2. 安装依赖
```bash
pip install -r requirements.txt
npm install
```

### 3. 构建安装
```bash
npm run build:prod
pip install -e .
```

### 4. 启动服务
```bash
# 终端1: 启动MCP服务器
python ../start_mcp_server.py

# 终端2: 启动JupyterLab
jupyter lab
```

## 📋 使用步骤

1. **启动服务**后，在浏览器中打开JupyterLab
2. 在右侧面板找到 **"🤖 AI助手"** 标签
3. 点击 **"连接MCP"** 按钮
4. 配置API设置：
   - API URL: `https://api.aihubmix.com/v1/chat/completions`
   - API Key: 您的密钥
   - 模型: `GPT-4o-mini`
5. 开始与AI助手对话！

## 🔧 故障排除

- **扩展未显示**: 运行 `jupyter labextension list` 检查
- **连接失败**: 检查MCP服务器是否在端口4040运行
- **构建错误**: 删除 `node_modules` 后重新安装

## 📞 获取帮助

- 查看详细文档: [DEPLOYMENT.md](./DEPLOYMENT.md)
- 查看更新日志: [CHANGELOG.md](./CHANGELOG.md)
