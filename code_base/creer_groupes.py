from operator import attrgetter
import time
from typing import Dict
import sys
import cProfile

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
            etudiant = Etudiant(nom=r['Prénom'].split()[-1],
                                prenom=r['Prénom'].split()[-1],
                                avantage=r['Avantage compté'],
                                leader=bool(r['« chef »']),
                                polarite=r['À séparer'])
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
    start = time.time() 
    promo = load_groups('Groupes SAÉ S3 -constitution.xlsx', 'Liste S3')
    calcul(promo[sys.argv[1]], 3)
    end = time.time()
    print(f"\n⏱ Temps d'exécution : {end - start:.3f} secondes")
    

    
