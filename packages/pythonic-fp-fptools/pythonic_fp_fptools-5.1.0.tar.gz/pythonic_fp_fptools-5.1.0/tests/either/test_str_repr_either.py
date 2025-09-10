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

from pythonic_fp.fptools.either import Either, LEFT, RIGHT
from pythonic_fp.fptools.maybe import MayBe


def add_gt_42(x: int, y: int) -> Either[int, str]:
    sum_xy = x + y
    if sum_xy > 42:
        return Either(sum_xy, LEFT)
    else:
        return Either('too small', RIGHT)

    def test_Either_str(self) -> None:
        assert str(Either[int, str](10, LEFT)) == '< 10 | >'
        assert str(add_gt_42(10, -4)) == '< | too small >'
        assert str(add_gt_42(10, 40)) == "< 50 | >"
        assert str(Either('Foofoo rules', RIGHT)) == "< | Foofoo rules >"
        assert str(Either[int, str](42, LEFT)) == "< 42 | >"
        assert str(Either[str, int]('foofoo', LEFT)) == "< foofoo | >"

    def test_either_repr(self) -> None:
        e1: Either[int, str] = Either('Nobody home!', RIGHT)
        e2: Either[int, str] = Either('Somebody not home!', RIGHT)
        e3: Either[int, str] = Either(5, LEFT)
        assert e1 != e2
        e5 = eval(repr(e2))
        assert e2 != Either('Nobody home!', RIGHT)
        assert e2 == Either('Somebody not home!', RIGHT)
        assert e5 == e2
        assert e5 != e3
        assert e5 is not e2
        assert e5 is not e3

        def lt5_or_nothing(x: int) -> MayBe[int]:
            if x < 5:
                return MayBe(x)
            else:
                return MayBe()

        def lt5_or_str(x: int) -> Either[int, str]:
            if x < 5:
                return Either(x, LEFT)
            else:
                return Either(f'was to be {x}', RIGHT)

        e6 = lt5_or_nothing(2)
        e7 = lt5_or_str(2)
        e8 = lt5_or_str(3)
        e9 = lt5_or_nothing(7)
        e10 = Either[int, str](10, LEFT).bind(lt5_or_str)

        assert e6 != e7
        assert e7 != e8
        assert e9 != e10
        assert e8 == eval(repr(e7)).map(lambda x: x+1)

        assert repr(e6) ==  "MayBe(2)"
        assert repr(e7) ==  "Either(2, LEFT)"
        assert repr(e8) ==  "Either(3, LEFT)"
        assert repr(e9) == "MayBe()"
        assert repr(e10) ==  "Either('was to be 10', RIGHT)"
