from operator import attrgetter
from typing import Dict
import sys

from students import GroupeTP, Etudiant, Repartition

from openpyxl import load_workbook

class Row(object):

    def __init__(self, head, row):
        self.head = head
        self.row = row

    def __getitem__(self, item):
        for i, c in enumerate(self.head):
            if c.value == item:
                return self.row[i].value
        raise KeyError(item)


def load_groups(filename, sheet) -> Dict:
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
            full = (r['Prénom'] or "").strip()
            nom_xlsx = (r.get('Nom') or "").strip() if hasattr(r, 'head') else ""
            nom_ok = nom_xlsx if nom_xlsx else (full.split()[-1] if full else "")
            prenom_ok = full.replace(nom_ok, "", 1).strip() or full

            # Normalisation du chef (bool) et de la polarité (int/None)
            is_leader = str(r['« chef »']).lower() in ("1","true","oui","yes","y")
            pol_raw = r['À séparer']
            try:
                pol_ok = int(pol_raw) if pol_raw not in (None, "", "-") else None
            except:
                pol_ok = None

            etudiant = Etudiant(nom=nom_ok,
                                prenom=prenom_ok,
                                avantage=float(r['Avantage compté'] or 0),
                                leader=is_leader,
                                polarite=pol_ok)
            groupe.etudiants.append(etudiant)

    return res


def calcul(g: GroupeTP, nb):
    print("Groupe :", g)
    opt = Repartition.faire(g, nb=nb)

    if not g:
        print("Pas de composition de groupe trouvée")
        return

    for g in opt:
        print("%d %s" % (g,opt[g].members))

if __name__ == '__main__':
    promo = load_groups('Groupes SAÉ S3 -constitution.xlsx', 'Liste S3')

    calcul(promo[sys.argv[1]], 3)
