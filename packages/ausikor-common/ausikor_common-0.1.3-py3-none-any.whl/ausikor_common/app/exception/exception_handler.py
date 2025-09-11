from functools import wraps
from sqlite3 import OperationalError
from typing import Callable

try:
    from fastapi.responses import JSONResponse
except Exception:
    try:
        from starlette.responses import JSONResponse
    except Exception:
        class JSONResponse(dict):
            def __init__(self, content=None, status_code: int = 200, media_type: str = None, headers=None, background=None):
                super().__init__(content or {})
                self.status_code = status_code
                self.media_type = media_type
                self.headers = headers or {}
                self.background = background
            def __repr__(self):
                return f"JSONResponse(status_code={self.status_code}, content={dict(self)})"

try:
    from fastapi.encoders import jsonable_encoder
except Exception:
    def jsonable_encoder(obj, *args, **kwargs):
        return obj

from ausikor_common.app.http.http_status_code import HttpStatusCode
from ausikor_common.app.response.response_state import server_error

#### 

# 라우터에서 사용. 에러 발생 시 200 코드로 감싸서 전송, 서버에서 에러 발생 억제.
def exception_wrapper(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, OperationalError) and "Lost connection to MySQL server during query" in str(e):
                return JSONResponse(status_code=HttpStatusCode.OK.value,
                                    content=jsonable_encoder(
                                        server_error(
                                            status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value,
                                            message=str(type(e).__name__),
                                            explanation=f"데이터베이스 연결 대기시간 초과로 인한 일시적 연결 끊김.\n 방금 요청으로 연결 복구 됐습니다.\n 다시 시도해 주세요. {str(e)}",
                                        )
                                    )
                                    )
            return JSONResponse(status_code=HttpStatusCode.OK.value,
                                content=jsonable_encoder(
                                    server_error(
                                        status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value,
                                        message=str(type(e).__name__),
                                        explanation=str(e),
                                    )
                                )
                                )

    return wrapper




