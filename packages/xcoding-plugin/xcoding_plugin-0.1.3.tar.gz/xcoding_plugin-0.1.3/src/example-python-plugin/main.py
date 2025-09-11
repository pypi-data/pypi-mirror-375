#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Plugin 1 - 支持PLUGIN_CONFIG_BASE64环境变量的Python插件
"""

import json
import sys
import os
import base64
from typing import Dict, Any


def load_config_from_base64() -> Dict[str, Any]:
    """从PLUGIN_CONFIG_BASE64环境变量加载配置"""
    config = {}
    
    # 获取PLUGIN_CONFIG_BASE64环境变量
    plugin_config_base64 = os.getenv('PLUGIN_CONFIG_BASE64')
    
    if plugin_config_base64:
        try:
            # 解码Base64值
            decoded_config = base64.b64decode(plugin_config_base64).decode('utf-8')
            print(f"[DEBUG] 从PLUGIN_CONFIG_BASE64解码的配置: {decoded_config}")
            
            # 解析JSON
            config = json.loads(decoded_config)
            print(f"[DEBUG] 解析后的配置: {config}")
            
            return config
        except Exception as e:
            print(f"[ERROR] 解码或解析PLUGIN_CONFIG_BASE64失败: {e}")
            return {}
    else:
        print("[WARNING] PLUGIN_CONFIG_BASE64环境变量不存在")
        return {}


def load_runtime_variables() -> Dict[str, Any]:
    """加载运行时变量并组成JSON环境"""
    runtime_vars = {}
    
    # 首先尝试获取PLUGIN_VAR_RUNTIME环境变量（JSON格式的完整运行时变量）
    plugin_var_runtime = os.getenv('PLUGIN_VAR_RUNTIME')
    if plugin_var_runtime:
        try:
            # 解析JSON格式的运行时变量
            runtime_vars = json.loads(plugin_var_runtime)
            print(f"[DEBUG] 从PLUGIN_VAR_RUNTIME加载的运行时变量: {runtime_vars}")
        except json.JSONDecodeError as e:
            print(f"[ERROR] 解析PLUGIN_VAR_RUNTIME失败: {e}")
            runtime_vars = {}
    
    # 如果没有PLUGIN_VAR_RUNTIME，则收集所有以PLUGIN_VAR_开头的环境变量
    if not runtime_vars:
        for key, value in os.environ.items():
            if key.startswith('PLUGIN_VAR_') and key != 'PLUGIN_VAR_RUNTIME':
                # 去除PLUGIN_VAR_前缀，转换为小写
                var_name = key[11:].lower()
                
                # 尝试解析JSON值
                try:
                    runtime_vars[var_name] = json.loads(value)
                except json.JSONDecodeError:
                    # 如果不是JSON，直接使用字符串值
                    runtime_vars[var_name] = value
        
        print(f"[DEBUG] 从PLUGIN_VAR_*环境变量收集的运行时变量: {runtime_vars}")
    
    # 获取一个特定的环境变量作为示例
    example_env_var = os.getenv('EXAMPLE_ENV_VAR')
    if example_env_var:
        runtime_vars['example_env_var'] = example_env_var
        print(f"[DEBUG] 获取到环境变量 EXAMPLE_ENV_VAR: {example_env_var}")
    else:
        print("[DEBUG] 环境变量 EXAMPLE_ENV_VAR 不存在")
    
    # 收集其他可能的环境变量
    common_env_vars = [
        'WORKSPACE', 'BUILD_ID', 'PIPELINE_ID', 'PROJECT_ID',
        'GIT_COMMIT', 'GIT_BRANCH', 'GIT_URL',
        'BUILD_NUMBER', 'BUILD_URL', 'JOB_NAME'
    ]
    
    env_vars = {}
    for var in common_env_vars:
        value = os.getenv(var)
        if value is not None:
            env_vars[var.lower()] = value
    
    # 如果有环境变量，添加到运行时变量中
    if env_vars:
        runtime_vars['environment'] = env_vars
    
    print(f"[DEBUG] 最终运行时变量: {runtime_vars}")
    return runtime_vars


def merge_config_and_runtime(config: Dict[str, Any], runtime_vars: Dict[str, Any]) -> Dict[str, Any]:
    """合并配置和运行时变量"""
    merged = config.copy()
    
    # 添加运行时变量到配置中
    if runtime_vars:
        merged['runtime'] = runtime_vars
    
    # 将合并后的配置设置为环境变量，供子进程使用
    merged_json = json.dumps(merged, ensure_ascii=False)
    merged_b64 = base64.b64encode(merged_json.encode('utf-8')).decode('utf-8')
    os.environ['MERGED_CONFIG_BASE64'] = merged_b64
    
    print(f"[DEBUG] 合并后的配置: {merged}")
    return merged


def generate_output(config: Dict[str, Any]) -> str:
    """根据配置生成输出内容"""
    output_lines = []
    output_lines.append("=== Test Plugin 1 输出 ===")
    output_lines.append("")
    
    # 文本字段输出
    if 'text_field' in config:
        output_lines.append("[文本字段]")
        output_lines.append(f"文本内容: {config['text_field']}")
        output_lines.append("")
    
    # 数字字段输出
    if 'number_field' in config:
        output_lines.append("[数字字段]")
        output_lines.append(f"数字值: {config['number_field']}")
        output_lines.append(f"数字乘以2: {config['number_field'] * 2}")
        output_lines.append("")
    
    # 布尔字段输出
    if 'boolean_field' in config:
        output_lines.append("[布尔字段]")
        output_lines.append(f"布尔值: {config['boolean_field']}")
        output_lines.append(f"布尔值取反: {not config['boolean_field']}")
        output_lines.append("")
    
    # 选择字段输出
    if 'select_field' in config:
        output_lines.append("[选择字段]")
        output_lines.append(f"选择的选项: {config['select_field']}")
        output_lines.append("")
    
    # 多行文本字段输出
    if 'textarea_field' in config:
        output_lines.append("[多行文本字段]")
        output_lines.append("多行文本内容:")
        for line in config['textarea_field'].split('\n'):
            output_lines.append(f"  {line}")
        output_lines.append("")
    
    # 数组字段输出
    if 'array_field' in config:
        output_lines.append("[数组字段]")
        output_lines.append(f"数组内容: {config['array_field']}")
        output_lines.append("数组元素:")
        for i, item in enumerate(config['array_field'], 1):
            output_lines.append(f"  {i}. {item}")
        output_lines.append("")
    
    # 对象字段输出
    if 'object_field' in config:
        output_lines.append("[对象字段]")
        output_lines.append(f"对象内容: {config['object_field']}")
        output_lines.append("对象键值对:")
        for key, value in config['object_field'].items():
            output_lines.append(f"  {key}: {value}")
        output_lines.append("")
    
    # JSON字段输出
    if 'json_field' in config:
        output_lines.append("[JSON字段]")
        output_lines.append(f"JSON内容: {config['json_field']}")
        output_lines.append("格式化的JSON:")
        output_lines.append(json.dumps(config['json_field'], indent=2, ensure_ascii=False))
        output_lines.append("")
    
    # 脚本字段输出
    if 'script' in config:
        output_lines.append("[脚本字段]")
        output_lines.append("脚本内容:")
        for i, line in enumerate(config['script'], 1):
            output_lines.append(f"  {i}: {line}")
        output_lines.append("")
    
    # 运行时变量输出
    if 'runtime' in config:
        output_lines.append("[运行时变量]")
        runtime_vars = config['runtime']
        
        # 输出环境变量信息
        if 'environment' in runtime_vars:
            output_lines.append("环境变量:")
            env_vars = runtime_vars['environment']
            for key, value in env_vars.items():
                output_lines.append(f"  {key}: {value}")
            output_lines.append("")
        
        # 输出其他运行时变量
        other_vars = {k: v for k, v in runtime_vars.items() if k != 'environment'}
        if other_vars:
            output_lines.append("其他运行时变量:")
            for key, value in other_vars.items():
                if isinstance(value, (dict, list)):
                    # 如果是复杂类型，格式化为JSON
                    output_lines.append(f"  {key}:")
                    formatted_json = json.dumps(value, indent=4, ensure_ascii=False)
                    for line in formatted_json.split('\n'):
                        output_lines.append(f"    {line}")
                else:
                    output_lines.append(f"  {key}: {value}")
            output_lines.append("")
    
    return '\n'.join(output_lines)


def main():
    """插件主入口函数"""
    print("我是test1-plugin1插件")
    try:
        print("[INFO] Test Plugin 1 开始执行...")
        
        # 加载配置
        config = load_config_from_base64()
        
        # 加载运行时变量
        runtime_vars = load_runtime_variables()
        
        # 合并配置和运行时变量
        merged_config = merge_config_and_runtime(config, runtime_vars)
        
        print(f"[INFO] 加载配置: {json.dumps(merged_config, indent=2, ensure_ascii=False)}")
        
        # 生成输出
        output = generate_output(merged_config)
        
        print("[INFO] 插件执行结果:")
        print("=" * 50)
        print(output)
        print("=" * 50)
        
        print("[INFO] Test Plugin 1 执行完成")
        return 0
        
    except Exception as e:
        print(f"[ERROR] 插件执行失败: {str(e)}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())