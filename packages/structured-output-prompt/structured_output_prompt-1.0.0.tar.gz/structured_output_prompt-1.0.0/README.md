# structured_output_prompt 🚀

一个 **Python** 库，用于从 **Pydantic 模型** 生成结构化输出提示词（Prompt），特别适用于 **不支持 JSON Schema 的大语言模型**，帮助你获得严格的 JSON 结构结果。  

---

## ✨ 特性

- 🧩 从 Pydantic 模型自动生成字段结构描述
- 🌍 多语言模板支持（zh / en / ja / de / fr / es / pt / ru / ko）
- 🛠️ 支持 `None`（无模板）、默认模板、自定义模板（含 `{model_desc}` 占位符）
- 🪆 支持嵌套模型、可选字段、列表等复杂类型
- 📦 简洁 API：`generate_structured_prompt(model, language, template)`
- 🔧 适合集成到 LLM 推理管线、Agent 工程、工具调用场景

---

## 📦 安装

使用 pip:

```bash
pip install structured-output-prompt
```

---

## ⚡ 快速开始

```python
from pydantic import BaseModel, Field
from structured_output_prompt import generate_structured_prompt

class User(BaseModel):
    name: str = Field(description="用户的全名 / The user's full name")
    age: int = Field(description="用户的年龄 / The user's age")
    email: str = Field(description="电子邮件地址 / Email address")

prompt = generate_structured_prompt(User, language="zh", template="default")
print(prompt)
```

生成的 Prompt（示例）：

```text
严格按照下面要求输出：
你必须返回实际的完整内容作为最终答案，而不是摘要。
仅输出一个 JSON 对象；不要输出任何解释、前后缀、空行或 Markdown 代码块。
确保你的最终答案只包含以下格式的内容：{
  "name": str (用户的全名 / The user's full name),
  "age": int (用户的年龄 / The user's age),
  "email": str (电子邮件地址 / Email address)
}
```

---

## 🛠️ 自定义模板与不使用模板

```python
custom = "请严格输出以下JSON结构（不要多余解释）：{model_desc}"
prompt = generate_structured_prompt(User, template=custom, language="zh")
print(prompt)
```

输出：

```text
请严格输出以下JSON结构（不要多余解释）：
{
  "name": str (用户的全名 / The user's full name),
  "age": int (用户的年龄 / The user's age),
  "email": str (电子邮件地址 / Email address)
}
```

不使用模板（只返回结构描述）：

```python
print(generate_structured_prompt(User, template=None))
```

输出：

```text
{
  "name": str (用户的全名 / The user's full name),
  "age": int (用户的年龄 / The user's age),
  "email": str (电子邮件地址 / Email address)
}
```

---

## 🌍 多语言

支持语言代码：

- zh - 中文
- en - English
- ja - 日本語
- de - Deutsch
- fr - Français
- es - Español
- pt - Português
- ru - Русский
- ko - 한국어

> **提示**：中文模板为基础，其他语言模板通过大模型翻译生成，以确保一致性和准确性。

切换语言：

```python
generate_structured_prompt(User, language="en")
```

输出结果：

```text
Output strictly according to the following requirements:
You must return the actual complete content as the final answer, not a summary.
Output only one JSON object; do not output any explanations, prefixes, suffixes, blank lines, or Markdown code blocks.
Ensure your final answer contains only the following format: {
  "name": str (用户的全名 / The user's full name),
  "age": int (用户的年龄 / The user's age),
  "email": str (电子邮件地址 / Email address)
}
```

---

## 📚 API 说明 | API Reference

```python
generate_structured_prompt(model, language="zh", template="default")
```

参数:

- model: Pydantic BaseModel 子类
- language: 语言代码（见支持列表）
- template:
  - "default": 使用内置模板
  - None: 仅输出模型结构
  - 自定义字符串: 必须包含 `{model_desc}`

返回:

- 字符串形式的 Prompt

抛出:

- ValueError: 不支持的语言或模板格式异常

---

## 🧪 示例

查看 `example/` 目录：

- `basic_example.py` 基本用法  
- `multilingual_example.py` 多语言演示  
- `custom_template_example.py` 自定义模板  
- `nested_model_example.py` 嵌套模型  

---

## 📄 许可证

MIT License. 详见 `LICENSE`。

---

## ⭐ 支持

如果这个项目对你有帮助，请点亮 Star！⭐

---
