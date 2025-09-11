"""
XCoding Plugin Python Package

用于初始化用户插件、插件压缩、上传的Python包
"""

from xcoding_plugin.client import PluginClient
from xcoding_plugin.exceptions import PluginSDKError, PluginUploadError, PluginValidationError

__version__ = "0.1.0"
__all__ = ["PluginClient", "PluginSDKError", "PluginUploadError", "PluginValidationError"]