import math
from typing import List, Sequence

from grouping import BoundedPartition, BoundedGroup


class Etudiant(object):

    def __init__(self, nom, prenom, avantage: float, leader=False, polarite: int = None, alea: float = 0):
        self.nom = nom
        self.prenom = prenom
        self.avantage = avantage
        self.leader = leader
        self.polarite = polarite
        self.alea = alea

    def __repr__(self):
        return "%s %s %s" % (self.nom, self.leader, self.polarite)

    def __lt__(self, other):
        return self.nom <= other.nom


def has_duplicate_numbers(li):
    for i, n in enumerate(li):
        if n is None:
            continue
        if n in li[i+1:]:
            return True
    return False


class GroupeProjet(BoundedGroup):

    def avantage(self):
        return sum(etu.avantage for etu in self.members)

    def avec_leader(self):
        return any(etu.leader for etu in self.members)

    def incompatible(self):
        polarites = [etu.polarite for etu in self.members if etu.polarite is not None]
        return has_duplicate_numbers(polarites)

    def __repr__(self):
        return super(GroupeProjet, self).__repr__() + f'={self.avantage():.1f}'


class GroupeTP(object):

    def __init__(self, nom, etudiants: Sequence[Etudiant]):
        self.nom = nom
        self.etudiants = list(etudiants)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.nom}, {self.etudiants})'

    def repartition(self, nb_groupes: int) -> List[int]:
        nb_etu = len(self.etudiants)
        res = [nb_etu // nb_groupes + int(i < nb_etu % nb_groupes) for i in range(nb_groupes)]
        assert sum(res) == nb_etu
        return res


class Repartition(BoundedPartition):

    def validite(self):
        avec_leader = all(g.avec_leader() for g in self.groups.values())
        if not avec_leader:
            return False
        incompatible = any(g.incompatible() for g in self.groups.values())
        if incompatible:
            return False
        return True


    def optimalite(self):
        avantages = [g.avantage() for g in self.groups.values()]
        return max(avantages) - min(avantages)

    @classmethod
    def faire(cls, g: GroupeTP, nb: int = 3):
        tailles = g.repartition(nb)
        groupes = [GroupeProjet(name=n, room=capacite) for n, capacite in enumerate(tailles, start=1)]
        rep = cls(*groupes)
        score_optimal = math.inf
        groupes_optimaux = None
        for rep_complete in rep.possible_assignments(g.etudiants):
            if not rep_complete.validite():
                continue
            score = rep_complete.optimalite()
            if score < score_optimal:
                print('Nouvel optimal: ', score)
                score_optimal = score
                groupes_optimaux = rep_complete.groups
        return groupes_optimaux
