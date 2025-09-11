import json
import logging
from datetime import datetime

from fastapi import Response, Request
from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from starlette.types import Message

from ausikor_common.app.http.http_status_code import HttpStatusCode
from ausikor_common.app.response.response_state import (
    url_not_found,
    method_not_allowed,
    server_error,
)




logger = logging.getLogger("main")
logging.basicConfig(level=logging.DEBUG, encoding='utf-8')
steam_handler = logging.FileHandler(filename='info.log', mode='w', encoding='utf-8')
logger.addHandler(steam_handler)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()
        req_client = request.client
        req_method = request.method
        req_url = request.url
        req_headers = request.headers
        req_body = await request.body()
        await set_body(request, req_body)
        response = await call_next(request)
        res_status_code = response.status_code
        res_media_type = response.media_type
        res_headers = response.headers
        if isinstance(response, StreamingResponse):
            res_body = b''
            async for chunk in response.body_iterator:
                res_body += chunk
        else:
            res_body = response.body
        res_body = await middleware_exception_handler(
            req_method=req_method,
            req_url=req_url,
            res_body=res_body,
            res_status_code=res_status_code,
            response=response
        ) if res_status_code != HttpStatusCode.OK.value else res_body
        task = BackgroundTask(func=log_info,
                              req_client=req_client,
                              req_method=req_method,
                              req_url=req_url,
                              req_headers=req_headers,
                              req_body=req_body,
                              res_status_code=res_status_code,
                              res_media_type=res_media_type,
                              res_headers=res_headers,
                              res_body=res_body)
        # send_message_to_slack(req_client, req_method, req_url, req_headers, req_body,
        #                       res_status_code, res_media_type, res_headers, res_body)
        end_time = datetime.now()
        measure_duration(start_time=start_time, end_time=end_time)
        return Response(status_code=HttpStatusCode.OK.value,
                        media_type=res_media_type,
                        headers=dict(res_headers),
                        content=res_body,
                        background=task)


# def send_message_to_slack(req_client, req_method, req_url, req_headers, req_body,
#                           res_status_code, res_media_type, res_headers, res_body):
#     try:
#         user_agent = req_headers.get("user-agent")  # 슬랙 메세지 요청 후 응답 차단용
#         json_res = json.loads(res_body)
#         if (json_res.get('code') == HttpStatusCode.INTERNAL_SERVER_ERROR.value
#                 and user_agent != 'Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)'):
#             requests.post(
#                 url=SLACK_WEBHOOK_URL,
#                 headers={'content-type': 'application/json'},
#                 json=dict(
#                     text=f"REQUEST TIME >>> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nREQUEST URL >>> {req_url}\nRESPONSE BODY >>> {res_body.decode('utf-8')}"
#             )
#     except json.JSONDecodeError:
#         return


def log_info(req_client, req_method, req_url, req_headers, req_body,
             res_status_code, res_media_type, res_headers, res_body):
    try:
        decoded_res_body = res_body.decode('utf-8')
        if decoded_res_body.strip():
            res_body_to_print = json.loads(decoded_res_body)
            array = res_body_to_print.get('array')
            new_array = []
            if array:
                new_array.append(array[0])
            res_body_to_print['array'] = new_array
        else:
            res_body_to_print = decoded_res_body
    except json.JSONDecodeError:
        res_body_to_print = res_body.decode('utf-8')

    logging.info("-" * 100)
    logging.info(f">>> 요청시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f">>> 요청주소: {req_client}")
    logging.info(f">>> 요청방식: {req_method}")
    logging.info(f">>> 요청URL: {req_url}")
    logging.info(f">>> 요청헤더: {req_headers}")
    logging.info(
        f">>> 요청바디**: {req_body.decode('utf-8') if req_headers.get('Content-Type') == 'application/json' else req_body}"
    )
    logging.info(f">>> 응답상태코드: {res_status_code}")
    logging.info(f">>> 미디어타입: {res_media_type}")
    logging.info(f">>> 응답헤더: {res_headers}")
    logging.info(f">>> 응답바디** : {res_body_to_print}")
    logging.info("-" * 100)


async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {'type': 'http.request', 'body': body}

    request._receive = receive


async def middleware_exception_handler(req_method, req_url, res_body, res_status_code, response):
    if res_status_code == HttpStatusCode.URL_NOT_FOUND.value:
        res_body = json.dumps(
            url_not_found(url=str(req_url)), ensure_ascii=False
        ).encode('utf-8')
        response.headers['Content-Length'] = str(len(res_body))
    elif res_status_code == HttpStatusCode.METHOD_NOT_ALLOWED.value:
        res_body = json.dumps(
            method_not_allowed(method=str(req_method)), ensure_ascii=False
        ).encode('utf-8')
        response.headers['Content-Length'] = str(len(res_body))
    else:
        res_body = json.dumps(
            server_error(status_code=res_status_code,
                                 message=json.loads(res_body.decode('utf-8'))['detail']), ensure_ascii=False
        ).encode('utf-8')
        response.headers['Content-Length'] = str(len(res_body))
    return res_body


async def save_request_body_as_file(request: Request, file_name: str = "req_body"):
    req_body = await request.body()
    decoded_req_body = req_body.decode('utf-8')
    with open(f"./request_body/{file_name}.json", "w") as f:
        f.write(decoded_req_body)