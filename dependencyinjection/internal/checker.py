#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from .errors import CycleDependencyError


class CycleChecker:
    def __init__(self):
        self._chain = []
        self._chain_set = set()

    def add_or_raise(self, service_type: type):
        self._chain.append(service_type)
        if service_type in self._chain_set:
            msg = ' -> '.join([str(x.__name__) for x in self._chain])
            raise CycleDependencyError(msg)
        self._chain_set.add(service_type)

    def remove_last(self):
        self._chain_set.remove(self._chain.pop())
