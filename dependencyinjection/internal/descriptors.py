#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import typing
import inspect
from .common import LifeTime, IServiceProvider

class Descriptor:
    def __init__(self, service_type: type, lifetime: LifeTime):
        self._service_type = service_type
        self._lifetime = lifetime

    @property
    def service_type(self):
        return self._service_type

    @property
    def lifetime(self):
        return self._lifetime

    def create(self, provider: IServiceProvider, depend_chain) -> object:
        raise NotImplementedError

    def _build_params_map(self, params: list) -> dict:
        table = {}
        for param in params:
            assert isinstance(param, inspect.Parameter)
            if param.kind is param.POSITIONAL_OR_KEYWORD:
                if not isinstance(param.annotation, type):
                    raise TypeError
                if param.annotation is inspect.Parameter.empty:
                    raise TypeError
                table[param.name] = param.annotation
        return table

    def _resolve_params_map(self, params_map: dict, provider: IServiceProvider, depend_chain) -> dict:
        kwargs = {}
        if params_map:
            for k in params_map:
                annotation = params_map[k]
                kwargs[k] = provider._resolve(annotation, depend_chain)
        return kwargs


class CallableDescriptor(Descriptor):
    def __init__(self, service_type: type, func: callable, lifetime: LifeTime):
        super().__init__(service_type, lifetime)
        self._func = func
        signature = inspect.signature(func)
        params = list(signature.parameters.values())
        self._params_map = self._build_params_map(params)

    def create(self, provider: IServiceProvider, depend_chain) -> object:
        kwargs = self._resolve_params_map(self._params_map, provider, depend_chain)
        return self._func(**kwargs)


class TypedDescriptor(Descriptor):
    def __init__(self, service_type: type, impl_type: type, lifetime: LifeTime):
        super().__init__(service_type, lifetime)
        self._impl_type = impl_type
        signature = inspect.signature(impl_type.__init__)
        params = list(signature.parameters.values())
        self._params_map = self._build_params_map(params[1:]) # ignore `self`

    def create(self, provider: IServiceProvider, depend_chain) -> object:
        kwargs = self._resolve_params_map(self._params_map, provider, depend_chain)
        return self._impl_type(**kwargs)


class InstanceDescriptor(Descriptor):
    def __init__(self, service_type: type, instance):
        super().__init__(service_type, LifeTime.singleton)
        self._instance = instance

    def create(self, provider: IServiceProvider, depend_chain: set) -> object:
        return self._instance


class ServiceProviderDescriptor(Descriptor):
    def __init__(self):
        super().__init__(IServiceProvider, LifeTime.scoped)

    def create(self, provider: IServiceProvider, depend_chain: set) -> object:
        return provider
