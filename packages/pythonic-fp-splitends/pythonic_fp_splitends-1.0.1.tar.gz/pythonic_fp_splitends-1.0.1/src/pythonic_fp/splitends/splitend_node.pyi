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

from collections.abc import Callable, Hashable, Iterator
from typing import TypeVar
from pythonic_fp.fptools.maybe import MayBe

__all__ = ['SENode']

D = TypeVar('D', bound=Hashable)

class SENode[D]:
    __slots__ = '_data', '_prev'

    _data: D
    _prev: MayBe[SENode[D]]

    def __init__(self, data: D, prev: SENode[D] | None = None) -> None: ...
    def __iter__(self) -> Iterator[D]: ...
    def __bool__(self) -> bool: ...
    def __eq__(self, other: object) -> bool: ...
    def peak(self) -> D: ...
    def pop2(self) -> tuple[D, SENode[D]]: ...
    def push(self, data: D) -> SENode[D]: ...
    def fold[T](self, f: Callable[[T, D], T], init: T | None = None) -> T: ...
