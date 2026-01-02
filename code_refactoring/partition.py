
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Generic, Iterable, Iterator, List, Dict, TypeVar

T = TypeVar("T")

@dataclass
class BoundedGroup(Generic[T]):
    name: str
    room: int
    members: List[T] = field(default_factory=list)

    def is_full(self) -> bool:
        return len(self.members) >= self.room

    def add_member(self, item: T) -> None:
        if self.is_full():
            raise ValueError(f"Groupe {self.name} plein (capacité={self.room})")
        self.members.append(item)

    def remove_member(self, item: T) -> None:
        self.members.remove(item)

    def __len__(self) -> int:
        return len(self.members)

    def __iter__(self) -> Iterator[T]:
        return iter(self.members)


@dataclass
class BoundedPartition(Generic[T]):
    groups: Dict[str, BoundedGroup[T]]

    @classmethod
    def from_sizes(cls, prefix: str, sizes: Iterable[int]) -> "BoundedPartition[T]":
        d: Dict[str, BoundedGroup[T]] = {}
        for i, size in enumerate(sizes, start=1):
            d[f"{prefix}{i}"] = BoundedGroup[T](name=f"{prefix}{i}", room=size)
        return cls(groups=d)

    def __len__(self) -> int:
        return sum(len(g.members) for g in self.groups.values())

    def total_capacity(self) -> int:
        return sum(g.room for g in self.groups.values())

    def not_full(self) -> List[BoundedGroup[T]]:
        return [g for g in self.groups.values() if not g.is_full()]
