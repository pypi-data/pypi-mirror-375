# 发布指南

本文档描述了如何构建、打包和发布Jupyterchatzz扩展。

## 构建和打包

使用提供的打包脚本：

```bash
python build_package.py
```

这将执行以下步骤：
1. 安装依赖
2. 构建TypeScript代码
3. 构建JupyterLab扩展
4. 构建Python包

构建完成后，打包文件将位于`dist`目录下。

## 手动构建步骤

如果您想手动执行构建步骤，可以按照以下顺序执行命令：

```bash
# 安装依赖
jlpm install

# 构建TypeScript代码
jlpm run build:lib

# 构建JupyterLab扩展
python -m jupyter labextension build .

# 构建Python包
python -m pip install build
python -m build
```

## 发布到PyPI

构建完成后，您可以将扩展发布到PyPI：

```bash
# 安装twine
pip install twine

# 上传到PyPI
twine upload dist/*
```

## 版本管理

更新版本号：

1. 修改`package.json`中的`version`字段
2. 修改`pyproject.toml`中的`version`字段
3. 提交更改并创建一个新的Git标签

```bash
# 创建Git标签
git tag v0.1.1
git push origin v0.1.1
```

## 安装已发布的扩展

用户可以通过以下命令安装已发布的扩展：

```bash
pip install jupyterchatzz
```

或者从本地wheel文件安装：

```bash
pip install ./dist/jupyterchatzz-0.1.1-py3-none-any.whl
```