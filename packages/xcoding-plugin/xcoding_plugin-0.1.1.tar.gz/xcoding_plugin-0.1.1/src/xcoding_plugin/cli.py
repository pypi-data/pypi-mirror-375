"""
XCoding Plugin 命令行接口
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .client import PluginClient
from .exceptions import PluginSDKError


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Returns:
        参数解析器
    """
    parser = argparse.ArgumentParser(
        description="XCoding Plugin 工具 - 用于初始化、压缩和上传插件\n\n插件上传方式：\n\n1、uv run main.py quick-upload <插件名> <token>\n\n2. 插件目录内快速上传格式: uv run main.py . <token> (在插件目录内执行)",
        formatter_class = argparse.RawDescriptionHelpFormatter
    )
    
    # 全局参数
    parser.add_argument(
        "--base-url",
        default="http://localhost:8088",
        help="XCoding 服务器基础 URL (默认: http://localhost:8088)"
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化新插件目录结构")
    init_parser.add_argument("name", help="插件名称")
    init_parser.add_argument(
        "--dir",
        default=".",
        help="插件创建目录 (默认: 当前目录)"
    )
    

    
    # quick-upload 命令
    quick_upload_parser = subparsers.add_parser(
        "quick-upload", 
        help="快速压缩并上传现有插件到 XCoding 服务器，自动判断是上传新插件还是更新现有插件"
    )
    quick_upload_parser.add_argument("name", help="插件名称")
    quick_upload_parser.add_argument("token", help="API Token")
    quick_upload_parser.add_argument(
        "--dir",
        default=".",
        help="插件目录 (默认: 当前目录)"
    )
    
    return parser


def handle_init_command(args, client: PluginClient) -> None:
    """
    处理 init 命令
    
    Args:
        args: 命令行参数
        client: PluginClient 实例
    """
    try:
        plugin_path = client.initialize_plugin(args.name, args.dir)
        print(f"插件已创建: {plugin_path}")
    except PluginSDKError as e:
        print(f"初始化插件失败: {e}", file=sys.stderr)
        sys.exit(1)


def handle_quick_upload_command(args, client: PluginClient) -> None:
    """
    处理 quick-upload 命令
    
    Args:
        args: 命令行参数
        client: PluginClient 实例
    """
    try:
        # 设置 token
        client.set_api_token(args.token)
        
        # 构建插件目录路径
        plugin_dir = Path(args.dir) / args.name
        
        # 压缩插件
        zip_path = client.compress_plugin(str(plugin_dir))
        print(f"插件已压缩: {zip_path}")
        
        # 上传插件（自动判断是上传新插件还是更新现有插件）
        result = client.upload_plugin(zip_path)
        print(f"插件处理成功: {result}")
    except PluginSDKError as e:
        print(f"快速处理插件失败: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """
    主函数
    """
    # 首先检查是否是插件目录内快速上传格式：. token
    if len(sys.argv) >= 3 and sys.argv[1] == "." and not sys.argv[2].startswith('--'):
        # 这是插件目录内快速上传格式
        token = sys.argv[2]
        
        # 获取当前目录名作为插件名称
        current_dir = Path.cwd().name
        
        # 检查是否有--base-url参数
        base_url = "http://localhost:8088"  # 默认值
        for i in range(3, len(sys.argv)):
            if sys.argv[i] == '--base-url' and i + 1 < len(sys.argv):
                base_url = sys.argv[i + 1]
                break
        
        # 创建客户端
        client = PluginClient(base_url=base_url)
        
        # 设置token
        client.set_api_token(token)
        
        # 创建模拟的快速上传参数
        class QuickUploadArgs:
            def __init__(self, name, token, dir="."):
                self.name = name
                self.token = token
                self.dir = dir
        
        quick_args = QuickUploadArgs(current_dir, token, "..")
        
        # 执行快速上传
        handle_quick_upload_command(quick_args, client)
        return
    
    # 使用正常的参数解析
    parser = create_parser()
    args = parser.parse_args()
    

    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 创建客户端
    client = PluginClient(base_url=args.base_url)
    
    # 根据命令调用相应的处理函数
    if args.command == "init":
        handle_init_command(args, client)
    elif args.command == "quick-upload":
        handle_quick_upload_command(args, client)
    else:
        print(f"未知命令: {args.command}", file=sys.stderr)
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()