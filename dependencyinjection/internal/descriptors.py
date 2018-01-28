#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from abc import abstractmethod
import inspect
from .common import LifeTime, IServiceProvider, IDescriptor, ICallSiteMaker
from .param_type_resolver import ParameterTypeResolver
from .errors import ParameterTypeResolveError
from .callsites import (
    InstanceCallSite,
    ServiceProviderCallSite,
    CallableCallSite,
    ListedCallSite
)

class Descriptor(IDescriptor):
    def __init__(self, service_type: type, lifetime: LifeTime):
        if not isinstance(service_type, type):
            raise TypeError('service_type must be a type')
        if not isinstance(lifetime, LifeTime):
            raise TypeError('lifetime must be a LifeTime')

        self._service_type = service_type
        self._lifetime = lifetime

    @property
    def service_type(self):
        return self._service_type

    @property
    def lifetime(self):
        return self._lifetime


class CallableDescriptor(Descriptor):
    def __init__(self, service_type: type, func: callable, lifetime: LifeTime):
        super().__init__(service_type, lifetime)
        if not callable(func):
            raise TypeError

        self._func = func
        self._params_type_map = None

        if service_type is ParameterTypeResolver:
            raise RuntimeError(f'service_type cannot be {ParameterTypeResolver}.')

    def make_callsite(self, service_provider, depend_chain):
        param_callsites = {}
        signature = inspect.signature(self._func)

        params = signature.parameters.values()
        params = [p for p in params if p.kind is p.POSITIONAL_OR_KEYWORD]
        if params:
            type_resolver: ParameterTypeResolver = service_provider.get(ParameterTypeResolver)
            for param in params:
                callsite = None
                if param.default is param.empty:
                    try:
                        param_type = type_resolver.resolve(param, False)
                    except ParameterTypeResolveError as err:
                        if isinstance(self._func, type):
                            msg = f'error on creating type {self._func}: {err}'
                        else:
                            msg = f'error on invoke facrory {self._func}: {err}'
                        raise ParameterTypeResolveError(msg)
                    callsite = service_provider.get_callsite(param_type, depend_chain)
                else:
                    param_type = type_resolver.resolve(param, True)
                    if param_type is not None:
                        callsite = service_provider.get_callsite(param_type, depend_chain, required=False)
                    if callsite is None:
                        callsite = InstanceCallSite(None, param.default)
                param_callsites[param.name] = callsite

        return CallableCallSite(self, self._func, param_callsites)


class InstanceDescriptor(Descriptor):
    def __init__(self, service_type: type, instance):
        super().__init__(service_type, LifeTime.singleton)
        if not isinstance(instance, service_type):
            raise TypeError('obj is not a {}'.format(service_type))
        self._instance = instance

    def make_callsite(self, service_provider, depend_chain):
        return InstanceCallSite(self, self._instance)


class ServiceProviderDescriptor(Descriptor):
    def __init__(self):
        super().__init__(IServiceProvider, LifeTime.scoped)

    def make_callsite(self, service_provider, depend_chain):
        return ServiceProviderCallSite(self)


class MapDescriptor(Descriptor):
    def __init__(self, service_type: type, target_service_type: type):
        super().__init__(service_type, LifeTime.transient)
        if not isinstance(target_service_type, type):
            raise TypeError('target_service_type must be a type')
        self._target = target_service_type

    def make_callsite(self, service_provider, depend_chain):
        return service_provider.get_callsite(self._target, depend_chain)


class ListedDescriptor(ICallSiteMaker):
    def __init__(self, descriptors):
        self._descriptors = tuple(descriptors)

    def __hash__(self):
        return hash(self._descriptors)

    def __eq__(self, other):
        return self._descriptors == other

    def make_callsite(self, service_provider, depend_chain):
        callsites = []
        for descriptor in self._descriptors:
            callsites.append(service_provider.get_callsite(descriptor, depend_chain))
        return ListedCallSite(callsites)
