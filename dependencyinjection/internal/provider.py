#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import contextlib
import typing
from .common import IServiceProvider, IValidator, IScopedFactory, LifeTime, FakeLock, ILock
from .descriptors import Descriptor
from .servicesmap import ServicesMap
from .checker import CycleChecker
from .errors import TypeNotFoundError
from .service_resolver import IServiceResolver, ServiceResolver, ListedServiceResolver

INTERNAL_TYPES = set([
    IServiceProvider,
    IValidator,
    ILock,
])

class ServiceProvider(IServiceProvider):
    def __init__(self, parent_provider: IServiceProvider=None, service_map: ServicesMap=None):
        self._root_provider = parent_provider._root_provider if parent_provider else self
        self._exit_stack = contextlib.ExitStack()
        self._exit_stack.__enter__()
        # if service_map is None, parent_provider must not None
        self._service_map = service_map or parent_provider._service_map
        self._cache: typing.Dict[type, object] = {} # cached service_type to instance
        self._cache_list: typing.Dict[Descriptor, object] = {} # cached descriptor to instance
        self._service_resolvers: typing.Dict[type, IServiceResolver] = {}

        self._lock = FakeLock()
        if self._root_provider is self:
            self._lock = self.get(ILock)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._exit_stack.__exit__(exc_type, exc_value, traceback)
        self._cache.clear()
        self._cache_list.clear()

    def get(self, service_type: type):
        if not isinstance(service_type, type):
            raise TypeError
        with self._lock:
            if service_type in self._cache:
                return self._cache[service_type]
            service_resolver = self._get_service_resolver(service_type)
            return service_resolver.resolve(self)

    def _get_service_resolver(self, service_type: type) -> IServiceResolver:
        with self._lock:
            resolver = self._service_resolvers.get(service_type)
            if resolver is None:
                if self is not self._root_provider:
                    resolver = self._root_provider._get_service_resolver(service_type)
                elif getattr(service_type, '__origin__', None) is typing.List and isinstance(service_type.__args__, tuple):
                    inner_type = service_type.__args__[0]
                    resolver = ListedServiceResolver(inner_type)
                else:
                    resolver = ServiceResolver(service_type)
                self._service_resolvers[service_type] = resolver
            return resolver

    def _resolve(self, service_type: type, depend_chain: CycleChecker, require: bool=True):
        if service_type in self._cache:
            return self._cache[service_type]
        depend_chain.add_or_raise(service_type)
        try:
            descriptor = self._service_map.get(service_type)
            if descriptor is None:
                if require:
                    raise TypeNotFoundError('type {} cannot resolve from container.'.format(service_type))
            else:
                obj = self._resolve_by_descriptor(descriptor, depend_chain)
                if descriptor.lifetime != LifeTime.transient: # cache other value
                    self._cache[service_type] = obj
                return obj
        finally:
            depend_chain.remove_last()

    def _resolve_by_descriptor(self, descriptor: Descriptor, depend_chain: CycleChecker):
        provider = self if descriptor.lifetime != LifeTime.singleton else self._root_provider
        with self._lock:
            if descriptor in self._cache_list:
                return self._cache_list[descriptor]
            if provider is self:
                obj = descriptor.create(provider, depend_chain)
                if descriptor.service_type not in INTERNAL_TYPES:
                    self.get(IValidator).verify(descriptor.service_type, obj)
                    if obj is not None and hasattr(obj, '__enter__') and hasattr(obj, '__exit__'):
                        self._exit_stack.enter_context(obj)
            else:
                obj = provider._resolve_by_descriptor(descriptor, depend_chain)
            if descriptor.lifetime != LifeTime.transient: # cache other value
                self._cache_list[descriptor] = obj
            return obj

    def scope(self):
        return self.get(IScopedFactory).service_provider
