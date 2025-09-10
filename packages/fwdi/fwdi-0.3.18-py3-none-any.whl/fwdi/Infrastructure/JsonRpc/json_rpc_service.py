from types import FunctionType
from typing import Union
from collections.abc import Coroutine

from fastapi_jsonrpc import Entrypoint, API
from fastapi import FastAPI

class JRPCService():
    def __init__(self, path:str='/api/v1/jsonrpc'):
        self.__api = Entrypoint(path=path)
        self.__app = API()
    
    def add_method(self, 
                   func: Union[FunctionType, Coroutine],
                   name:str,
                   tags:list[str]|None=None):
        if tags:
            self.__api.add_method_route(func=func, name=name, kwargs={'tags': tags})
        else:
            self.__api.add_method_route(func=func, name=name)
    
    def mount_to_asgi(self, fast_api:FastAPI, path:str='rpc'):
        self.__app.bind_entrypoint(self.__api)
        fast_api.mount(path, self.__app)