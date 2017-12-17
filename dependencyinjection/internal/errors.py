#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import typing

class InvalidError(Exception):
    pass


class CycleDependencyError(Exception):
    def __init__(self, chain: typing.List[type]):
        self._chain = chain


class TypeNotFoundError(Exception):
    pass
