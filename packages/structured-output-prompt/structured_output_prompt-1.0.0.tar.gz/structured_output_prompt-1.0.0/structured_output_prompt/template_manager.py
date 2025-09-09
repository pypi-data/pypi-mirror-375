from pydantic import BaseModel
from typing import Type, Optional, Literal
from .model_generator import generate_model_description
from .templates import DEFAULT_TEMPLATES


def generate_structured_prompt(
    model: Type[BaseModel],
    language: Literal["zh", "en", "ja", "de", "fr", "es", "pt", "ru", "ko"] = "zh",
    template: Optional[str] = "default",
) -> str:
    """
    根据指定的语言和模板选项，选择或生成结构化输出提示词。

    此函数用于为 Pydantic 模型生成结构化提示词，支持多语言模板和自定义选项。
    提示词用于指导大语言模型输出严格的 JSON 格式内容，避免不支持 JSON Schema 的模型的限制。

    参数:
    - model (Type[BaseModel]): Pydantic 模型类，用于生成字段描述。
    - language (Literal["zh", "en", "ja", "de", "fr", "es", "pt", "ru", "ko"]): 语言选项，支持的语言代码。默认为 'zh'。
    - template (Optional[str]): 'default' 使用默认模板；None 或 "none" 不使用模板；自定义字符串使用自定义模板（需 {model_desc}）。

    返回:
    - str: 生成的结构化提示词字符串。

    异常:
    - ValueError: 如果指定的语言不支持默认模板。

    使用示例:
    >>> from pydantic import BaseModel
    >>> class User(BaseModel):
    ...     name: str
    ...     age: int
    >>> prompt = select_template(User, language="en", template="default")
    >>> print(prompt)  # 输出英文默认模板
    >>> prompt = select_template(User, template="none")
    >>> print(prompt)  # 输出纯模型描述
    >>> prompt = select_template(User, template="自定义提示: {model_desc}")
    >>> print(prompt)  # 输出自定义模板
    """
    model_desc = generate_model_description(model)

    if template == None or template.lower() == "none":
        return model_desc
    elif template == "default":
        if language in DEFAULT_TEMPLATES:
            return DEFAULT_TEMPLATES[language].format(model_desc=model_desc)
        else:
            raise ValueError(f"默认模版不支持此语言 '{language}'")
    else:
        # 自定义模板，替换 {model_desc}
        return template.format(model_desc=model_desc)
