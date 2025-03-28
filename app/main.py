#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import httpx

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core import api_logger
from app.middlewares import RedisConnection, CeleryProducer
from app.response import JSONResponse as API_JSONResponse
from app.core import ServiceStatus, EnvConfig
from app.routers import platform_router, robot_router, app_router


async def schedule():
    while True:
        api_logger.info("API日志数据上传")
        # 这里实现具体任务
        await asyncio.sleep(60)  # 每 60 秒执行一次任务

# 应用程序的生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 从环境中加载配置
    EnvConfig.get_config()
    CeleryProducer.init_celery()
    # 初始化redis并测试redis连接
    await RedisConnection.test_redis()
    task = asyncio.create_task(schedule())  # 启动定时任务

    # 启动 lifespan
    yield

    # 应用关闭时释放连接

    # 应用关闭时释放连接
    await RedisConnection.close_redis()
    task.cancel()  # 关闭 FastAPI 时取消任务

app = FastAPI(lifespan=lifespan)

# 将中间件添加到 FastAPI 应用
# app.add_middleware(RateLimitMiddleware, limit=60, time_window=60)

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

@app.get("/proxy/", summary='proxy', tags=['Default'])
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
    prefix="/api/v1/platform", 
    tags=['Platform Interface']
)

app.include_router(
    robot_router, 
    prefix="/api/v1/robot", 
    tags=['Robot Interface']
)

app.include_router(
    app_router, 
    prefix="/api/v1/webapp", 
    tags=['WebAPP Interface']
)

# 重写shutdown函数，避免某些协程bug
'''
关于此处的问题，可以通过asyncio_atexit注册一个关闭事件解决
具体原因请查看python协程时间循环的原理
'''
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