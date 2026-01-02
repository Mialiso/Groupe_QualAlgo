from collections import Counter 
from models import GroupeTP, GroupeProjet, Repartition

""" Algorithme glouton pour créer des groupes optimisés. 
Retourne {} si le nombre de leaders < nb_groupes (aucune répartition effectuée).
"""
def creer_groupes_glouton(g: GroupeTP, nb_groupes: int):
    # --- Pré-vérification du nombre de chefs de groupe ---
    nb_leaders = sum(1 for e in g.etudiants if getattr(e, "leader", False))
    if nb_leaders < nb_groupes:
        print(f"Pas assez de chefs de groupe : {nb_leaders} pour {nb_groupes} groupes.")
        print("Aucune répartition effectuée. Ajoutez des leaders ou réduisez le nombre de groupes.")
        return {}  # important: même type que rep.groups pour éviter les erreurs d'itération

    # Construction des groupes uniquement si faisable
    tailles = g.repartition(nb_groupes)
    groupes = [GroupeProjet(name=n, room=capacite) for n, capacite in enumerate(tailles, start=1)]
    rep = Repartition(*groupes)
    
    """ Place les étudiants dans les groupes en respectant les contraintes. """
    def candidat_ok(gr, e) -> bool:
        if gr.is_full():
            return False
        p = getattr(e, "polarite", None)
        if p is None:
            return True
        # refuse si la polarité p est déjà dans le groupe
        pols = [etu.polarite for etu in gr.members if etu.polarite is not None]
        return p not in pols
    
    """ Place un étudiant e dans un groupe selon les critères définis. """
    def place(e):
        # 1) groupes qui respectent la polarité et la capacité
        candidats = [gr for gr in rep.groups.values() if candidat_ok(gr, e)]
        if not candidats:
            # 2) dernier recours : ignorer la polarité si c'est impossible (ex: > nb_groupes pour une même polarité)
            candidats = [gr for gr in rep.groups.values() if not gr.is_full()]
            if not candidats:
                raise RuntimeError("Tous les groupes sont pleins, impossible de placer d'autres étudiants.")
        # équilibre: on choisit le groupe au plus faible avantage
        cible = min(candidats, key=lambda gr: gr.avantage())
        cible.add_member(e)

    # Trier les étudiants par avantage décroissant
    etudiants = sorted(g.etudiants, key=lambda e: e.avantage, reverse=True)
    # Séparer les leaders et non-leaders
    leaders = [e for e in etudiants if getattr(e, "leader", False)]
    non_leaders = [e for e in etudiants if not getattr(e, "leader", False)]

    # Placement des étudiants (faisable garanti par la pré-vérification)
    # 1) d'abord les leaders
    for e in leaders:
        place(e)

    # 2) puis les non-leaders
    for e in non_leaders:
        place(e)

    # -----Vérifications -----
    doublons = []
    for gid, gr in rep.groups.items():
        pols = [e.polarite for e in gr.members if e.polarite is not None]
        if len(pols) != len(set(pols)):
            doublons.append(gid)
    if doublons:
        print(f"Doublon(s) de polarité dans les groupes: {doublons}")
    
    cnt = Counter([e.polarite for e in g.etudiants if e.polarite is not None])
    impossibles = {p: c for p, c in cnt.items() if c > nb_groupes}
    if impossibles:
        print(f"Contrainte impossible pour polarité(s) {impossibles} (plus d'étudiants que de groupes).")
        
    # Calcul et affichage du score d'équilibre 
    score = rep.optimalite() 
    print(f"\nScore d'équilibre final : {score:.2f}\n")
    
    return rep.groups
