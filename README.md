# dependency injection

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
service.singleton(A)
service.singleton(B)
provider = service.build()
assert isinstance(provider.get(B), B)
```
