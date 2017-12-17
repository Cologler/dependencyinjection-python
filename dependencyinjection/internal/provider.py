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

class ServiceProvider(IServiceProvider):
    def __init__(self, parent_provider: IServiceProvider=None, service_map: ServicesMap=None):
        self._root_provider = parent_provider._root_provider if parent_provider else self
        self._exit_stack = contextlib.ExitStack()
        self._exit_stack.__enter__()
        # if service_map is None, parent_provider must not None
        self._service_map = service_map or parent_provider._service_map
        self._cache = {}
        self._cache_list = {}
        self._lock = FakeLock()
        if self._root_provider is self:
            self._lock = self.get(ILock)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._exit_stack.__exit__(exc_type, exc_value, traceback)
        self._cache.clear()

    def get(self, service_type: type):
        if not isinstance(service_type, type):
            raise TypeError
        with self._lock:
            if service_type in self._cache:
                return self._cache[service_type]
            return self._get(service_type)

    def _get(self, service_type: type):
        if getattr(service_type, '__origin__', None) is typing.List and isinstance(service_type.__args__, tuple):
            ins_type = service_type.__args__[0]
            descriptors = self._service_map.getall(ins_type)
            if descriptors is None:
                return [] # always return new instance.
            else:
                cache = self._cache_list.get(ins_type) # cached
                if cache is None:
                    cache = []
                    for d in [d for d in descriptors[:-1] if d.lifetime != LifeTime.transient]:
                        cache.append(self._resolve_descriptor(d, CycleChecker()))
                    if descriptors[-1].lifetime != LifeTime.transient:
                        cache.append(self.get(ins_type))
                    self._cache_list[ins_type] = cache
                cache_copy = cache.copy()
                ret = []
                for d in descriptors:
                    if d.lifetime != LifeTime.transient:
                        ret.append(cache_copy.pop(0))
                    else:
                        ret.append(self._resolve_descriptor(d, CycleChecker()))
                assert len(cache_copy) == 0
                return ret
        else:
            return self._resolve(service_type, CycleChecker())

    def _resolve(self, service_type: type, depend_chain: CycleChecker):
        depend_chain.add_or_raise(service_type)
        try:
            descriptor = self._service_map.get(service_type)
            if descriptor is None:
                raise TypeNotFoundError('type {} is not found in container.'.format(service_type))
            obj = self._resolve_descriptor(descriptor, depend_chain)
            if descriptor.lifetime != LifeTime.transient: # cache other value
                self._cache[service_type] = obj
            return obj
        finally:
            depend_chain.remove_last()

    def _resolve_descriptor(self, descriptor: Descriptor, depend_chain: CycleChecker):
        provider = self if descriptor.lifetime != LifeTime.singleton else self._root_provider
        obj = descriptor.resolve(provider, depend_chain)
        if provider is self:
            if not (obj is self):
                if not (descriptor.service_type is IValidator):
                    self.get(IValidator).verify(descriptor.service_type, obj)
                if obj != None and hasattr(obj, '__enter__') and hasattr(obj, '__exit__'):
                    self._exit_stack.enter_context(obj)
        return obj

    def scope(self):
        return self.get(IScopedFactory).service_provider
