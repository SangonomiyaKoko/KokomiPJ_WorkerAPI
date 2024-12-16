#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import httpx

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core import api_logger
from app.middlewares import RateLimitMiddleware
from app.response import JSONResponse as API_JSONResponse
from app.core import ServiceStatus, EnvConfig
from app.routers import platform_router, robot_router

# 应用程序的生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 从环境中加载配置
    EnvConfig.get_config()

    # 启动 lifespan
    yield

    # 应用关闭时释放连接

app = FastAPI(lifespan=lifespan)

# 将中间件添加到 FastAPI 应用
app.add_middleware(RateLimitMiddleware, limit=60, time_window=60)

@app.get("/", summary='Root', tags=['Default'])
async def root():
    """Root router

    Args:
    - None

    Returns:
    - dict

    """
    return {'status':'ok','messgae':'Hello! Welcome to Kokomi Interface.'}

@app.get("/ping/", summary="Ping", tags=['Default'])
async def ping():
    if not ServiceStatus.is_service_available():
        return API_JSONResponse.API_8000_ServiceUnavailable
    return API_JSONResponse.API_1000_Success

@app.get("/proxy", summary='proxy', tags=['Default'])
async def proxy(
    url: str
):
    '''
    接口请求代理
    '''
    if 'api' in url:
        data = None
        status_code = None
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36'
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                timeout=20,
                headers=headers
            )
            data=response.json()
            status_code=response.status_code
        return JSONResponse(
            content=data, 
            status_code=status_code
        )
    else:
        return JSONResponse(
            content={}, 
            status_code=404
        )

app.include_router(
    platform_router, 
    prefix="/p", 
    tags=['Platform Interface']
)

app.include_router(
    robot_router, 
    prefix="/r", 
    tags=['Robot Interface']
)

# 重写shutdown函数，避免某些协程bug
async def _shutdown(self, any = None):
    await origin_shutdown(self)
    wait_second = 3
    while wait_second > 0:
        api_logger.info(f'App will close after {wait_second} seconds')
        await asyncio.sleep(1)
        wait_second -= 1
    api_logger.info('App has been closed')

origin_shutdown = asyncio.BaseEventLoop.shutdown_default_executor
asyncio.BaseEventLoop.shutdown_default_executor = _shutdown  