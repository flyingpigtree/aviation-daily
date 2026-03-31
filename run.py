# 运行所有步骤的入口脚本

import subprocess
import sys
import os

# 使用虚拟环境的Python
VENV_PYTHON = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
if os.path.exists(VENV_PYTHON):
    PYTHON = VENV_PYTHON
else:
    PYTHON = sys.executable

def run_step(name, script):
    print(f"\n{'='*50}")
    print(f"步骤: {name}")
    print('='*50)
    result = subprocess.run([PYTHON, f"scripts/{script}"])
    if result.returncode != 0:
        print(f"错误: {name} 失败")
        sys.exit(1)

if __name__ == '__main__':
    run_step("抓取新闻", "fetch.py")
    run_step("生成摘要", "summarize.py")
    run_step("构建网站", "build.py")
    print("\n" + "="*50)
    print("全部完成!")
    print("="*50)
