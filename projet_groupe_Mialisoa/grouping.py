from typing import Sequence, Collection


class BoundedGroup(object):
    """
    Objects representing groups with a limited capacity.
    """

    def __init__(self, name=None, members: Collection = (), room: int = 0):
        """
        :param name: Groupe name (informative)
        :param members: current members
        :param room: extra capacity
        """
        self.name = name
        self.members = list(members)
        self.capacity = room + len(self.members)

    @property
    def room(self):
        return self.capacity - len(self.members)

    def __repr__(self):
        args = []
        if self.name is not None:
            args.append(f'name={repr(self.name)}')
        if self.members:
            args.append(f'members={sorted(self.members)}')
        if self.room:
            args.append(f'room={self.room}')
        return f'{self.__class__.__name__}({", ".join(args)})'

    def is_full(self):
        return self.room == 0

    def add_member(self, m):
        if self.is_full():
            raise ValueError(f'Group {self.name} is full')
        self.members.append(m)  


class BoundedPartition(object):

    def __init__(self, *groupes: BoundedGroup):
        self.groups = {g.name: g for g in groupes}
        if len(self.groups) != len(groupes):
            raise ValueError

    @property
    def capacity(self):
        return sum(g.capacity for g in self.groups.values())

    @property
    def member_count(self):
        return sum(len(g.members) for g in self.groups.values())

    def __repr__(self):
        groups = (f'({len(g.members)}/{g.capacity})' for g in self.groups.values())
        return f'<BoundedPartition: {"".join(groups)}>'
