"""
XCoding Plugin 异常类
"""


class PluginSDKError(Exception):
    """XCoding Plugin SDK 基础异常类"""
    pass


class PluginUploadError(PluginSDKError):
    """插件上传异常"""
    pass


class PluginValidationError(PluginSDKError):
    """插件验证异常"""
    pass


class PluginCompressionError(PluginSDKError):
    """插件压缩异常"""
    pass


class PluginInitializationError(PluginSDKError):
    """插件初始化异常"""
    pass