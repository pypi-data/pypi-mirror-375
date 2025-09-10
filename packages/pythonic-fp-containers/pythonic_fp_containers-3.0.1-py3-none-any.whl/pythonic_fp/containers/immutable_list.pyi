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

from collections.abc import Callable, Iterable, Iterator, Hashable
from typing import Never, overload, TypeVar
from pythonic_fp.iterables.merging import MergeEnum

__all__ = ['IList']

D = TypeVar('D', covariant=True)
T = TypeVar('T')


class IList[D](Hashable):
    __slots__ = ('_ds', '_len', '_hash')
    __match_args__ = ('_ds', '_len')

    L = TypeVar('L')
    R = TypeVar('R')
    U = TypeVar('U')

    def __init__(self, *dss: Iterable[D]) -> None: ...
    def __hash__(self) -> int: ...
    def __iter__(self) -> Iterator[D]: ...
    def __reversed__(self) -> Iterator[D]: ...
    def __bool__(self) -> bool: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: object, /) -> bool: ...
    @overload
    def __getitem__(self, idx: int, /) -> D: ...
    @overload
    def __getitem__(self, idx: slice, /) -> IList[D]: ...
    def foldl[L](
        self,
        f: Callable[[L, D], L],
        /,
        start: L | None = None,
        default: L | None = None,
    ) -> L | None: ...
    def foldr[R](
        self,
        f: Callable[[D, R], R],
        /,
        start: R | None = None,
        default: R | None = None,
    ) -> R | None: ...
    def __add__(self, other: IList[D], /) -> IList[D]: ...
    def __mul__(self, num: int, /) -> IList[D]: ...
    def __rmul__(self, num: int, /) -> IList[D]: ...
    def accummulate[L](
        self, f: Callable[[L, D], L], s: L | None = None, /
    ) -> IList[L]: ...
    def map[U](self, f: Callable[[D], U], /) -> IList[U]: ...
    def bind[U](
        self,
        f: Callable[[D], IList[U]],
        merge_enum: MergeEnum = MergeEnum.Concat,
        yield_partials: bool = False,
    ) -> IList[U] | Never: ...
