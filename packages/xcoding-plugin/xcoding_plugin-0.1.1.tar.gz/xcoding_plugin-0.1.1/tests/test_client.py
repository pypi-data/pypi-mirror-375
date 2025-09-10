"""
XCoding Plugin Python 包测试模块

此模块包含 PluginClient 类的单元测试。
"""

import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from xcoding_plugin_sdk import PluginClient
from xcoding_plugin_sdk.exceptions import (
    PluginSDKError,
    PluginUploadError,
    PluginValidationError,
    PluginCompressionError,
    PluginInitializationError
)


class TestPluginClient(unittest.TestCase):
    """PluginClient 测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.client = PluginClient(base_url="http://test-server.com")
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialize_plugin(self):
        """测试插件初始化"""
        plugin_path = self.client.initialize_plugin("test-plugin", self.temp_dir)
        
        # 检查插件目录是否创建
        expected_path = Path(self.temp_dir) / "test-plugin"
        self.assertEqual(plugin_path, str(expected_path))
        self.assertTrue(expected_path.exists())
        
        # 检查必要文件和目录是否存在
        self.assertTrue((expected_path / "plugin.json").exists())
        self.assertTrue((expected_path / "src" / "main.py").exists())
        self.assertTrue((expected_path / "README.md").exists())
        
        # 检查 plugin.json 内容
        with open(expected_path / "plugin.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        self.assertEqual(config["name"], "test-plugin")
        self.assertEqual(config["version"], "0.1.0")
        self.assertEqual(config["entry_point"], "src/main.py")
    
    def test_initialize_plugin_existing_dir(self):
        """测试初始化已存在的插件目录"""
        plugin_path = Path(self.temp_dir) / "test-plugin"
        plugin_path.mkdir(parents=True, exist_ok=True)
        
        with self.assertRaises(PluginInitializationError):
            self.client.initialize_plugin("test-plugin", self.temp_dir)
    
    def test_compress_plugin(self):
        """测试插件压缩"""
        # 先创建一个插件
        plugin_dir = self.client.initialize_plugin("test-plugin", self.temp_dir)
        
        # 压缩插件
        zip_path = self.client.compress_plugin(plugin_dir)
        
        # 检查 ZIP 文件是否创建
        self.assertTrue(os.path.exists(zip_path))
        self.assertTrue(zip_path.endswith("test-plugin-0.1.0.zip"))
    
    def test_compress_plugin_nonexistent_dir(self):
        """测试压缩不存在的插件目录"""
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")
        
        with self.assertRaises(PluginCompressionError):
            self.client.compress_plugin(nonexistent_dir)
    
    def test_compress_plugin_missing_config(self):
        """测试压缩缺少配置文件的插件目录"""
        plugin_dir = Path(self.temp_dir) / "test-plugin"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        with self.assertRaises(PluginCompressionError):
            self.client.compress_plugin(str(plugin_dir))
    
    def test_compress_plugin_invalid_config(self):
        """测试压缩配置文件无效的插件目录"""
        plugin_dir = Path(self.temp_dir) / "test-plugin"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建无效的 plugin.json
        with open(plugin_dir / "plugin.json", "w", encoding="utf-8") as f:
            f.write("invalid json")
        
        with self.assertRaises(PluginValidationError):
            self.client.compress_plugin(str(plugin_dir))
    
    def test_compress_plugin_missing_required_fields(self):
        """测试压缩缺少必要字段的插件目录"""
        plugin_dir = Path(self.temp_dir) / "test-plugin"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建缺少必要字段的 plugin.json
        with open(plugin_dir / "plugin.json", "w", encoding="utf-8") as f:
            json.dump({"name": "test-plugin"}, f)
        
        with self.assertRaises(PluginValidationError):
            self.client.compress_plugin(str(plugin_dir))
    
    @patch('requests.Session.post')
    def test_upload_plugin_success(self, mock_post):
        """测试插件上传成功"""
        # 创建一个临时 ZIP 文件
        zip_path = os.path.join(self.temp_dir, "test-plugin-0.1.0.zip")
        with open(zip_path, "wb") as f:
            f.write(b"fake zip content")
        
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "123", "status": "uploaded"}
        mock_post.return_value = mock_response
        
        # 设置 API Token
        self.client.set_api_token("test-token")
        
        # 上传插件
        result = self.client.upload_plugin(zip_path)
        
        # 验证结果
        self.assertEqual(result, {"id": "123", "status": "uploaded"})
        
        # 验证请求参数
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://test-server.com/api/v1/plugins")
        self.assertIn("files", kwargs)
        self.assertIn("file", kwargs["files"])
    
    @patch('requests.Session.post')
    def test_upload_plugin_auth_error(self, mock_post):
        """测试插件上传认证错误"""
        # 创建一个临时 ZIP 文件
        zip_path = os.path.join(self.temp_dir, "test-plugin-0.1.0.zip")
        with open(zip_path, "wb") as f:
            f.write(b"fake zip content")
        
        # 模拟认证错误响应
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        # 设置 API Token
        self.client.set_api_token("invalid-token")
        
        # 上传插件，期望抛出异常
        with self.assertRaises(PluginUploadError) as context:
            self.client.upload_plugin(zip_path)
        
        self.assertEqual(str(context.exception), "API Token无效或已过期")
    
    def test_upload_plugin_nonexistent_file(self):
        """测试上传不存在的插件文件"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.zip")
        
        with self.assertRaises(PluginUploadError):
            self.client.upload_plugin(nonexistent_file)
    
    @patch('builtins.input', return_value="test-token")
    @patch('requests.Session.post')
    def test_upload_plugin_prompt_for_token(self, mock_post, mock_input):
        """测试上传插件时提示输入 API Token"""
        # 创建一个临时 ZIP 文件
        zip_path = os.path.join(self.temp_dir, "test-plugin-0.1.0.zip")
        with open(zip_path, "wb") as f:
            f.write(b"fake zip content")
        
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "123", "status": "uploaded"}
        mock_post.return_value = mock_response
        
        # 不设置 API Token，应该提示用户输入
        self.client.api_token = None
        
        # 上传插件
        result = self.client.upload_plugin(zip_path)
        
        # 验证结果
        self.assertEqual(result, {"id": "123", "status": "uploaded"})
        
        # 验证提示用户输入 API Token
        mock_input.assert_called_once_with("请输入X-API-Token: ")
        
        # 验证 API Token 已设置
        self.assertEqual(self.client.api_token, "test-token")
    
    @patch('xcoding_plugin.client.PluginClient.initialize_plugin')
    @patch('xcoding_plugin.client.PluginClient.compress_plugin')
    @patch('xcoding_plugin.client.PluginClient.upload_plugin')
    def test_create_and_upload_plugin(self, mock_upload, mock_compress, mock_initialize):
        """测试创建并上传插件"""
        # 设置模拟返回值
        mock_initialize.return_value = "/tmp/test-plugin"
        mock_compress.return_value = "/tmp/test-plugin-0.1.0.zip"
        mock_upload.return_value = {"id": "123", "status": "uploaded"}
        
        # 设置 API Token
        self.client.set_api_token("test-token")
        
        # 创建并上传插件
        result = self.client.create_and_upload_plugin("test-plugin", ".")
        
        # 验证结果
        self.assertEqual(result, {"id": "123", "status": "uploaded"})
        
        # 验证方法调用
        mock_initialize.assert_called_once_with("test-plugin", ".")
        mock_compress.assert_called_once_with("/tmp/test-plugin")
        mock_upload.assert_called_once_with("/tmp/test-plugin-0.1.0.zip", "test-token")
    
    @patch('xcoding_plugin.client.PluginClient.initialize_plugin')
    @patch('xcoding_plugin.client.PluginClient.compress_plugin')
    @patch('xcoding_plugin.client.PluginClient.upload_plugin')
    def test_create_and_upload_plugin_keep_files(self, mock_upload, mock_compress, mock_initialize):
        """测试创建并上传插件，保留文件"""
        # 设置模拟返回值
        plugin_dir = os.path.join(self.temp_dir, "test-plugin")
        mock_initialize.return_value = plugin_dir
        mock_compress.return_value = os.path.join(self.temp_dir, "test-plugin-0.1.0.zip")
        mock_upload.return_value = {"id": "123", "status": "uploaded"}
        
        # 设置 API Token
        self.client.set_api_token("test-token")
        
        # 创建并上传插件，保留文件
        result = self.client.create_and_upload_plugin("test-plugin", self.temp_dir, keep_files=True)
        
        # 验证结果
        self.assertEqual(result, {"id": "123", "status": "uploaded"})
        
        # 验证文件存在
        self.assertTrue(os.path.exists(plugin_dir))
        
        # 验证方法调用
        mock_initialize.assert_called_once_with("test-plugin", self.temp_dir)
        mock_compress.assert_called_once_with(plugin_dir)
        mock_upload.assert_called_once_with(os.path.join(self.temp_dir, "test-plugin-0.1.0.zip"), "test-token")


if __name__ == "__main__":
    unittest.main()