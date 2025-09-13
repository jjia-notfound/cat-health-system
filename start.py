#!/usr/bin/env python3
"""
猫咪健康管理系统启动脚本
一键启动应用，自动处理端口和依赖问题
"""

import subprocess
import sys
import os


def check_requirements():
    """检查并安装依赖"""
    try:
        __import__('flask')
        __import__('pandas')
        __import__('sklearn')
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("正在安装依赖...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        return True


def start_app():
    """启动应用"""
    print("🐱 启动猫咪健康管理系统...")
    print("🔍 正在检查端口占用情况...")
    
    # 启动应用
    try:
        subprocess.run([sys.executable, "flask_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        print("💡 提示：程序已自动处理端口冲突，请查看上方输出的实际端口号")
        print("💡 如果仍有问题，请尝试重启应用或检查系统防火墙设置")


if __name__ == "__main__":
    check_requirements()
    start_app()