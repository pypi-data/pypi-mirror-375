#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python示例插件主脚本
这是一个支持所有动态表单类型的Python插件示例，展示如何处理各种配置参数并生成输出
"""

import base64
import json
import sys
import os
import ast
from typing import Dict, Any, Union


def load_config() -> Dict[str, Any]:
    """从环境变量或配置文件加载插件配置"""
    config = {}
    
    # 辅助函数：获取环境变量，优先尝试Base64编码版本
    def get_env_var(key, default=None):
        # 首先尝试获取Base64编码的环境变量
        base64_key = f"PLUGIN_{key.upper()}_BASE64"
        base64_value = os.getenv(base64_key)
        if base64_value:
            try:
                # 解码Base64值
                decoded_bytes = base64.b64decode(base64_value)
                return decoded_bytes.decode('utf-8')
            except Exception as e:
                print(f"[WARNING] 解码Base64环境变量 {base64_key} 失败: {e}", file=sys.stderr)
        
        # 如果Base64版本不存在或解码失败，尝试获取原始版本
        original_key = f"PLUGIN_{key.upper()}"
        return os.getenv(original_key, default)
    
    # 从环境变量读取配置
    config['text_field'] = get_env_var('text_field', 'Hello from Python Plugin!')
    
    # 数字字段
    try:
        config['number_field'] = int(get_env_var('number_field', '5'))
    except ValueError:
        config['number_field'] = 5
    
    # 布尔字段
    config['boolean_field'] = get_env_var('boolean_field', 'true').lower() in ('true', '1', 'yes', 'on')
    
    # 选择字段
    config['select_field'] = get_env_var('select_field', 'option2')
    
    # 多行文本字段
    config['textarea_field'] = get_env_var('textarea_field', '这是默认的多行文本内容\n第二行内容\n第三行内容')
    
    # 数组字段
    try:
        array_str = get_env_var('array_field', '["item1", "item2", "item3"]')
        config['array_field'] = json.loads(array_str)
    except json.JSONDecodeError:
        config['array_field'] = ["item1", "item2", "item3"]
    
    # 对象字段
    try:
        object_str = get_env_var('object_field', '{"key1": "value1", "key2": "value2"}')
        config['object_field'] = json.loads(object_str)
    except json.JSONDecodeError:
        config['object_field'] = {"key1": "value1", "key2": "value2"}
    
    # JSON字段
    try:
        json_str = get_env_var('json_field', '{"name": "test", "value": 123, "enabled": true}')
        config['json_field'] = json.loads(json_str)
    except json.JSONDecodeError:
        config['json_field'] = {"name": "test", "value": 123, "enabled": true}
    
    # 处理SCRIPT字段（如果有）
    script_field = get_env_var('script', '')
    if script_field:
        config['script_field'] = script_field
    
    return config


def generate_output(config: Dict[str, Any]) -> str:
    """根据配置生成输出内容"""
    output_lines = []
    output_lines.append("=== Python示例插件输出 ===")
    output_lines.append("")
    
    # 文本字段输出
    output_lines.append("[文本字段]")
    output_lines.append(f"文本内容: {config['text_field']}")
    output_lines.append("")
    
    # 数字字段输出
    output_lines.append("[数字字段]")
    output_lines.append(f"数字值: {config['number_field']}")
    output_lines.append(f"数字乘以2: {config['number_field'] * 2}")
    output_lines.append("")
    
    # 布尔字段输出
    output_lines.append("[布尔字段]")
    output_lines.append(f"布尔值: {config['boolean_field']}")
    output_lines.append(f"布尔值取反: {not config['boolean_field']}")
    output_lines.append("")
    
    # 选择字段输出
    output_lines.append("[选择字段]")
    output_lines.append(f"选择的选项: {config['select_field']}")
    output_lines.append("")
    
    # 多行文本字段输出
    output_lines.append("[多行文本字段]")
    output_lines.append("多行文本内容:")
    for line in config['textarea_field'].split('\n'):
        output_lines.append(f"  {line}")
    output_lines.append("")
    
    # 数组字段输出
    output_lines.append("[数组字段]")
    output_lines.append(f"数组内容: {config['array_field']}")
    output_lines.append("数组元素:")
    for i, item in enumerate(config['array_field'], 1):
        output_lines.append(f"  {i}. {item}")
    output_lines.append("")
    
    # 对象字段输出
    output_lines.append("[对象字段]")
    output_lines.append(f"对象内容: {config['object_field']}")
    output_lines.append("对象键值对:")
    for key, value in config['object_field'].items():
        output_lines.append(f"  {key}: {value}")
    output_lines.append("")
    
    # JSON字段输出
    output_lines.append("[JSON字段]")
    output_lines.append(f"JSON内容: {config['json_field']}")
    output_lines.append("格式化的JSON:")
    output_lines.append(json.dumps(config['json_field'], indent=2, ensure_ascii=False))
    output_lines.append("")
    
    return '\n'.join(output_lines)


def main():
    """插件主入口函数"""
    try:
        print("[INFO] Python示例插件开始执行...")
        
        # 加载配置
        config = load_config()
        print(f"[INFO] 加载配置: {json.dumps(config, indent=2, ensure_ascii=False)}")
        
        # 生成输出
        output = generate_output(config)
        
        print("[INFO] 插件执行结果:")
        print("=" * 50)
        print(output)
        print("=" * 50)
        
        print("[INFO] Python示例插件执行完成")
        return 0
        
    except Exception as e:
        print(f"[ERROR] 插件执行失败: {str(e)}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())