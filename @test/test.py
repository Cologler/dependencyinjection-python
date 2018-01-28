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

    def test_singleton_dep_is_root(self):
        class A:
            pass

        class B:
            def __init__(self, a: A):
                self.a = a

        service = di.Services()
        service.scoped(A, A)
        service.singleton(B, B)
        root_provider = service.build()

        with root_provider.scope() as child_provider:
            self.assertIs(child_provider.get(B).a, root_provider.get(A))

    def test_scoped(self):
        tester = self

        class A:
            pass

        class B:
            def __init__(self, a: A):
                self.a = a

        service = di.Services()
        service.scoped(A, A)
        service.scoped(B, B)
        root_provider = service.build()

        def scoped_item_is(service_provider):
            self.assertIs(service_provider.get(A), service_provider.get(A))
            self.assertIs(service_provider.get(B), service_provider.get(B))
            self.assertIs(service_provider.get(B).a, service_provider.get(A))

        def scoped_item_is_not(provider_1, provider_2):
            self.assertIsNot(provider_1.get(A), provider_2.get(A))
            self.assertIsNot(provider_1.get(B), provider_2.get(B))

        with root_provider.scope() as provider1:
            with provider1.scope() as provider2:
                scoped_item_is(root_provider)
                scoped_item_is(provider1)
                scoped_item_is(provider2)
                scoped_item_is_not(root_provider, provider1)
                scoped_item_is_not(root_provider, provider2)
                scoped_item_is_not(provider1, provider2)

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
        service.scoped(B, B, auto_exit=True)
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
                self.a = a
                tester.assertIsNotNone(a)
                tester.assertTrue(isinstance(a, A2))

        service = di.Services()
        service.singleton(A, A1)
        service.singleton(A, A2)
        service.singleton(B, B)
        provider = service.build()

        # B().a should be last singleton(A, ?) => A2
        self.assertIsInstance(provider.get(B).a, A2)

        # list of B
        import typing
        itemsB = provider.get(typing.List[B])
        self.assertEqual(1, len(itemsB))
        self.assertIs(itemsB[0], provider.get(B))

        # list of A

        items1 = provider.get(typing.List[A])
        self.assertEqual(2, len(items1))
        self.assertIsInstance(items1[0], A1)
        self.assertIsInstance(items1[1], A2)

        items2 = provider.get(typing.List[A])
        self.assertEqual(2, len(items2))
        self.assertIsInstance(items2[0], A1)
        self.assertIsInstance(items2[1], A2)

        self.assertIsNot(items1, items2)

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
