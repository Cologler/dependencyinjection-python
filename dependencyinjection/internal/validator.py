#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from .common import IValidator
from .errors import InvalidError

class Validator(IValidator):
    def verify(self, service_type: type, obj):
        if not isinstance(obj, service_type):
            raise InvalidError
