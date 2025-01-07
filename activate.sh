#!/bin/bash

# 确保脚本在出错时退出
set -e

# 检查python3.9命令是否存在
if ! command -v python3.9 &> /dev/null; then
    echo "Error: python3.9 is not installed"
    exit 1
fi

# 删除旧的虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# 创建新的虚拟环境
echo "Creating new virtual environment..."
python3.9 -m venv venv

# 激活虚拟环境
echo "Activating virtual environment..."
source venv/bin/activate

# 升级pip
echo "Upgrading pip..."
python3.9 -m pip install --upgrade pip

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Environment setup completed successfully!"
