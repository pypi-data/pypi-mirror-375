#!/bin/bash
# 构建并发布到PyPI的脚本

echo "正在构建包..."
python3 -m build

echo "准备上传到PyPI..."
echo "请确保你已经配置了PyPI的token或用户名密码"
python3 -m twine upload dist/mcp_image_cutout-0.2.1*

echo "发布完成！"
echo "稍后可以使用: uvx mcp-image-cutout@0.2.1"
