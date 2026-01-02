from openpyxl import load_workbook
from students import Etudiant, GroupeTP, GroupeProjet, Repartition
import sys

import unicodedata, re

class Row:
    def __init__(self, head, row):
        self.head = head
        self.row = row
        # index des colonnes normalisées -> position
        self._col_index = {self._norm(c.value): i for i, c in enumerate(self.head)}

    @staticmethod
    def _norm(s):
        if s is None:
            return ""
        s = unicodedata.normalize('NFKD', str(s))
        s = "".join(ch for ch in s if not unicodedata.combining(ch))  # retire accents
        s = s.lower().strip()
        s = s.replace("«", "").replace("»", "").replace('"', "").replace("'", "")
        s = re.sub(r"\s+", " ", s)  # espaces multiples -> simple espace
        return s

    def __getitem__(self, item):
        key = self._norm(item)
        if key not in self._col_index:
            raise KeyError(item)
        return self.row[self._col_index[key]].value

    def get(self, item, default=None):
        try:
            val = self[item]
        except KeyError:
            return default
        return default if val in (None, "") else val


def load_groups(filename, sheet):
    wb = load_workbook(filename=filename, data_only=True, read_only=True)
    sh = wb[sheet]
    head, *rows = sh.rows
    res = {}
    for r in rows:
        r = Row(head, r)
        nom_groupe = r['Groupe']
        if nom_groupe:
            groupe = res.setdefault(nom_groupe, GroupeTP(nom_groupe, etudiants=()))
            # Récupération robuste Nom/Prénom
            full = (r.get('Prénom') or "").strip()  # OK grâce à Row.get
            nom_xlsx = (r.get('Nom') or "").strip()
            nom_ok = nom_xlsx if nom_xlsx else (full.split()[-1] if full else "")
            prenom_ok = full.replace(nom_ok, "", 1).strip() or full

            # Normalisation du chef (bool) et de la polarité (int/None)
            is_leader = str(r.get('« chef »') or r.get('chef') or "").lower() in ("1","true","oui","yes","y")
            pol_raw = r.get('À séparer')
            try:
                pol_ok = int(pol_raw) if pol_raw not in (None, "", "-") else None
            except (TypeError, ValueError):
                pol_ok = None

            etudiant = Etudiant(nom=nom_ok,
                                prenom=prenom_ok,
                                avantage=float(r['Avantage compté'] or 0),
                                leader=is_leader,
                                polarite=pol_ok)
            groupe.etudiants.append(etudiant)
    return res

def creer_groupes_glouton(g: GroupeTP, nb_groupes: int):
    tailles = g.repartition(nb_groupes)
    groupes = [GroupeProjet(name=n, room=capacite) for n, capacite in enumerate(tailles, start=1)]
    rep = Repartition(*groupes)

    # Trier les étudiants par avantage décroissant
    etudiants = sorted(g.etudiants, key=lambda e: e.avantage, reverse=True)

    # Étape 1 : placer un leader par groupe
    leaders = [e for e in etudiants if e.leader]
    non_leaders = [e for e in etudiants if not e.leader]

    for i, leader in enumerate(leaders):
        groupe = rep.groups[(i % nb_groupes) + 1]
        groupe.add_member(leader)

    # Étape 2 : répartir les autres en équilibrant les avantages
    for e in non_leaders:
        candidats = [gr for gr in rep.groups.values() if not gr.is_full() and not gr.incompatible()]
        if not candidats:
            candidats = [gr for gr in rep.groups.values() if not gr.is_full()]
        cible = min(candidats, key=lambda gr: gr.avantage())
        cible.add_member(e)
    
    # Vérification des contraintes globales
    if not rep.validite():
        print("⚠️ Contrainte non satisfaite : manque de leader ou polarités en conflit.")


    # Calcul du score d'équilibre final
    score = rep.optimalite()
    print(f"\nScore d'équilibre final : {score:.2f}\n")

    # Affichage des groupes
    for gname, gr in rep.groups.items():
        print(f"Groupe {gname}: {gr.members} (avantage total={gr.avantage():.2f})")

    return rep.groups


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 creer_groupes.py <NomDuGroupe> (ex: 2B)")
        return

    nom_groupe = sys.argv[1]
    print(f"Création des groupes optimisés pour le groupe {nom_groupe}...\n")

    promo = load_groups('Groupes SAÉ S3 -constitution.xlsx', 'Liste S3')
    if nom_groupe not in promo:
        print(f"Groupe {nom_groupe} introuvable dans le fichier Excel.")
        return

    creer_groupes_glouton(promo[nom_groupe], nb_groupes=3)


if __name__ == '__main__':
    main()