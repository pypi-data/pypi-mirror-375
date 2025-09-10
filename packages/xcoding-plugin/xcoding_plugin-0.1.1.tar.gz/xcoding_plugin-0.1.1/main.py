#!/usr/bin/env python3
"""
XCoding Plugin Python 包入口点

此文件作为 XCoding Plugin Python 包的入口点，调用命令行接口。
"""

import sys
from pathlib import Path

# 添加源码路径以便导入包
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from xcoding_plugin.cli import main as cli_main
except ImportError:
    print("无法导入 xcoding_plugin，请确保已正确安装包")
    sys.exit(1)


if __name__ == "__main__":
    cli_main()
