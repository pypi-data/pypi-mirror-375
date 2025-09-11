from typing import Callable

from ausikor_common.app.http.http_status_code import HttpStatusCode



success_message: Callable[..., dict] = lambda json=None, array=None, **kwargs: dict(
    code=HttpStatusCode.OK.value,
    success=True,
    message=HttpStatusCode.OK.name,
    **kwargs,
    json=json or {},
    array=array or []
)

exceptional_message: Callable[..., dict] = lambda http_status_code, **kwargs: dict(
    error=f"[{http_status_code.value[0]}] {http_status_code.value[1]}",
    **kwargs,
    code=http_status_code.value[0],
    success=True,
    message=http_status_code.name,
    json={},
    array=[]
)

error_message: Callable[..., dict] = lambda http_status_code, **kwargs: dict(
    error=f"[{http_status_code.value[0]}] {http_status_code.value[1]}",
    **kwargs,
    code=http_status_code.value[0],
    success=False,
    message=http_status_code.name,
    json={},
    array=[]
)

server_error_message: Callable[..., dict] = lambda status_code, message, **kwargs: dict(
    error=f"[{status_code}] 에러 상세 : {message}",
    **kwargs,
    code=status_code,
    success=False,
    message=message,
    json={},
    array=[]
)

url_not_found_message: Callable[..., dict] = lambda **kwargs: dict(
    error=f"[{HttpStatusCode.NOT_FOUND.value}] 요청한 URL 오류.",
    **kwargs,
    code=HttpStatusCode.NOT_FOUND.value,
    success=False,
    message=HttpStatusCode.NOT_FOUND.name,
    json={},
    array=[]
)

method_not_allowed_message: Callable[..., dict] = lambda **kwargs: dict(
    error=f"[{HttpStatusCode.METHOD_NOT_ALLOWED.value}] REST API 요청 방식 오류.",
    **kwargs,
    code=HttpStatusCode.METHOD_NOT_ALLOWED.value,
    success=False,
    message=HttpStatusCode.METHOD_NOT_ALLOWED.name,
    json={},
    array=[]
)

query_string_not_found_message: Callable[..., dict] = lambda **kwargs: dict(
    error=f"[{HttpStatusCode.QUERY_STRING_NOT_FOUND.value[0]}] {HttpStatusCode.QUERY_STRING_NOT_FOUND.value[1]}",
    **kwargs,
    code=HttpStatusCode.QUERY_STRING_NOT_FOUND.value[0],
    success=False,
    message=HttpStatusCode.QUERY_STRING_NOT_FOUND.name,
    json={},
    array=[]
)

request_body_not_found_message: Callable[..., dict] = lambda **kwargs: dict(
    error=f"[{HttpStatusCode.REQUEST_BODY_NOT_FOUND.value[0]}] {HttpStatusCode.REQUEST_BODY_NOT_FOUND.value[1]}",
    **kwargs,
    code=HttpStatusCode.REQUEST_BODY_NOT_FOUND.value[0],
    success=False,
    message=HttpStatusCode.REQUEST_BODY_NOT_FOUND.name,
    json={},
    array=[]
)