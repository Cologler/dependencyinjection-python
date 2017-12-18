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

    def _build_params_type_map(self, params: list, provider: IServiceProvider) -> dict:
        table = {}
        params = [p for p in params if p.kind is p.POSITIONAL_OR_KEYWORD]
        if params:
            type_resolver: ParameterTypeResolver = provider.get(ParameterTypeResolver)
            for param in params:
                table[param.name] = type_resolver.resolve(param)
        return table

    def _resolve_params_map(self, params_type_map: dict, provider: IServiceProvider, depend_chain) -> dict:
        kwargs = {}
        if params_type_map:
            for k in params_type_map:
                t = params_type_map[k]
                kwargs[k] = provider._resolve(t, depend_chain)
        return kwargs


class CallableDescriptor(Descriptor):
    def __init__(self, service_type: type, func: callable, lifetime: LifeTime):
        super().__init__(service_type, lifetime)
        self._func = func
        signature = inspect.signature(func)
        self._params = list(signature.parameters.values())
        self._params_type_map = None

    def create(self, provider: IServiceProvider, depend_chain) -> object:
        if self._params_type_map is None:
            self._params_type_map = self._build_params_type_map(self._params, provider)
        kwargs = self._resolve_params_map(self._params_type_map, provider, depend_chain)
        return self._func(**kwargs)


class TypedDescriptor(Descriptor):
    def __init__(self, service_type: type, impl_type: type, lifetime: LifeTime):
        super().__init__(service_type, lifetime)
        self._impl_type = impl_type
        signature = inspect.signature(impl_type.__init__)
        self._params = list(signature.parameters.values())[1:] # ignore `self`
        self._params_type_map = None

    def create(self, provider: IServiceProvider, depend_chain) -> object:
        if self._params_type_map is None:
            try:
                self._params_type_map = self._build_params_type_map(self._params, provider)
            except ParameterTypeResolveError as err:
                msg = 'error on creating type {}: {}'.format(self._impl_type, err)
                raise ParameterTypeResolveError(msg)
        kwargs = self._resolve_params_map(self._params_type_map, provider, depend_chain)
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


class MapDescriptor(Descriptor):
    def __init__(self, service_type: type, target_service_type: type):
        super().__init__(service_type, LifeTime.transient)
        self._target = target_service_type

    def create(self, provider: IServiceProvider, depend_chain: set) -> object:
        return provider.get(self._target)
