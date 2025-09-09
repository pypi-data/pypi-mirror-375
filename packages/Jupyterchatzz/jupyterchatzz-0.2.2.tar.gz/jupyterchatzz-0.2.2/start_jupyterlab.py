import subprocess
import sys
import os

def main():
    """启动JupyterLab并加载我们的扩展"""
    print("正在启动JupyterLab...")
    
    # 使用子进程启动JupyterLab
    cmd = [sys.executable, "-m", "jupyter", "lab", "--no-browser"]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # 实时输出日志
        print("JupyterLab正在启动，请查看以下URL：")
        for line in process.stdout:
            print(line, end='')
            # 如果检测到JupyterLab已启动，可以在这里添加额外逻辑
            if "Jupyter Server" in line and "is running at:" in line:
                print("\n\n请在浏览器中打开上面的URL，然后在顶部菜单栏中查找MCP菜单。")
                print("如果没有看到MCP菜单，请检查浏览器控制台是否有错误信息。")
    
    except KeyboardInterrupt:
        print("\n用户中断，正在关闭JupyterLab...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"启动JupyterLab时出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
