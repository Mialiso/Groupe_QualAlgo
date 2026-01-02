
from __future__ import annotations
from typing import Iterable
from models import Repartition

def score_equilibre(rep: Repartition) -> float:
    """Écart max-min des avantages totaux entre les groupes."""
    totaux = [g.avantage_total() for g in rep.groups.values()]
    if not totaux:
        return 0.0
    return max(totaux) - min(totaux)

def leaders_possibles(rep: Repartition) -> bool:
    nb_leaders = sum(1 for e in rep.tous_les_etudiants() if getattr(e, "leader", False))
    return nb_leaders >= len(rep.groups)

def validite_globale(rep: Repartition) -> bool:
    # 1) Aucune polarité en double dans un groupe
    for g in rep.groups.values():
        pols = [e.polarite for e in g.members if e.polarite is not None]
        if len(pols) != len(set(pols)):
            return False
    # 2) Si assez de leaders globalement, chaque groupe doit en avoir un
    if leaders_possibles(rep):
        for g in rep.groups.values():
            if not g.a_un_leader():
                return False
    return True
