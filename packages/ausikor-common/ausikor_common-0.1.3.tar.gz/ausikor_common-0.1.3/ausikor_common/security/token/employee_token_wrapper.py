import inspect
from functools import wraps
from typing import Callable
from typing import Type

import jwt
from fastapi import Form
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic.fields import ModelField
from sqlalchemy.exc import OperationalError
from starlette.responses import JSONResponse

from app.utils.util.config import ACCESS_TOKEN_ALGORITHM, ACCESS_TOKEN_SECRET_KEY
from app.utils.util.http_status_code import HttpStatusCode
from app.utils.util.response import exceptional_message, server_error_message

def employee_token_wrapper(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not kwargs.get("access_token"):
            return exceptional_message(http_status_code=HttpStatusCode.NO_ACCESS_TOKEN)
        try:
            access_token = kwargs.get("access_token")
            payload = jwt.decode(jwt=access_token, key=ACCESS_TOKEN_SECRET_KEY, algorithms=ACCESS_TOKEN_ALGORITHM)
            employee_id = payload.get('sub')
            return func(*args, **kwargs, employee_id=employee_id)  # employee_id
        except jwt.ExpiredSignatureError:
            return exceptional_message(http_status_code=HttpStatusCode.EXPIRED_ACCESS_TOKEN)
        except jwt.exceptions.DecodeError:
            return exceptional_message(http_status_code=HttpStatusCode.WRONG_ACCESS_TOKEN)

    return wrapper