# dependency injection

**try use [anyioc](https://github.com/Cologler/anyioc-python).**

A dependency injection framework for python.

Just like `Microsoft.Extensions.DependencyInjection`.

## Usage

``` py
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
```
