#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from .checker import CycleChecker

class IServiceResolver:
    def resolve(self, service_provider):
        raise NotImplementedError


class ServiceResolver(IServiceResolver):
    def __init__(self, service_type: type):
        assert service_type is not None
        self._service_type = service_type

    def resolve(self, service_provider):
        return service_provider._resolve(self._service_type, CycleChecker(), False)


class ListedServiceResolver(IServiceResolver):
    def __init__(self, service_type: type):
        assert service_type is not None
        self._service_type = service_type

    def resolve(self, service_provider):
        descriptors = service_provider._service_map.getall(self._service_type)
        ret = []
        if descriptors:
            for d in descriptors:
                ret.append(service_provider._resolve_by_descriptor(d, CycleChecker()))
        return ret
