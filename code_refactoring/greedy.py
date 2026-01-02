
from __future__ import annotations
from typing import List
import random
from models import Etudiant, GroupeTP, Repartition

def creer_groupes_glouton(g: GroupeTP, nb_groupes: int, seed: int | None = None) -> Repartition:
    tailles = g.repartition(nb_groupes)
    rep = Repartition.from_sizes(tailles)

    # Tri des étudiants : leaders d'abord, puis avantage décroissant
    etudiants = sorted(g.etudiants, key=lambda e: (not e.leader, -e.avantage))

    if seed is not None:
        rnd = random.Random(seed)
        # légère perturbation stable: on mélange par blocs d'avantage identique
        i = 0
        while i < len(etudiants):
            j = i + 1
            while j < len(etudiants) and etudiants[j].avantage == etudiants[i].avantage and etudiants[j].leader == etudiants[i].leader:
                j += 1
            block = etudiants[i:j]
            rnd.shuffle(block)
            etudiants[i:j] = block
            i = j

    leaders = [e for e in etudiants if e.leader]
    autres  = [e for e in etudiants if not e.leader]

    # 1) Un leader par groupe si possible
    group_list = list(rep.groups.values())
    for gr, e in zip(group_list, leaders):
        if gr.can_accept(e):
            gr.add_member(e)

    # 2) Remplissage équilibré en respectant polarités
    def admissibles(e: Etudiant):
        return [gr for gr in rep.groups.values() if gr.can_accept(e)]

    reste = autres + leaders[len(group_list):]
    for e in reste:
        cand = admissibles(e)
        if not cand:
            # fallback ultime: ignorer la contrainte polarité si blocage
            cand = [gr for gr in rep.groups.values() if not gr.is_full()]
            if not cand:
                raise RuntimeError("Plus de capacité disponible pour placer un étudiant.")
        cible = min(cand, key=lambda gr: gr.avantage_total())
        cible.add_member(e)

    return rep
