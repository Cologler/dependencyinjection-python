# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from abc import abstractmethod
import typing

from .common import IDescriptor, LifeTime

class BaseCallSite:
    def __init__(self, descriptor, options: dict=None):
        self._descriptor = descriptor
        self._options = options if options is not None else {}

    @property
    def descriptor(self):
        return self._descriptor

    @abstractmethod
    def get(self, service_provider):
        raise NotImplementedError

    @property
    def options(self):
        return self._options


class LifeTimeCallSite(BaseCallSite):
    def __init__(self, descriptor, base_callsite: BaseCallSite):
        super().__init__(descriptor)
        self._descriptor = descriptor
        self._base_callsite = base_callsite

    def _from_provider(self, provider):
        descriptor = self._descriptor
        with provider._lock:
            if descriptor not in provider._cache_list:
                obj = self._from_callsite(provider)
                if self._base_callsite.options.get('auto_exit'):
                    provider._exit_stack.enter_context(obj)
                provider._cache_list[descriptor] = obj
            return provider._cache_list[descriptor]

    def _from_callsite(self, provider):
        return self._base_callsite.get(provider)

    @staticmethod
    def wrap(descriptor: IDescriptor, callsite):
        if isinstance(callsite, NoLifeTimeCallSite):
            return callsite

        if descriptor.lifetime is LifeTime.singleton:
            return SingletonCallSite(descriptor, callsite)

        if descriptor.lifetime is LifeTime.scoped:
            return ScopedCallSite(descriptor, callsite)

        return callsite


class SingletonCallSite(LifeTimeCallSite):
    def get(self, service_provider):
        return self._from_provider(service_provider.root_provider)


class ScopedCallSite(LifeTimeCallSite):
    def get(self, service_provider):
        return self._from_provider(service_provider)


class NoLifeTimeCallSite(BaseCallSite):
    ''' the callsite does not need to wraped into `LifeTimeCallSite`.'''
    pass


class InstanceCallSite(NoLifeTimeCallSite):
    def __init__(self, descriptor, instance):
        super().__init__(descriptor)
        self._instance = instance

    def get(self, service_provider):
        return self._instance


class ServiceProviderCallSite(NoLifeTimeCallSite):
    def get(self, service_provider):
        return service_provider


class ListedCallSite(NoLifeTimeCallSite):
    def __init__(self, callsites: typing.List[BaseCallSite]):
        super().__init__(None)
        self._callsites = callsites

    def get(self, service_provider):
        items = []
        for callsite in self._callsites:
            items.append(callsite.get(service_provider))
        return items


class CallableCallSite(BaseCallSite):
    def __init__(self, descriptor, func, param_callsites: typing.Dict[str, BaseCallSite], options: dict):
        super().__init__(descriptor, options)
        self._func = func
        self._param_callsites = param_callsites

    def get(self, service_provider):
        if self._param_callsites:
            kwargs = {}
            for name, callsite in self._param_callsites.items():
                kwargs[name] = callsite.get(service_provider)
            return self._func(**kwargs)
        else:
            return self._func()
