"""
单元测试 for structured_output_prompt

使用 pytest 进行测试，使用类管理测试用例。
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from pydantic import BaseModel, Field
from structured_output_prompt import generate_structured_prompt


class TestStructuredOutputPrompt:
    """测试 structured_output_prompt 的主要功能"""

    # 定义测试模型
    class SimpleModel(BaseModel):
        name: str = Field(description="名称")
        age: int = Field(description="年龄")

    class NestedModel(BaseModel):
        title: str = Field(description="标题")
        items: list[str] = Field(description="项目列表")

    def test_default_template_zh(self):
        """测试中文默认模板"""
        prompt = generate_structured_prompt(
            self.SimpleModel, language="zh", template="default"
        )
        assert "严格按照下面要求输出" in prompt
        assert '"name": str (名称)' in prompt
        assert '"age": int (年龄)' in prompt

    def test_default_template_en(self):
        """测试英文默认模板"""
        prompt = generate_structured_prompt(
            self.SimpleModel, language="en", template="default"
        )
        assert "Output strictly according to the following requirements" in prompt
        assert '"name": str (名称)' in prompt

    def test_none_template(self):
        """测试无模板选项"""
        prompt = generate_structured_prompt(self.SimpleModel, template=None)
        assert "严格按照下面要求输出" not in prompt
        assert '"name": str (名称)' in prompt

    def test_custom_template(self):
        """测试自定义模板"""
        custom_template = "自定义提示: {model_desc}"
        prompt = generate_structured_prompt(self.SimpleModel, template=custom_template)
        assert "自定义提示:" in prompt
        assert '"name": str (名称)' in prompt

    def test_nested_model(self):
        """测试嵌套模型"""
        prompt = generate_structured_prompt(
            self.NestedModel, language="zh", template="default"
        )
        assert '"title": str (标题)' in prompt
        assert '"items": List[str] (项目列表)' in prompt

    def test_invalid_language(self):
        """测试无效语言"""
        with pytest.raises(ValueError, match="默认模版不支持此语言"):
            generate_structured_prompt(
                self.SimpleModel, language="invalid", template="default"
            )

    def test_supported_languages(self):
        """测试所有支持的语言"""
        languages = ["zh", "en", "ja", "de", "fr", "es", "pt", "ru", "ko"]
        for lang in languages:
            prompt = generate_structured_prompt(
                self.SimpleModel, language=lang, template="default"
            )
            assert isinstance(prompt, str)
            assert len(prompt) > 0
