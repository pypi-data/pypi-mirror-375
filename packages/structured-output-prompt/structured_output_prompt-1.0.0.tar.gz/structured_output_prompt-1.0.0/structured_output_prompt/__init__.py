"""
structured_output_prompt

一个 Python 包，用于从 Pydantic 模型生成结构化输出提示词。

此包提供多语言支持和自定义模板选项，帮助指导大语言模型输出严格的 JSON 格式内容，
尤其适用于不支持 JSON Schema 的模型。

主要功能：
- 生成模型字段描述
- 支持多语言模板（中文、英文、日语等）
- 自定义模板选项

使用示例：
    from pydantic import BaseModel
    from structured_output_prompt import generate_structured_prompt

    class User(BaseModel):
        name: str
        age: int

    prompt = generate_structured_prompt(User, language="en")
    print(prompt)
"""

from .template_manager import generate_structured_prompt

__all__ = ["generate_structured_prompt"]
