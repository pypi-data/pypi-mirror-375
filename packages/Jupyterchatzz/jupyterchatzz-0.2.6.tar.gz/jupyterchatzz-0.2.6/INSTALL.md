# Jupyterchatzz 安装和使用指南

本文档提供了安装和使用Jupyterchatzz扩展的详细说明。Jupyterchatzz是一个JupyterLab扩展，通过MCP服务器提供AI助手功能，可以在笔记本中自动编写和执行代码。

## 系统要求

- Python 3.8+
- JupyterLab 4.0+
- Jupyter MCP Server

## 安装步骤

### 1. 安装Jupyter MCP服务器

如果您还没有安装Jupyter MCP服务器，请先安装：

```bash
# 切换到Jupyter MCP服务器目录
cd ..

# 安装MCP服务器
pip install -e .
```

### 2. 安装Jupyterchatzz扩展

```bash
# 切换到扩展目录
cd Jupyterchatzz

# 安装依赖
jlpm

# 构建扩展
jlpm run build

# 安装扩展
pip install -e .
```

### 3. 验证安装

```bash
python -m jupyter labextension list
```

应该看到 `Jupyterchatzz v0.1.1 enabled ok` 的输出。

## 启动服务

### 1. 启动JupyterLab

使用提供的脚本：

```bash
python start_jupyterlab.py
```

或手动启动：

```bash
python -m jupyter lab
```

### 2. 启动MCP服务器

在另一个终端中，使用提供的脚本：

```bash
cd ..
python start_mcp_server.py
```

或手动启动：

```bash
python -m jupyter_mcp_server.server --port 8080
```

## 配置和使用

### 1. 连接MCP服务器

1. 在JupyterLab中，通过以下方式打开MCP配置面板：
   - 点击顶部菜单中的"MCP"（如果可见）
   - 或使用命令面板（Ctrl+Shift+C）搜索"MCP服务器配置"

2. 在配置面板中：
   - MCP服务器URL：`http://localhost:8080`
   - 笔记本ID：当前打开的笔记本路径（例如：`test_notebook.ipynb`）
   - AihubMix推理时代API配置：
     - 选择AI模型（默认：GPT-4o-mini）
     - AihubMix API URL：填写您的AihubMix API URL
     - AihubMix API密钥：填写您的AihubMix API密钥
   - 点击"连接"按钮

### 2. 使用AI助手

连接成功后：

1. 打开AI助手面板：
   - 点击MCP菜单中的"打开AI助手"
   - 或使用命令面板搜索"打开AI助手"

2. 在AI助手面板中：
   - 选择要使用的模型（默认：aihubmix）
   - 在输入框中输入您的问题或需求
   - 按Enter发送消息

3. AI助手将回复您的消息，并可能生成代码：
   - 代码块会自动识别并显示在消息下方
   - 点击"执行代码"按钮可以将代码写入笔记本并执行
   - 或点击"执行所有代码"一次执行所有代码块

## 常见问题解决

### 如果MCP菜单不可见

- 检查浏览器控制台是否有错误信息
- 确认扩展已正确安装：`python -m jupyter labextension list`
- 尝试使用命令面板（Ctrl+Shift+C）访问MCP功能
- 重启JupyterLab

### 如果连接到MCP服务器失败

- 确认MCP服务器正在运行
- 检查服务器URL是否正确
- 确认笔记本ID路径正确
- 检查JupyterLab控制台中的错误信息

### 如果代码执行失败

- 确保您已打开一个笔记本
- 检查笔记本内核是否正在运行
- 查看浏览器控制台是否有错误信息

### 如果您看到403错误

确保您使用的Jupyter令牌是正确的。您可以在JupyterLab启动时在终端中找到令牌信息。