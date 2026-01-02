# Groupe_QualAlgo
# Projet groupe (Qualité algo S5)
Cette application génère des groupes en fonction de contraintes.
Récupérez le code source, exécutez les commandes :
- python3 creer_groupes.py 1A
- python3 creer_groupes.py 2B

## Consigne 
Trouvez une nouvelle approche pour générer les meilleurs groupes projet possible du groupe de TD 2B.

Vous pouvez adapter le jeu de données pour voir comment votre algorithme évolue

## Attendu 
- Vous déposerez le ou les fichiers .py ou java correspondant à votre code utile sur Moodle.
- Vous rédigerez un compte rendu au format PDF décrivant :
    1. Succinctement, la description de votre projet,
    2. Les problèmes potentiels que vous identifiez dans votre projet,
    3. Les corrections que vous proposez pour améliorer votre algorithme,
    4. Un benchmark avant / après de votre code (cf TD1) avec différents jeux de données, et d’éventuels éléments comparatifs (complexités algorithmique, temporelle, spatiale, cyclomatique, etc…). Des graphes seront appréciés.

# Student Group Optimizer

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![OpenPyXL](https://img.shields.io/badge/Library-OpenPyXL-green?style=for-the-badge)

Ce projet est un outil de répartition automatique d'étudiants dans des groupes de projet (type SAÉ). L'objectif est de créer des groupes équilibrés et cohérents à partir d'un export Excel de promotion, en automatisant ce qui est habituellement une tâche manuelle complexe.

## Fonctionnalités

- **Extraction de données** : Chargement fluide depuis des fichiers `.xlsx` avec parsing dynamique des colonnes.
- **Algorithme Glouton** : Répartition intelligente basée sur plusieurs critères :
  - **Équilibrage du niveau** : Calcule la somme des "avantages" (compétences) pour que chaque groupe soit d'un niveau homogène.
  - **Gestion des leaders** : Assure la présence systématique d'un chef d'équipe par groupe.
  - **Contraintes de polarité** : Système d'exclusion pour séparer automatiquement les étudiants ne devant pas être dans le même groupe.
- **Validation & Logs** : Détection des impossibilités logiques (ex: pas assez de leaders) et affichage d'un score d'optimalité.


## Structure du Projet

* `creer_groupes.py` : Point d'entrée principal du script.
* `glouton.py` : Logique de l'algorithme de répartition.
* `xlsx_loader.py` : Module de lecture et de conversion du fichier Excel.
* `models.py` : Définition des objets métiers (`Etudiant`, `GroupeProjet`, `Repartition`).
* `grouping.py` : Classes de base pour la gestion générique des groupes.

## Installation & Usage

1. **Cloner le dépôt** :
   ```bash
   git clone [https://github.com/TON_PSEUDO/student-group-optimizer.git](https://github.com/TON_PSEUDO/student-group-optimizer.git)
   cd student-group-optimizer
