#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio.selector_events
import time
import asyncio
from log import log as logger

from config import REGION_LIST
from network import Network
from update import Update


class ContinuousUserCacheUpdater:
    def __init__(self):
        self.stop_event = asyncio.Event()  # 停止信号

    async def update_user(self):
        start_time = int(time.time())
        # 更新用户
        limit = 1000
        request_result = await Network.get_cache_users()
        if request_result['code'] != 1000:
            logger.error(f"获取MaxUserID时发生错误，Error: {request_result.get('message')}")
        else:
            max_id = request_result['data']['max_id']
            max_offset = (int(max_id / limit) + 1) * limit
            offset = 0
            while offset <= max_offset:
                users_result = await Network.get_cache_users(offset, limit)
                if users_result['code'] == 1000:
                    i = 1
                    for user in users_result['data']:
                        account_id = user['user_basic']['account_id']
                        region_id = user['user_basic']['region_id']
                        a = 0
                        if region_id in REGION_LIST and (offset + i) % 4 == a:
                            logger.info(f'{region_id} - {account_id} | ------------------[ {offset + i} / {max_id} ]')
                            await Update.main(user)
                        i += 1
                else:
                    logger.error(f"获取CacheUsers时发生错误，Error: {users_result.get('message')}")
                offset += limit
        end_time = int(time.time())
        # 避免测试时候的循环bug
        if end_time - start_time <= 4*60*60-10:
            sleep_time = 4*60*60 - (end_time - start_time)
            logger.info(f'更新线程休眠 {round(sleep_time,2)} s')
            await asyncio.sleep(sleep_time)

    async def continuous_update(self):
        # 持续循环更新，直到接收到停止信号
        # 似乎写不写没区别(
        while not self.stop_event.is_set():  
            await self.update_user()

    def stop(self):
        self.stop_event.set()  # 设置停止事件

async def main():
    updater = ContinuousUserCacheUpdater()

    # 创建并启动异步更新任务
    update_task = asyncio.create_task(updater.continuous_update())
    try:
        await update_task
    except asyncio.CancelledError:
        updater.stop()

if __name__ == "__main__":
    logger.info('开始运行UserCache更新进程')
    # 开始不间断更新
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('收到进程关闭信号')
    # 退出并释放资源
    wait_second = 3
    while wait_second > 0:
        logger.info(f'进程将在 {wait_second} s后关闭')
        time.sleep(1)
        wait_second -= 1
    logger.info('UserCache更新进程已停止')