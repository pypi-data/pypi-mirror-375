from pydantic import BaseModel
from typing import Type, Union, get_args, get_origin


def generate_model_description(model: Type[BaseModel]) -> str:
    """
    生成Pydantic模型字段及其类型的字符串描述。

    此函数接收一个Pydantic模型类，返回描述该模型字段及其相应类型的字符串。
    描述包括处理复杂类型如`Optional`、`List`和`Dict`，以及嵌套的Pydantic模型。
    """

    def describe_field(field_type):
        origin = get_origin(field_type)
        args = get_args(field_type)

        if origin is Union or (origin is None and len(args) > 0):
            # 处理Union和新的'|'语法
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                return f"Optional[{describe_field(non_none_args[0])}]"
            else:
                return f"Optional[Union[{', '.join(describe_field(arg) for arg in non_none_args)}]]"
        elif origin is list:
            return f"List[{describe_field(args[0])}]"
        elif origin is dict:
            key_type = describe_field(args[0])
            value_type = describe_field(args[1])
            return f"Dict[{key_type}, {value_type}]"
        elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
            return generate_model_description(field_type)
        elif hasattr(field_type, "__name__"):
            return field_type.__name__
        else:
            return str(field_type)

    fields = model.model_fields
    field_descriptions = []
    for name, field in fields.items():
        desc = describe_field(field.annotation)
        if field.description:
            desc += f" ({field.description})"
        field_descriptions.append(f'"{name}": {desc}')
    return "{\n  " + ",\n  ".join(field_descriptions) + "\n}"
