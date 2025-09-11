"""
XCoding Plugin 客户端

提供插件初始化、压缩和上传功能
"""

import os
import json
import zipfile
import tempfile
import shutil
import requests
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from getpass import getpass
import importlib.resources

from .exceptions import (
    PluginSDKError,
    PluginUploadError,
    PluginValidationError,
    PluginCompressionError,
    PluginInitializationError,
)


class PluginClient:
    """XCoding Plugin 客户端类"""

    def __init__(self, base_url: str = "http://localhost:8088"):
        """
        初始化插件客户端

        Args:
            base_url: XCoding 服务器基础 URL
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = None
        self.session = requests.Session()

    def set_api_token(self, token: str) -> None:
        """
        设置 API Token

        Args:
            token: API Token
        """
        self.api_token = token
        self.session.headers.update({"X-API-Token": token})

    def prompt_for_api_token(self) -> str:
        """
        提示用户输入 API Token

        Returns:
            用户输入的 API Token
        """
        if not self.api_token:
            token = getpass("请输入 API Token: ")
            self.set_api_token(token)
        return self.api_token

    def initialize_plugin(self, name: str, directory: str = ".") -> str:
        """
        初始化插件目录结构

        Args:
            name: 插件名称
            directory: 插件创建目录

        Returns:
            插件目录路径

        Raises:
            PluginInitializationError: 插件初始化失败
        """
        try:
            # 获取示例插件目录的路径
            # 使用importlib.resources访问包内的资源
            try:
                example_plugin_ref = importlib.resources.files("xcoding_plugin") / ".." / "example-python-plugin"
                example_plugin_dir = Path(str(example_plugin_ref))
            except (AttributeError, ImportError):
                # 如果importlib.resources不可用，回退到旧方法
                current_dir = Path(__file__).parent.parent
                example_plugin_dir = current_dir / "example-python-plugin"
            
            if not example_plugin_dir.exists():
                raise PluginInitializationError(f"示例插件目录不存在: {example_plugin_dir}")
            
            # 创建插件目录
            plugin_dir = Path(directory) / name
            plugin_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制示例插件文件
            for item in example_plugin_dir.iterdir():
                if item.is_file():
                    # 如果是文件，直接复制并根据名称进行替换
                    dest_file = plugin_dir / item.name
                    
                    if item.name == "plugin.yaml":
                        # 对于plugin.yaml文件，需要替换名称和描述
                        with open(item, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # 替换名称和描述
                        content = content.replace(
                            'name: "python-example"', 
                            f'name: "{name.lower()}"'
                        )
                        content = content.replace(
                            'display_name: "Python示例插件"', 
                            f'display_name: "{name}插件"'
                        )
                        content = content.replace(
                            'description: "一个支持所有动态表单类型的Python插件示例"', 
                            f'description: "{name}插件"'
                        )
                        
                        with open(dest_file, "w", encoding="utf-8") as f:
                            f.write(content)
                    elif item.name == "main.py":
                        # 对于main.py文件，需要替换描述文本
                        with open(item, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # 替换描述文本
                        content = content.replace(
                            '"""\nPython示例插件主脚本\n这是一个支持所有动态表单类型的Python插件示例，展示如何处理各种配置参数并生成输出\n"""', 
                            f'"""\n{name}插件主脚本\n这是一个基于示例插件创建的{name}插件\n"""'
                        )
                        content = content.replace(
                            'print("[INFO] Python示例插件开始执行...")', 
                            f'print("[INFO] {name}插件开始执行...")'
                        )
                        content = content.replace(
                            'print("[INFO] Python示例插件执行完成")', 
                            f'print("[INFO] {name}插件执行完成")'
                        )
                        
                        with open(dest_file, "w", encoding="utf-8") as f:
                            f.write(content)
                    elif item.name == "README.md":
                        # 对于README.md文件，需要替换标题和描述
                        with open(item, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # 替换标题和描述
                        content = content.replace(
                            '# Python示例插件', 
                            f'# {name}插件'
                        )
                        content = content.replace(
                            '这是一个支持所有动态表单类型的Python插件示例，用于演示XCoding平台的Python插件系统如何处理各种类型的配置参数。', 
                            f'这是一个基于示例插件创建的{name}插件。'
                        )
                        
                        with open(dest_file, "w", encoding="utf-8") as f:
                            f.write(content)
                    else:
                        # 其他文件直接复制
                        shutil.copy2(item, dest_file)
            
            return str(plugin_dir)

        except Exception as e:
            raise PluginInitializationError(f"初始化插件失败: {e}")

    def compress_plugin(self, plugin_dir: str, output_path: Optional[str] = None) -> str:
        """
        压缩插件目录为 ZIP 文件

        Args:
            plugin_dir: 插件目录路径
            output_path: 输出 ZIP 文件路径（可选）

        Returns:
            ZIP 文件路径

        Raises:
            PluginCompressionError: 插件压缩失败
            PluginValidationError: 插件验证失败
        """
        try:
            plugin_path = Path(plugin_dir)
            if not plugin_path.exists():
                raise PluginValidationError(f"插件目录不存在: {plugin_dir}")

            # 验证 plugin.json 或 plugin.yaml
            plugin_json_path = plugin_path / "plugin.json"
            plugin_yaml_path = plugin_path / "plugin.yaml"
            
            if plugin_json_path.exists():
                # 使用 plugin.json
                with open(plugin_json_path, "r", encoding="utf-8") as f:
                    plugin_config = json.load(f)
            elif plugin_yaml_path.exists():
                # 使用 plugin.yaml 并转换为 JSON 格式
                import yaml
                with open(plugin_yaml_path, "r", encoding="utf-8") as f:
                    yaml_config = yaml.safe_load(f)
                
                # 转换为 PluginManifest 格式
                plugin_config = {
                    "name": yaml_config.get("name", ""),
                    "display_name": yaml_config.get("display_name", yaml_config.get("name", "")),
                    "description": yaml_config.get("description", ""),
                    "category": yaml_config.get("category", "utility"),
                    "version": yaml_config.get("version", "1.0.0"),
                    "author": yaml_config.get("author", ""),
                    "icon": yaml_config.get("icon", ""),
                    "config": yaml_config.get("ui", {}),
                    "script": yaml_config.get("execution", {}).get("main_script", "main.py")
                }
                
                # 创建 plugin.json 文件
                with open(plugin_json_path, "w", encoding="utf-8") as f:
                    json.dump(plugin_config, f, indent=2, ensure_ascii=False)
            else:
                raise PluginValidationError(f"plugin.json 或 plugin.yaml 不存在: {plugin_path}")

            # 验证必需字段
            required_fields = ["name", "version", "script"]
            for field in required_fields:
                if field not in plugin_config:
                    raise PluginValidationError(f"plugin.json 缺少必需字段: {field}")

            # 确定输出路径
            if not output_path:
                plugin_name = plugin_config["name"]
                plugin_version = plugin_config["version"]
                output_path = f"{plugin_name}-{plugin_version}.zip"

            output_path = Path(output_path)
            if output_path.is_absolute():
                zip_path = output_path
            else:
                # 确保ZIP文件创建在插件目录的父目录中，避免被包含在ZIP文件中
                zip_path = plugin_path.parent / output_path
            
            # 如果ZIP文件已经存在于插件目录中，删除它
            old_zip_path = plugin_path / output_path
            if old_zip_path.exists():
                old_zip_path.unlink()

            # 创建 ZIP 文件
            print(f"[DEBUG] 创建ZIP文件: {zip_path}")
            added_files = []
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(plugin_path):
                    for file in files:
                        file_path = Path(root) / file
                        # 跳过ZIP文件本身，防止递归包含
                        if file_path == zip_path:
                            continue
                        # 计算相对路径，确保文件直接位于ZIP根目录下
                        arcname = file_path.relative_to(plugin_path)
                        # 添加到 ZIP
                        zipf.write(file_path, arcname)
                        added_files.append(str(arcname))
                        print(f"[DEBUG] 添加文件到ZIP: {arcname}")
            
            # 检查ZIP文件是否创建成功
            if zip_path.exists():
                zip_size = zip_path.stat().st_size
                print(f"[DEBUG] ZIP文件创建成功，大小: {zip_size} 字节")
                print(f"[DEBUG] ZIP文件包含的文件: {', '.join(added_files)}")
            else:
                print(f"[DEBUG] ZIP文件创建失败: {zip_path}")

            return str(zip_path)

        except PluginValidationError:
            raise
        except Exception as e:
            raise PluginCompressionError(f"压缩插件失败: {e}")

    def _check_plugin_exists(self, plugin_name: str) -> bool:
        """
        检查插件是否已存在

        Args:
            plugin_name: 插件名称

        Returns:
            插件是否存在
        """
        try:
            if not self.api_token:
                self.prompt_for_api_token()

            # 发送检查请求 - 使用获取插件列表的API来检查插件是否存在
            response = self.session.get(
                f"{self.base_url}/api/v1/plugins"
            )
            
            print(f"[DEBUG] 检查插件存在性响应状态码: {response.status_code}")
            print(f"[DEBUG] 检查插件存在性响应内容: {response.text}")

            # 检查响应
            if response.status_code == 200:
                result = response.json()
                
                # 尝试从不同的字段中获取插件列表
                plugins = []
                if "plugins" in result:
                    plugins = result["plugins"]
                elif "data" in result:
                    plugins = result["data"]
                elif isinstance(result, list):
                    plugins = result
                else:
                    # 尝试查找任何可能是插件列表的字段
                    for key, value in result.items():
                        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict) and "name" in value[0]:
                            plugins = value
                            break
                
                # 检查插件列表中是否包含指定名称的插件
                for plugin in plugins:
                    if plugin.get("name") == plugin_name:
                        return True
                return False
            else:
                # 如果检查失败，默认认为插件不存在
                print(f"[DEBUG] 检查插件存在性失败，默认认为插件不存在")
                return False

        except Exception as e:
            print(f"[DEBUG] 检查插件存在性异常: {e}")
            # 如果检查失败，默认认为插件不存在
            return False

    def upload_plugin(self, zip_file: str) -> Dict[str, Any]:
        """
        上传插件 ZIP 文件到 XCoding 服务器，自动判断是上传新插件还是更新现有插件

        Args:
            zip_file: 插件 ZIP 文件路径

        Returns:
            上传结果

        Raises:
            PluginUploadError: 插件上传失败
        """
        try:
            if not self.api_token:
                self.prompt_for_api_token()

            zip_path = Path(zip_file)
            if not zip_path.exists():
                raise PluginUploadError(f"ZIP 文件不存在: {zip_file}")

            # 从ZIP文件名中提取插件名称
            plugin_name = zip_path.stem
            if '-' in plugin_name:
                # 如果文件名格式为 name-version.zip，则提取name部分
                plugin_name = '-'.join(plugin_name.split('-')[:-1])
            
            # 检查插件是否已存在
            print(f"[DEBUG] 检查插件是否存在: {plugin_name}")
            plugin_exists = self._check_plugin_exists(plugin_name)
            print(f"[DEBUG] 插件存在状态: {plugin_exists}")

            # 准备上传文件
            print(f"[DEBUG] 上传ZIP文件: {zip_path}")
            if zip_path.exists():
                zip_size = zip_path.stat().st_size
                print(f"[DEBUG] ZIP文件大小: {zip_size} 字节")
            else:
                print(f"[DEBUG] ZIP文件不存在: {zip_path}")
                
            with open(zip_path, "rb") as f:
                files = {"plugin": (zip_path.name, f, "application/zip")}
                
                # 根据插件是否存在选择不同的API端点
                if plugin_exists:
                    endpoint = f"{self.base_url}/api/v1/plugins/python/update"
                    operation = "更新"
                else:
                    endpoint = f"{self.base_url}/api/v1/plugins/python/upload"
                    operation = "上传"
                    
                print(f"[DEBUG] 发送{operation}请求到: {endpoint}")
                response = self.session.post(
                    endpoint,
                    files=files
                )
            
            print(f"[DEBUG] {operation}响应状态码: {response.status_code}")
            print(f"[DEBUG] {operation}响应内容: {response.text}")

            # 检查响应
            if response.status_code == 200:
                result = response.json()
                print(f"插件{operation}成功: {result}")
                return result
            else:
                error_msg = f"{operation}失败: HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        error_msg += f" - {error_data['message']}"
                    if "error" in error_data:
                        error_msg += f" - {error_data['error']}"
                    print(f"详细错误信息: {error_data}")
                except ValueError:
                    if response.text:
                        error_msg += f" - {response.text}"
                        print(f"服务器响应: {response.text}")
                raise PluginUploadError(error_msg)

        except PluginUploadError:
            raise
        except Exception as e:
            raise PluginUploadError(f"{operation}插件失败: {e}")

    def create_and_upload_plugin(self, name: str, directory: str = ".", keep_files: bool = False) -> Dict[str, Any]:
        """
        创建插件并上传到 XCoding 服务器

        Args:
            name: 插件名称
            directory: 工作目录
            keep_files: 是否保留创建的插件文件

        Returns:
            上传结果

        Raises:
            PluginSDKError: 插件创建或上传失败
        """
        temp_dir = None
        try:
            # 创建临时目录（如果需要）
            if keep_files:
                plugin_dir = Path(directory) / name
            else:
                temp_dir = tempfile.mkdtemp()
                plugin_dir = Path(temp_dir) / name

            # 初始化插件
            plugin_path = self.initialize_plugin(name, str(plugin_dir.parent))

            # 压缩插件
            zip_path = self.compress_plugin(plugin_path)

            # 上传插件
            result = self.upload_plugin(zip_path)

            return result

        except Exception as e:
            raise PluginSDKError(f"创建并上传插件失败: {e}")
        finally:
            # 清理临时目录
            if temp_dir and not keep_files:
                shutil.rmtree(temp_dir, ignore_errors=True)