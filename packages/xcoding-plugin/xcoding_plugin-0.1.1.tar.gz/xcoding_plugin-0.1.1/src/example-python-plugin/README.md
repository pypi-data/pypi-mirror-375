# Python示例插件

这是一个支持所有动态表单类型的Python插件示例，用于演示XCoding平台的Python插件系统如何处理各种类型的配置参数。

## 功能描述

该插件接收用户配置的各种类型参数，并根据配置生成结构化的输出：

- **文本字段**: 单行文本输入
- **数字字段**: 数值输入，支持范围验证
- **布尔字段**: 是/否选择
- **选择字段**: 下拉选择框
- **多行文本字段**: 多行文本输入
- **数组字段**: 支持多个值的数组
- **对象字段**: 键值对配置
- **JSON字段**: 复杂的JSON结构配置

## 配置参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|---------|
| text_field | text | 是 | "Hello from Python Plugin!" | 文本输入内容 |
| number_field | number | 是 | 5 | 数字值，范围1-100 |
| boolean_field | boolean | 否 | true | 布尔值选择 |
| select_field | select | 是 | "option2" | 下拉选择：选项1/选项2/选项3 |
| textarea_field | textarea | 否 | 多行默认内容 | 多行文本输入 |
| array_field | array | 否 | ["item1", "item2", "item3"] | 数组配置 |
| object_field | object | 否 | {"key1": "value1", "key2": "value2"} | 对象配置 |
| json_field | json | 否 | {"name": "test", "value": 123, "enabled": true} | JSON配置 |

## 文件结构

```
example-python-plugin/
├── plugin.yaml          # 插件配置文件，定义UI表单
├── main.py              # 主执行脚本，处理配置和生成输出
├── requirements.txt     # Python依赖文件
└── README.md           # 插件说明文档
```

## 使用方法

1. 将插件打包为ZIP文件
2. 通过XCoding平台的插件管理页面上传
3. 在流水线中配置并使用该插件

## 输出示例

插件执行后会生成包含所有配置字段的结构化输出：

```
=== Python示例插件输出 ===

[文本字段]
文本内容: Hello from Python Plugin!

[数字字段]
数字值: 5
数字乘以2: 10

[布尔字段]
布尔值: True
布尔值取反: False

[选择字段]
选择的选项: option2

[多行文本字段]
多行文本内容:
  这是默认的多行文本内容
  第二行内容
  第三行内容

[数组字段]
数组内容: ['item1', 'item2', 'item3']
数组元素:
  1. item1
  2. item2
  3. item3

[对象字段]
对象内容: {'key1': 'value1', 'key2': 'value2'}
对象键值对:
  key1: value1
  key2: value2

[JSON字段]
JSON内容: {'name': 'test', 'value': 123, 'enabled': True}
格式化的JSON:
{
  "name": "test",
  "value": 123,
  "enabled": true
}
```

## 开发说明

这个插件展示了如何处理所有动态表单类型的Python插件开发：

1. **配置定义**: 在plugin.yaml中定义各种类型的表单字段
2. **配置读取**: 从环境变量读取用户配置，处理各种数据类型
3. **业务逻辑**: 根据配置处理数据，展示不同类型字段的处理方式
4. **结果输出**: 生成结构化的输出格式，展示所有配置字段
5. **错误处理**: 捕获异常并返回适当的退出码

### 动态表单类型支持

插件支持以下表单字段类型：

- **text**: 单行文本输入
- **number**: 数字输入，支持验证规则
- **boolean**: 布尔值选择
- **select**: 下拉选择，支持自定义选项
- **textarea**: 多行文本输入
- **array**: 数组类型，支持添加/删除多个值
- **object**: 对象类型，支持键值对配置
- **json**: JSON类型，支持复杂的JSON结构

开发者可以基于这个示例创建支持各种动态表单类型的Python插件，为用户提供丰富的配置选项。