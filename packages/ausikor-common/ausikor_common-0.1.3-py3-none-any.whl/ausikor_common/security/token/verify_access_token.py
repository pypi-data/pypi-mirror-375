import inspect
from functools import wraps
from typing import Callable, Type

import jwt
from fastapi import Form
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic.fields import FieldInfo  # ✅ 올바른 import
from sqlalchemy.exc import OperationalError
from starlette.responses import JSONResponse

from app.foundation.core.security import token_singleton
from app.foundation.design.structural.facade.response_facade import ResponseFacade
from app.foundation.enums.http_status_code import HttpStatusCode


def verify_access_token(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not kwargs.get("access_token"):
            return ResponseFacade.exceptional(http_status_code=HttpStatusCode.NO_ACCESS_TOKEN)
        try:
            access_token = kwargs.get("access_token")
            payload = jwt.decode(jwt=access_token, 
                                 key=token_singleton.access_token_secret_key, 
                                 algorithms=token_singleton.access_token_algorithm)
            user_id = payload.get('sub')
            return func(*args, **kwargs, user_id=user_id)  # user_id
        except jwt.ExpiredSignatureError:
            return ResponseFacade.exceptional(http_status_code=HttpStatusCode.EXPIRED_ACCESS_TOKEN)
        except jwt.exceptions.DecodeError:
            return ResponseFacade.exceptional(http_status_code=HttpStatusCode.WRONG_ACCESS_TOKEN)

    return wrapper
