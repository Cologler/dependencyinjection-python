#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from enum import Enum

class LifeTime(Enum):
    singleton = 0
    scoped = 1
    transient = 2


class IServiceProvider:
    def get(self, service_type: type):
        '''
        get service by the type.
        '''
        raise NotImplementedError

    def scope(self):
        '''
        get a scoped `IServiceProvider`.

        usage:
        ``` py
        with ?.scope() as service_provider:
            obj = service_provider.get(?)
        ```
        '''
        raise NotImplementedError


class IValidator:
    def verify(self, service_type: type, obj):
        raise NotImplementedError


class IScopedFactory:
    @property
    def service_provider(self):
        raise NotImplementedError


class ILock:
    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError


class FakeLock(ILock):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
