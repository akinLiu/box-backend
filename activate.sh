#!/bin/bash

# 检查虚拟环境是否存在，如果不存在则创建
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 升级pip并安装依赖
pip install --upgrade pip
pip install -r requirements.txt
