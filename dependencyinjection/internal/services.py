#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from .common import LifeTime, IValidator, IServiceProvider, IScopedFactory, ILock, FakeLock
from .scopedfactory import ScopedFactory
from .provider import ServiceProvider
from .descriptors import CallableDescriptor, TypedDescriptor, InstanceDescriptor, ServiceProviderDescriptor
from .validator import Validator
from .servicesmap import ServicesMap
from .lock import ThreadLock

class Services:
    def __init__(self):
        self._services = []
        self._name_map = {}
        self.singleton(IValidator, Validator)
        self.singleton(ILock, FakeLock)

    def add(self, service_type: type, obj: (callable, type), lifetime: LifeTime):
        ''' register a singleton type. '''
        if not isinstance(service_type, type):
            raise TypeError('service_type must be a type')
        if not isinstance(lifetime, LifeTime):
            raise TypeError
        if isinstance(obj, type):
            self._services.append(TypedDescriptor(service_type, obj, lifetime))
        elif callable(obj):
            self._services.append(CallableDescriptor(service_type, obj, lifetime))
        else:
            raise ValueError
        return self

    def singleton(self, service_type: type, obj: (callable, type)=None):
        ''' register a singleton type. '''
        if obj is None:
            obj = service_type
        return self.add(service_type, obj, LifeTime.singleton)

    def instance(self, service_type: type, obj):
        ''' register a singleton instance to service type. '''
        if not isinstance(obj, service_type):
            raise TypeError('obj must be {} type'.format(service_type))
        self._services.append(InstanceDescriptor(service_type, obj))
        return self

    def scoped(self, service_type: type, obj: (callable, type)=None):
        ''' register a scoped type. '''
        if obj is None:
            obj = service_type
        return self.add(service_type, obj, LifeTime.scoped)

    def transient(self, service_type: type, obj: (callable, type)=None):
        ''' register a transient type. '''
        if obj is None:
            obj = service_type
        return self.add(service_type, obj, LifeTime.transient)

    def threadsafety(self):
        '''
        make all `LifeTime.singleton` service thread safety.
        '''
        self.singleton(ILock, ThreadLock)
        return self

    def build(self) -> IServiceProvider:
        self.transient(IScopedFactory, ScopedFactory)
        self._services.append(ServiceProviderDescriptor())
        service_map = ServicesMap(self._services)
        return ServiceProvider(service_map=service_map)
