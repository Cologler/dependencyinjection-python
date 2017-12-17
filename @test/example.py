#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import os
import sys
import traceback

sys.path.append('..')

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        class A:
            pass

        class B:
            def __init__(self, a: A):
                assert isinstance(a, A)

        import dependencyinjection as di

        service = di.Services()
        service.singleton(A)
        service.singleton(B)
        provider = service.build()
        assert isinstance(provider.get(B), B)
    except Exception:
        traceback.print_exc()
        input()

if __name__ == '__main__':
    main()
