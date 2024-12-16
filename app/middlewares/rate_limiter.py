import time

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from .access_manager import IPAccessListManager


# 全局变量存储请求数据
request_counts = {}  # 限流记录：{"ip_address": [timestamp1, timestamp2, ...]}
last_clear_time = 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int, time_window: int):
        """
        初始化限流中间件
        """
        super().__init__(app)
        self.limit = limit
        self.time_window = time_window

    async def dispatch(self, request: Request, call_next):
        """
        限流和记录请求量
        """
        client_ip = request.client.host  # 获取客户端 IP 地址
        # 检查是否在禁止名单
        if IPAccessListManager.is_blacklisted(client_ip):
            raise HTTPException(status_code=403, detail='Forbidden')
        # 白名单IP跳过限速检测
        if not IPAccessListManager.is_whitelisted(client_ip):
            now = time.time()  # 当前时间戳
            # 初始化 IP 的请求记录
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            request_counts[client_ip].append(now)
            # 如果ip数据过多则删除部分不需要的数据
            new_request_counts = []
            if last_clear_time != 0 and now - last_clear_time > 60*60:
                for client_host in request_counts:
                    if request_counts[client_host] == []:
                        continue
                    if now - request_counts[client_host][-1] > 60:
                        continue
                    new_request_counts[client_host] = request_counts[client_host]
            request_counts = new_request_counts
            # 移除时间窗口外的记录
            request_counts[client_ip] = [
                ts for ts in request_counts[client_ip] if now - ts < self.time_window
            ]
            # 判断是否超过请求限制
            if len(request_counts[client_ip]) >= self.limit:
                raise HTTPException(status_code=429, detail="Too Many Requests")
        # TODO: 更新每小时请求统计
        # 调用下一个中间件或路由处理程序
        response = await call_next(request)
        return response


