from enum import Enum


class HttpStatusCode(Enum):
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    PROCESSING = 102
    EARLY_HINTS = 103
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTI_STATUS = 207
    ALREADY_REPORTED = 208
    IM_USED = 226
    MULTIPLE_CHOICE = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    UNUSED = 306
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    URL_NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    PAYLOAD_TOO_LARGE = 413
    URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    REQUESTED_RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    IM_A_TEAPOT = 418
    MISDIRECTED_REQUEST = 421
    UNPROCESSABLE_ENTITY = 422
    LOCKED = 423
    FAILED_DEPENDENCY = 424
    UPGRADE_REQUIRED = 426
    PRECONDITION_REQUIRED = 428
    TOO_MANY_REQUESTS = 429
    REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    UNAVAILABLE_FOR_LEGAL_REASONS = 451
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    VARIANT_ALSO_NEGOTIATES = 506
    INSUFFICIENT_STORAGE = 507
    LOOP_DETECTED = 508
    NOT_EXTENDED = 510
    NETWORK_AUTHENTICATION_REQUIRED = 511

    WRONG_ID = 20001, f"""ID 값이 틀립니다."""
    WRONG_PASSWORD = 20002, f"""PASSWORD가 틀립니다."""

    WRONG_ACCESS_TOKEN = 20003, f"""ACCESS_TOKEN 값이 틀립니다."""
    WRONG_REFRESH_TOKEN = 20005, "네트워크 신호는 도달했으나, 데이터베이스에 일치하는 REFRESH_TOKEN이 없습니다."
    EXPIRED_ACCESS_TOKEN = 20006, "네트워크 신호는 도달했으나, ACCESS_TOKEN 유효기간이 만료 했습니다."
    EXPIRED_REFRESH_TOKEN = 20007, "네트워크 신호는 도달했으나, REFRESH_TOKEN  유효기간이 만료 했습니다."

    WRONG_PASSWORD_5TIMES = 20008, "PASSWORD 5회 이상 틀렸습니다. 또는 네트워크 신호는 도달했으나, PASSWORD 값이 전송되지 않았습니다."
    ALREADY_EXIST = 20009, "네트워크 신호는 도달했으나, 요청한 데이터가 이미 존재합니다."
    NO_MATCHING_RECORD = 20010, "네트워크 신호는 도달했으나, 요청한 값이 전송되지 않았거나 데이터베이스에 일치하는 값이 없습니다."
    LIMIT_EXCEEDED = 20011, "네트워크 신호는 도달했으나, 제한된 수량을 초과하여 요청을 수행할 수 없습니다."
    UPLOAD_FAILED = 20012, "네트워크 신호는 도달했으나, 업로드할 파일 데이터가 전송되지 않았습니다."
    TOO_LONG_PERIOD = 20013, "검색은 최대 1년 단위로만 가능합니다."

    WRONG_KAKAO_CODE = 20014, "KAKAO 인가코드 값이 전송되지 않았거나 잘못된 값입니다."

    NO_ACCESS_TOKEN = 20003, "네트워크 신호는 도달했으나, ACCESS_TOKEN 값이 전송되지 않았습니다."

    WRONG_FORMAT = 20015, "요청한 데이터의 형식을 확인하세요."

    WRONG_NAVER_CODE = 20016, "KAKAO 인가코드 값이 전송되지 않았거나 잘못된 값입니다."

    INVALID_CAPTCHA = 20016, "CAPTCHA 값이 전송되지 않았거나 잘못된 값입니다."

    INICIS_AUTH_FAILED = 20017, "이니시스 결제승인에 실패했습니다."

    WRONG_PARAM = 20018, "요청한 파라미터의 값이 올바르지 않습니다."

    QUERY_STRING_NOT_FOUND = 40401, "Check key and value of Query Parameters. URL 쿼리 파라미터의 키와 값이 올바른지 확인하세요."
    REQUEST_BODY_NOT_FOUND = 40402, "Check key and value of Request Data. 요청한 JSON 데이터의 키와 값이 올바른지 확인하세요."

    INVALID_REQUEST_BODY = 40001, "Check key and value of Request Data. 요청한 JSON 데이터의 키와 값이 올바른지 확인하세요."


if __name__ == '__main__':
    print(HttpStatusCode.OK)
    print(HttpStatusCode.OK.name)
    print(HttpStatusCode.NOT_FOUND.value)
    print(type(HttpStatusCode.NOT_FOUND))
    print(HttpStatusCode(404))