from typing import Dict
from openpyxl import load_workbook
from models import Etudiant, GroupeTP

class Row(object):

    def __init__(self, head, row):
        self.head = head
        self.row = row

    def __getitem__(self, item):
        for i, c in enumerate(self.head):
            if c.value == item:
                return self.row[i].value
        raise KeyError(item)

""" Charge les groupes et étudiants depuis un fichier Excel. """
def load_groups(filename, sheet) -> Dict:
    # Charger le fichier Excel en mode lecture seule
    wb = load_workbook(filename=filename, data_only=True, read_only=True)
    # Sélectionner la feuille spécifiée
    sh = wb[sheet]
    # Lire l'en-tête et les lignes de données
    head, *rows = sh.rows
    res = {}
    # Parcourir chaque ligne et créer les objets correspondants
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

