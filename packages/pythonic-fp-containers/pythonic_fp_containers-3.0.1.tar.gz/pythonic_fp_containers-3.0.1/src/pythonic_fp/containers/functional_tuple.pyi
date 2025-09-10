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

from collections.abc import Callable, Iterator
from typing import Never, overload, TypeVar, SupportsIndex
from pythonic_fp.iterables.merging import MergeEnum

__all__ = ['FTuple']

D = TypeVar('D', covariant=True)

class FTuple[D](tuple[D, ...]):
    def __reversed__(self) -> Iterator[D]: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object, /) -> bool: ...
    @overload
    def __getitem__(self, idx: SupportsIndex) -> D: ...
    @overload
    def __getitem__(self, idx: slice) -> tuple[D, ...]: ...
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
    def copy(self) -> FTuple[D]: ...
    def __add__(self, other: object, /) -> tuple[D, ...]: ...
    def __mul__(self, num: SupportsIndex) -> tuple[D, ...]: ...
    def __rmul__(self, num: SupportsIndex) -> tuple[D, ...]: ...
    def accummulate[L](
        self, f: Callable[[L, D], L], s: L | None = None, /
    ) -> FTuple[L]: ...
    def map[U](self, f: Callable[[D], U], /) -> FTuple[U]: ...
    def bind[U](
        self,
        f: Callable[[D], FTuple[U]],
        merge_enum: MergeEnum = MergeEnum.Concat,
        yield_partials: bool = False,
    ) -> FTuple[U] | Never: ...
