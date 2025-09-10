# Copyright 2023-2025 Geoffrey R. Scheller
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
Lazy function evaluation
========================

Delayed function evaluations. FP tools for "non-strict" function evaluations.
Useful to delay a function's evaluation until some inner scope.

Non-strict delayed function evaluation.

- *class* **Lazy** - Delay evaluation of functions taking & returning single values
- *function* **lazy** - Delay evaluation of functions taking any number of values
- *function* **real_lazy** - Version of ``lazy`` which caches its result

"""

from collections.abc import Callable
from typing import Any, Final
from .function import sequenced
from .either import Either, LEFT, RIGHT
from .maybe import MayBe

__all__ = ['Lazy', 'lazy', 'real_lazy']


class Lazy[D, R]:
    """
    Non-strict function evaluation
    ------------------------------

    Delayed evaluation of a singled valued function.

    Class instance delays the executable of a function where ``Lazy(f, arg)``
    constructs an object that can evaluate the Callable ``f`` with its argument
    at a later time.

    .. note::

        Usually use case is to make a function "non-strict" by passing some of its
        arguments wrapped in Lazy instances.

    """

    __slots__ = ('_f', '_d', '_result', '_pure', '_evaluated', '_exceptional')

    def __init__(self, f: Callable[[D], R], d: D, pure: bool = True) -> None:
        """
        :param f: single argument function
        :param d: argument to be passed to ``f``
        :param pure: if true, cache the result for future ``eval`` method calls
        :returns: an object that can call the function ``f`` at a later time

        """
        self._f: Final[Callable[[D], R]] = f
        self._d: Final[D] = d
        self._pure: bool = pure
        self._evaluated: bool = False
        self._exceptional: MayBe[bool] = MayBe()
        self._result: Either[R, Exception]

    def __bool__(self) -> bool:
        return self._evaluated

    def eval(self) -> None:
        """Evaluate function with its argument.

        - evaluate function
        - cache result or exception if ``pure is True``
        - reevaluate if ``pure is False``

        """
        if not (self._pure and self._evaluated):
            try:
                result = self._f(self._d)
            except Exception as exc:
                self._result, self._evaluated, self._exceptional = (
                    Either(exc, RIGHT),
                    True,
                    MayBe(True),
                )
            else:
                self._result, self._evaluated, self._exceptional = (
                    Either(result, LEFT),
                    True,
                    MayBe(False),
                )

    def got_result(self) -> MayBe[bool]:
        """
        :returns: ``True`` only if an evaluated ``Lazy`` did not raise an exception.

        """
        return self._exceptional.bind(lambda x: MayBe(not x))

    def got_exception(self) -> MayBe[bool]:
        """Return true if Lazy raised exception.
        :returns: ``True`` only if ``Lazy`` raised an exception.

        """
        return self._exceptional

    def get(self, alt: R | None = None) -> R:
        """Get result only if evaluated and no exceptions occurred, otherwise
        return an alternate value.

        :param alt: optional alternate value to return if ``Lazy`` is exceptional
        :returns: the successfully evaluated result, otherwise ``alt`` if given
        :raises ValueError: if method called on a ``Lazy`` which was not yet evaluated 

        """
        if self._evaluated and self._result:
            return self._result.get()
        if alt is not None:
            return alt
        msg = 'Lazy: method get needed an alternate value but none given.'
        raise ValueError(msg)

    def get_result(self) -> MayBe[R]:
        """Get result only if evaluated and not exceptional.

        :returns: The result wrapped in a maybe monad.

        """
        if self._evaluated and self._result:
            return self._result.get_left()
        return MayBe()

    def get_exception(self) -> MayBe[Exception]:
        """Get result only if evaluate and exceptional.

        :returns: The exception thrown wrapped in a maybe monad.

        """
        if self._evaluated and not self._result:
            return self._result.get_right()
        return MayBe()


def lazy[**P, R](
    f: Callable[P, R], *args: P.args, **kwargs: P.kwargs
) -> Lazy[tuple[Any, ...], R]:
    """
    Delayed evaluations
    -------------------

    Function returning a delayed evaluation of a function of an arbitrary number
    of positional arguments.

    :param f: Function whose evaluation is to be delayed.
    :param args: Positional arguments to be passed to ``f``.
    :param kwargs: Any kwargs given are ignored.
    :returns: a ``Lazy`` object wrapping the evaluation of ``f``

    """
    return Lazy(sequenced(f), args, pure=False)


def real_lazy[**P, R](
    f: Callable[P, R], *args: P.args, **kwargs: P.kwargs
) -> Lazy[tuple[Any, ...], R]:
    """
    Cached Delayed evaluations
    --------------------------

    Function returning a delayed evaluation of a function of an arbitrary number
    of positional arguments. Evaluation is cached.

    :param f: Function whose evaluation is to be delayed.
    :param args: Positional arguments to be passed to ``f``.
    :param kwargs: Any kwargs given are ignored.
    :returns: a ``Lazy`` object wrapping the evaluation of ``f``

    """
    return Lazy(sequenced(f), args)
