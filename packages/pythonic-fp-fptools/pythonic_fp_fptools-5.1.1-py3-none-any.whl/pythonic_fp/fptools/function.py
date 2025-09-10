# Copyright 2024-2025 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
FP tools for functions
======================

FP utilities to manipulate and partially apply functions

- *function* **swap** - Swap the arguments of a 2 argument function
- *function* **sequenced** - Convert function to take a sequence of its arguments
- *function* **negate** - Transforms a predicate to its negation
- *function* **partial** - Returns a partially applied function

"""

from collections.abc import Callable
from typing import Any, ParamSpec

__all__ = ['swap', 'sequenced', 'partial', 'negate']

P = ParamSpec('P')


def swap[U, V, R](f: Callable[[U, V], R]) -> Callable[[V, U], R]:
    """
    Swap args
    ---------

    Swap arguments of a two argument function.

    :param f: Two argument function.
    :returns: A version of ``f`` with its arguments swapped.

    """
    return lambda v, u: f(u, v)


def negate[**P](f: Callable[P, bool]) -> Callable[P, bool]:
    """
    Negate predicate
    ----------------

    Take a predicate and return its negation.

    :param f: a function ``f`` which returns a bool
    :returns: the function ``not f``
    """

    def ff(*args: P.args, **kwargs: P.kwargs) -> bool:
        return not f(*args, **kwargs)

    return ff


def sequenced[R](f: Callable[..., R]) -> Callable[[tuple[Any]], R]:
    """
    Multi-to-single valued
    ----------------------

    Convert a function with arbitrary positional arguments to one taking
    a tuple of the original arguments.

    - was awaiting typing and mypy "improvements" to ParamSpec

      - return type: Callable[tuple[P.args], R]   ???
      - return type: Callable[[tuple[P.args]], R] ???

    TODO: Look into replacing this function with a Callable class?

    """

    def ff(tupled_args: tuple[Any]) -> R:
        return f(*tupled_args)

    return ff


def partial[**P, R](f: Callable[P, R], *args: Any) -> Callable[..., R]:
    """
    Partial application
    -------------------

    Partially apply arguments to a function, left to right.

    - type-wise the only thing guaranteed is the return type
    - best practice is to cast the result immediately

    """

    def finish(*rest: Any) -> R:
        return sequenced(f)(args + rest)

    return finish
