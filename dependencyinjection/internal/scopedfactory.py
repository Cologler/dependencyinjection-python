#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from .common import IScopedFactory, IServiceProvider
from .provider import ServiceProvider

class ScopedFactory(IScopedFactory):
    def __init__(self, parent: IServiceProvider):
        self._service_provider = ServiceProvider(parent_provider=parent)

    @property
    def service_provider(self):
        return self._service_provider
