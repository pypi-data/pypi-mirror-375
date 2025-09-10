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

from collections.abc import Callable, Iterable, Iterator
from typing import cast, Never
from pythonic_fp.fptools.function import negate, swap
from pythonic_fp.fptools.maybe import MayBe
from pythonic_fp.sentinels.novalue import NoValue
from .drop_take import drop_while, take_while_split

__all__ = [
    'accumulate',
    'reduce_left',
    'fold_left',
    'maybe_fold_left',
    'sc_reduce_left',
    'sc_reduce_right',
]

def accumulate[D, L](
    iterable: Iterable[D], f: Callable[[L, D], L], initial: L | NoValue = NoValue()
) -> Iterator[L]: ...
def reduce_left[D](iterable: Iterable[D], f: Callable[[D, D], D]) -> D | Never: ...
def fold_left[D, L](
    iterable: Iterable[D], f: Callable[[L, D], L], initial: L
) -> L | Never: ...
def maybe_fold_left[D, L](
    iterable: Iterable[D], f: Callable[[L, D], L], initial: L | NoValue = NoValue()
) -> MayBe[L] | Never: ...
def sc_reduce_left[D](
    iterable: Iterable[D],
    f: Callable[[D, D], D],
    start: Callable[[D], bool] = (lambda d: True),
    stop: Callable[[D], bool] = (lambda d: False),
    include_start: bool = True,
    include_stop: bool = True,
) -> tuple[MayBe[D], Iterator[D]]: ...
def sc_reduce_right[D](
    iterable: Iterable[D],
    f: Callable[[D, D], D],
    start: Callable[[D], bool] = (lambda d: False),
    stop: Callable[[D], bool] = (lambda d: False),
    include_start: bool = True,
    include_stop: bool = True,
) -> tuple[MayBe[D], Iterator[D]]: ...
