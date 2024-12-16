import uuid
import traceback

import httpx

from .error_log import write_error_info
from app.response import JSONResponse

class ExceptionType:
    program = 'program'
    network = 'Network'

class NerworkExceptionName:
    connect_timeout = 'ConnectTimeout'
    read_timeout = 'ReadTimeout'
    request_timeout = 'RequestTimeout'
    network_error = 'NetworkError'
    connect_error = 'ConnectError'
    read_error = 'ReadError'

def generate_error_id():
    return str(uuid.uuid4())

class ExceptionLogger:
    @staticmethod
    def handle_program_exception_async(func):
        "负责异步程序异常信息的捕获"
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_program_exception_sync(func):
        "负责同步程序异常信息的捕获"
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper

    @staticmethod
    def handle_network_exception_async(func):
        "负责异步网络请求 httpx 的异常捕获"
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except httpx.ConnectTimeout:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.connect_timeout,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2001,'NetworkError',error_id)
            except httpx.ReadTimeout:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.read_timeout,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2002,'NetworkError',error_id)
            except httpx.TimeoutException:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.request_timeout,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2003,'NetworkError',error_id)
            except httpx.ConnectError:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.connect_error,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2004,'NetworkError',error_id)
            except httpx.ReadError:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.read_error,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2005,'NetworkError',error_id)
            except httpx.HTTPStatusError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.network_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'StatusCode: {e.response.status_code}'
                )
                return JSONResponse.get_error_response(2000,'NetworkError',error_id)
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper