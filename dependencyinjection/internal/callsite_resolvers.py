# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from .common import LifeTime, IServiceProvider, ICallSiteResolver
from .descriptors import CallableDescriptor

class CallSiteResolver(ICallSiteResolver):
    def __init__(self, service_provider: IServiceProvider):
        self._service_provider = service_provider

    def resolve(self, service_type: type, depend_chain):
        descriptor = CallableDescriptor.try_create(service_type, service_type, LifeTime.transient)
        if descriptor:
            return self._service_provider.get_callsite(descriptor, depend_chain)
