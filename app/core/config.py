# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings

class LoadConfig(BaseSettings):
    LOG_PATH: str
    MAIN_SERVICE_HOST: str
    MAIN_SERVICE_PASSWORD: str
    
    WG_API_TOKEN: str
    LESTA_API_TOKEN: str

    class Config:
        env_file = ".env"

class EnvConfig:
    __cache = None

    @classmethod
    def get_config(self) -> LoadConfig:
        if self.__cache is None:
            config = LoadConfig()
            self.__cache = config
            return config
        else:
            return self.__cache
