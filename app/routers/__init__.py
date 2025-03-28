from .platform_urls import router as platform_router
from .robot_urls import router as robot_router
from .appweb_urls import router as app_router

__all__ = [
    'platform_router',
    'robot_router',
    'app_router'
]