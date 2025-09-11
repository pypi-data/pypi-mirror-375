# Test Plugin 1

Test Plugin 1 是一个支持 PLUGIN_CONFIG_BASE64 环境变量的 Python 插件示例，用于 XCoding CI/CD 系统。

## 功能特点

- 支持 PLUGIN_CONFIG_BASE64 环境变量
- 处理各种类型的配置参数：文本、数字、布尔、选择、多行文本、数组、对象、JSON 和脚本
- 生成格式化的输出
- 提供详细的调试信息

## 文件结构

```
test-plugin1/
├── main.py         # 主脚本文件
├── plugin.json     # 插件配置文件
├── plugin.yaml     # 插件YAML配置文件
├── requirements.txt # Python依赖文件
└── README.md       # 说明文档
```

## 配置参数

### 文本字段 (text_field)
- 类型：文本
- 描述：输入文本内容
- 默认值："Hello from Python Plugin!"

### 数字字段 (number_field)
- 类型：数字
- 描述：输入数字
- 默认值：5

### 布尔字段 (boolean_field)
- 类型：布尔
- 描述：选择布尔值
- 默认值：true

### 选择字段 (select_field)
- 类型：选择
- 描述：从下拉列表中选择一个选项
- 选项：["option1", "option2", "option3"]
- 默认值："option2"

### 多行文本字段 (textarea_field)
- 类型：多行文本
- 描述：输入多行文本
- 默认值："这是默认的多行文本内容\n第二行内容\n第三行内容"

### 数组字段 (array_field)
- 类型：数组
- 描述：输入数组
- 默认值：["item1", "item2", "item3"]

### 对象字段 (object_field)
- 类型：对象
- 描述：输入对象
- 默认值：{"key1": "value1", "key2": "value2"}

### JSON字段 (json_field)
- 类型：JSON
- 描述：输入JSON
- 默认值：{"name": "test", "value": 123, "enabled": true}

### 脚本字段 (script)
- 类型：脚本
- 描述：输入脚本
- 默认值：["#!/usr/bin/env python3", "# Python示例脚本", "print(\"Hello, Python!\")", "# 在此处编写您的Python代码"]

## 使用方法

1. 在 XCoding CI/CD 系统中创建一个构建阶段
2. 添加一个步骤，类型为 "test-plugin1"
3. 配置所需的参数
4. 运行构建

## 输出示例

```
=== Test Plugin 1 输出 ===

[文本字段]
文本内容: Hello from Python Plugin!

[数字字段]
数字值: 2
数字乘以2: 4

[布尔字段]
布尔值: true
布尔值取反: false

[选择字段]
选择的选项: option2

[多行文本字段]
多行文本内容:
  多行文本111

[数组字段]
数组内容: []
数组元素:

[对象字段]
对象内容: {'AA': '1111', 'BB': '2222'}
对象键值对:
  AA: 1111
  BB: 2222

[JSON字段]
JSON内容: {'name': 'test', 'value': 12223, 'enabled': True}
格式化的JSON:
{
  "name": "test",
  "value": 12223,
  "enabled": true
}

[脚本字段]
脚本内容:
  1: #!/usr/bin/env python3
  2: # Python示例脚本
  3: print("Hello, Python!")
  4: # 在此处编写您的Python代码

```

## 调试信息

插件会输出详细的调试信息，包括：
- 从 PLUGIN_CONFIG_BASE64 解码的配置
- 解析后的配置
- 加载的配置
- 执行结果

## 错误处理

插件会捕获并报告所有异常，包括：
- PLUGIN_CONFIG_BASE64 环境变量不存在
- Base64 解码失败
- JSON 解析失败
- 其他执行错误

## 依赖

- pyyaml>=6.0
- requests>=2.28.0

## 兼容性

- XCoding CI/CD v1.0.0 及以上版本
- Python 3.10 及以上版本
- Linux, macOS, Windows

## 许可证

MIT

## 作者

XCoding Team

## 主页

https://github.com/xcoding/xcoding