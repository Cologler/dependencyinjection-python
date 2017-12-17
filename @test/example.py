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
        service.scoped(A)
        service.singleton(B)
        provider = service.build()
        assert isinstance(provider.get(A), A)
        assert isinstance(provider.get(B), B)

        with provider.scope() as scoped_provider:
            assert provider.get(A) is provider.get(A)
            assert scoped_provider.get(B) is scoped_provider.get(B)
            assert provider.get(B) is scoped_provider.get(B)
            assert not (provider.get(A) is scoped_provider.get(A))
    except Exception:
        traceback.print_exc()
        input()

if __name__ == '__main__':
    main()
