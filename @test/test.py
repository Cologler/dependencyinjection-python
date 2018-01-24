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
import unittest

sys.path.insert(0, '..')

import dependencyinjection as di

class Test(unittest.TestCase):
    def test_instance(self):
        class A:
            pass

        service = di.Services()
        # type safe
        with self.assertRaises(TypeError):
            service.instance(A, 1)
        service.instance(A, A())
        provider = service.build()
        a = provider.get(A)
        # ref equals
        self.assertTrue(provider.get(A) is provider.get(A))
        # type safe
        self.assertTrue(isinstance(a, A))

    def test_singleton(self):
        tester = self
        class A:
            pass

        class B:
            def __init__(self, a: A):
                tester.assertIsNotNone(a)
                tester.assertTrue(isinstance(a, A))

        service = di.Services()
        service.singleton(A, A)
        service.singleton(B, B)
        provider = service.build()
        # ref equals
        self.assertTrue(provider.get(A) is provider.get(A))
        self.assertTrue(provider.get(B) is provider.get(B))

        with provider.scope() as provider1:
            self.assertTrue(provider.get(A) is provider1.get(A))
            self.assertTrue(provider.get(B) is provider1.get(B))

    def test_scoped(self):
        tester = self
        class A:
            pass

        class B:
            def __init__(self, a: A):
                tester.assertIsNotNone(a)
                tester.assertTrue(isinstance(a, A))
                self.exited = False

        service = di.Services()
        service.scoped(A, A)
        service.scoped(B, B)
        root_provider = service.build()

        with root_provider.scope() as provider1:
            with provider1.scope() as provider2:
                self.assertTrue(root_provider.get(A) is root_provider.get(A))
                self.assertTrue(root_provider.get(B) is root_provider.get(B))
                self.assertTrue(provider1.get(A) is provider1.get(A))
                self.assertTrue(provider1.get(B) is provider1.get(B))
                self.assertTrue(provider2.get(A) is provider2.get(A))
                self.assertTrue(provider2.get(B) is provider2.get(B))
                self.assertFalse(root_provider.get(A) is provider1.get(A))
                self.assertFalse(provider1.get(A) is provider2.get(A))
                self.assertFalse(root_provider.get(B) is provider1.get(B))
                self.assertFalse(provider1.get(B) is provider2.get(B))

    def test_transient(self):
        tester = self
        class A:
            pass

        class B:
            def __init__(self, a: A):
                tester.assertIsNotNone(a)
                tester.assertTrue(isinstance(a, A))

        service = di.Services()
        service.transient(A, A)
        service.transient(B, B)
        provider = service.build()
        # ref equals
        self.assertFalse(provider.get(A) is provider.get(A))
        self.assertFalse(provider.get(B) is provider.get(B))

    def test_context(self):
        tester = self
        class A:
            pass

        class B:
            def __init__(self, a: A):
                self.exited = False

            def __enter__(self):
                pass

            def __exit__(self, exc_type, exc_value, traceback):
                self.exited = True

        service = di.Services()
        service.scoped(A, A)
        service.scoped(B, B)
        root_provider = service.build()
        with root_provider as root_provider:
            broot = root_provider.get(B)
            self.assertFalse(broot.exited)
            with root_provider.scope() as provider1:
                b1 = provider1.get(B)
                self.assertFalse(b1.exited)
                with provider1.scope() as provider2:
                    b2 = provider2.get(B)
                    self.assertFalse(b2.exited)
                self.assertTrue(b2.exited)
            self.assertTrue(b1.exited)
        self.assertTrue(broot.exited)

    def test_multi_service(self):
        tester = self
        class A: pass
        class A1(A): pass
        class A2(A): pass

        class B:
            def __init__(self, a: A):
                tester.assertIsNotNone(a)
                tester.assertTrue(isinstance(a, A2))

        service = di.Services()
        service.singleton(A, A1)
        service.singleton(A, A2)
        service.singleton(B, B)
        provider = service.build()
        # ref equals
        self.assertTrue(provider.get(A) is provider.get(A))
        self.assertTrue(provider.get(B) is provider.get(B))
        import typing
        items = provider.get(typing.List[A])
        self.assertEqual(2, len(items))
        self.assertTrue(isinstance(items[0], A1))
        self.assertTrue(isinstance(items[1], A2))

    def test_get_none(self):
        service = di.Services()
        provider = service.build()
        self.assertIsNone(provider.get(str))

    def test_bind(self):
        tester = self

        class A:
            pass

        class B:
            def __init__(self, a):
                tester.assertIsNotNone(a)
                tester.assertTrue(isinstance(a, A))

        service = di.Services()
        service.scoped(A)
        service.scoped(B)
        provider1 = service.build()
        with self.assertRaises(Exception):
            self.assertTrue(isinstance(provider1.get(B), B))
        service.bind('a', A) # after bind name to type.
        provider2 = service.build()
        self.assertTrue(isinstance(provider2.get(B), B))

    def test_service_provider(self):
        tester = self

        class A:
            def __init__(self, injected_provider: di.IServiceProvider):
                self.injected_provider = injected_provider


        service = di.Services()
        service.scoped(A)
        provider = service.build()
        tester.assertIs(provider.get(A).injected_provider, provider)

    def test_map(self):
        class A:
            pass
        class B(A):
            pass
        class C(B):
            pass

        provider = di.Services().scoped(C).scoped(B).map(A, C).build()
        # define twice, so C and B is not the same thing.
        self.assertIsNot(provider[C], provider[B])
        # with `map`, so A is C.
        self.assertIs(provider[C], provider[A])


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        unittest.main()
    except Exception:
        traceback.print_exc()
        input()

if __name__ == '__main__':
    main()
