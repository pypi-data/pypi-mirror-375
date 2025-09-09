from .type_class import Tp
from .type_classes import Semigroup, Functor
from .utils import identity, assert_and, expr, compose, curry, cache, Filter, State

lst = Tp([Functor, Semigroup], [1, 2, 3])

# fmt: off
__all__ = [
    # type classes
    "Semigroup", "Functor",
    # utils
    "identity", "assert_and", "expr", "compose", "curry", "cache",
    "Filter", "State",
    "lst"
]
# fmt: on
