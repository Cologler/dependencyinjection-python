#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import typing
from .descriptors import Descriptor

class ServicesMap:
    def __init__(self, services: typing.List[Descriptor]):
        self._type_map: typing.Dict[type, typing.List[Descriptor]] = {}
        for service in services:
            ls = self._type_map.get(service.service_type)
            if ls is None:
                ls = []
                self._type_map[service.service_type] = ls
            ls.append(service)

    def get(self, service_type: type) -> Descriptor:
        ls = self._type_map.get(service_type)
        if ls:
            return ls[-1] # has one item at least.

    def getall(self, service_type: type) -> typing.List[Descriptor]:
        return self._type_map.get(service_type)
