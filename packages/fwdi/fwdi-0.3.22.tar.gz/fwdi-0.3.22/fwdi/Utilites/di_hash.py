#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

from time import perf_counter_ns
from typing import NamedTuple

from ..Application.DependencyInjection.resolve_provider import *


class RecordInstance(NamedTuple):
    instance: TService
    lifetime: ServiceLifetime

class DiHashFunction():
    def __init__(self):
        self.__hash:dict[str, RecordInstance] = {}

    def get_or_create(self, base_type)->TService|None:
        if base_type.__name__ not in self.__hash:
            inst, life = ResolveProviderFWDI.get_service(base_type)
            self.__hash[base_type.__name__] = RecordInstance(inst, life)
            
            return inst
        else:
            try:
                new_instance:RecordInstance = self.__hash[base_type.__name__]
                if new_instance.lifetime == ServiceLifetime.Singleton:
                    return new_instance.instance
                else:
                    return type(new_instance.instance)()
                
            except Exception as ex:
                print(f"ERROR:{ex}")