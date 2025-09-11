import json
import logging

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


class ResponseFactory:
    @staticmethod
    def create_response(response):
        """서비스 응답에 대한 일관된 응답 생성"""
        logger = logging.getLogger(__name__)
        try:
            if response.status_code == 200:
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code
                )
            else:
                return JSONResponse(
                    content={"detail": f"Service error: {response.text}"},
                    status_code=response.status_code
                )
        except json.JSONDecodeError:
            return JSONResponse(
                content={"detail": "⚠️Invalid JSON response from service"},
                status_code=500
            )
        except Exception as e:
            logger.error(f"Error creating response: {str(e)}")
            return JSONResponse(
                content={"detail": f"Gateway error: {str(e)}"},
                status_code=500
            )
