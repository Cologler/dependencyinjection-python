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
from .param_type_resolver import ParameterTypeResolver
from .errors import ParameterTypeResolveError

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


class CallableDescriptor(Descriptor):
    def __init__(self, service_type: type, func: callable, lifetime: LifeTime):
        super().__init__(service_type, lifetime)
        self._func = func
        self._params_type_map = None

    def _build_params_table(self, provider: IServiceProvider) -> dict:
        if self._params_type_map is not None:
            return

        def new_table():
            table = {}
            signature = inspect.signature(self._func)
            params = list(signature.parameters.values())
            params = [p for p in params if p.kind is p.POSITIONAL_OR_KEYWORD]
            if params:
                type_resolver: ParameterTypeResolver = provider.get(ParameterTypeResolver)
                for param in params:
                    table[param.name] = type_resolver.resolve(param)
            return table

        try:
            self._params_type_map = new_table()
        except ParameterTypeResolveError as err:
            if isinstance(self._func, type):
                msg = 'error on creating type {}: {}'.format(self._func, err)
            else:
                msg = 'error on invoke facrory {}: {}'.format(self._func, err)
            raise ParameterTypeResolveError(msg)

    def _resolve_args(self, provider: IServiceProvider, depend_chain) -> dict:
        kwargs = {}
        if self._params_type_map:
            for k in self._params_type_map:
                t = self._params_type_map[k]
                kwargs[k] = provider._resolve(t, depend_chain)
        return kwargs

    def create(self, provider: IServiceProvider, depend_chain) -> object:
        self._build_params_table(provider)
        kwargs = self._resolve_args(provider, depend_chain)
        return self._func(**kwargs)


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


class MapDescriptor(Descriptor):
    def __init__(self, service_type: type, target_service_type: type):
        super().__init__(service_type, LifeTime.transient)
        self._target = target_service_type

    def create(self, provider: IServiceProvider, depend_chain: set) -> object:
        return provider.get(self._target)
