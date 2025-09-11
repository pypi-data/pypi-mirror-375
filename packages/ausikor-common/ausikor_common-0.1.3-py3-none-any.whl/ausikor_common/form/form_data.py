import inspect
from typing import Type
from fastapi import Form
from pydantic import BaseModel
from pydantic.fields import FieldInfo  # ✅ 올바른 import




# 프론트에서 form 데이터가 올 때 사용
def form_service(cls: Type[BaseModel]):
    new_parameters = []

    for field_name, model_field in cls.model_fields.items():  # ✅ Pydantic v2에서는 `__fields__` 대신 `model_fields`
        model_field: FieldInfo  # ✅ ModelField 대신 FieldInfo 사용

        new_parameters.append(
            inspect.Parameter(
                model_field.alias or field_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=Form(...) if model_field.default is None else Form(model_field.default),
                annotation=model_field.annotation,
            )
        )

    async def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig  # type: ignore
    setattr(cls, 'form_service', as_form_func)
    return cls