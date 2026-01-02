import sys
import time
from xlsx_loader import load_groups
from glouton import creer_groupes_glouton

""" Script pour créer des groupes optimisés à partir d'un fichier Excel. """
def afficher_repartition(rep: dict, truncate_membres=None) -> None:
    # Affiche la répartition des groupes dans un format tabulaire
    rows = []
    for nom, gr in sorted(rep.items(), key=lambda kv: str(kv[0])):
        membres = getattr(gr, "members", [])
        if hasattr(gr, "avantage_total") and callable(getattr(gr, "avantage_total")):
            avantage_total = gr.avantage_total()
        else:
            avantage_total = sum((getattr(e, "avantage", 0) or 0) for e in membres)

        def fmt_membre(e):
            prenom = getattr(e, "prenom", "") or str(e)
            leader = getattr(e, "leader", False)
            pol = getattr(e, "polarite", None)
            pol_str = "None" if pol is None else str(pol)
            return f"{prenom} {leader} {pol_str}"

        members_str = "<[" + ", ".join(fmt_membre(e) for e in membres) + "]>"
        if truncate_membres and len(members_str) > truncate_membres:
            members_str = members_str[:truncate_membres - 1] + "…"

        rows.append([str(nom), f"{avantage_total:.2f}", members_str])

    # Calcule la largeur de chaque colonne
    headers = ["Groupe", "Avantage total", "Membres"]
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if len(cell) > widths[i]:
                widths[i] = len(cell)

    # Affiche le tableau
    print("| " + " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    for row in rows:
        print("| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) + " |")
    
def main():
    # Vérifie les arguments de la ligne de commande
    if len(sys.argv) < 2:
        print("Usage: python3 creer_groupes.py <NomDuGroupe> (ex: 2B)")
        return

    nom_groupe = sys.argv[1]
    print(f"Création des groupes optimisés pour le groupe {nom_groupe}...\n")

    # Charger les données depuis le fichier Excel
    promo = load_groups('Groupes SAÉ S3 -constitution.xlsx', 'Liste S3')
    if nom_groupe not in promo:
        print(f"Groupe {nom_groupe} introuvable dans le fichier Excel.")
        return

    # Créer les groupes optimisés
    rep = creer_groupes_glouton(promo[nom_groupe], nb_groupes=3)
    # Afficher la répartition des groupes
    afficher_repartition(rep)
    

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(f"\n⏱ Temps d'exécution : {end - start:.3f} secondes")