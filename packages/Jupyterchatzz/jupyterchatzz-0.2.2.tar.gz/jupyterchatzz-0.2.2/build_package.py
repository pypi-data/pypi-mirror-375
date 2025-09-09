#!/usr/bin/env python
"""
打包脚本，用于构建和打包JupyterLab扩展
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并打印输出"""
    print(f"执行: {cmd}")
    process = subprocess.Popen(
        cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf-8',
        errors='replace',
        cwd=cwd
    )
    
    for line in process.stdout:
        print(line.strip())
    
    process.wait()
    if process.returncode != 0:
        print(f"命令执行失败，退出码: {process.returncode}")
        sys.exit(process.returncode)

def build_package():
    """构建和打包扩展"""
    # 获取当前目录
    current_dir = Path(__file__).parent.absolute()
    
    print("===== 开始构建JupyterLab扩展 =====")
    
    # 1. 安装依赖
    print("\n1. 安装依赖")
    run_command("jlpm install", cwd=current_dir)
    
    # 2. 构建TypeScript代码
    print("\n2. 构建TypeScript代码")
    run_command("jlpm run build:lib", cwd=current_dir)
    
    # 3. 构建JupyterLab扩展
    print("\n3. 构建JupyterLab扩展")
    run_command("python -m jupyter labextension build .", cwd=current_dir)
    
    # 4. 构建Python包
    print("\n4. 构建Python包")
    run_command("python -m pip install build", cwd=current_dir)
    run_command("python -m build", cwd=current_dir)
    
    print("\n===== 构建完成 =====")
    print(f"打包文件位于: {current_dir / 'dist'}")

if __name__ == "__main__":
    build_package()
