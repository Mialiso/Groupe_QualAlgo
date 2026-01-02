
from __future__ import annotations
from typing import Dict, Optional
from openpyxl import load_workbook  # type: ignore
import unicodedata, re

from models import Etudiant, GroupeTP

def _norm(s: Optional[str]) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize('NFKD', str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower().strip().replace("«", "").replace("»", "").replace('"', "").replace("'", "")
    return re.sub(r"\s+", " ", s)

def load_groups(filename: str, sheet: str) -> Dict[str, GroupeTP]:
    """Charge tous les Groupes TP depuis un .xlsx et retourne un dict {nom: GroupeTP}."""
    wb = load_workbook(filename=filename, data_only=True, read_only=True)
    sh = wb[sheet]
    head, *rows = sh.rows
    col_index = {_norm(c.value): i for i, c in enumerate(head)}

    def get(row, col, default=None):
        i = col_index.get(_norm(col))
        if i is None:
            return default
        v = row[i].value
        return default if v in (None, "") else v

    groupes: Dict[str, GroupeTP] = {}
    for r in rows:
        nom_groupe = get(r, "Groupe")
        if not nom_groupe:
            continue
        groupe = groupes.setdefault(str(nom_groupe), GroupeTP(str(nom_groupe)))

        full = (get(r, "Prénom", "") or "").strip()
        nom_xlsx = (get(r, "Nom", "") or "").strip()
        nom_ok = nom_xlsx if nom_xlsx else (full.split()[-1] if full else "")
        prenom_ok = full.replace(nom_ok, "", 1).strip() or full

        is_leader = str(get(r, "« chef »") or get(r, "chef") or "").lower() in ("1", "true", "oui", "yes", "y")
        pol_raw = get(r, "À séparer")
        try:
            pol_ok = int(pol_raw) if pol_raw not in (None, "", "-") else None
        except (TypeError, ValueError):
            pol_ok = None

        try:
            avantage = float(get(r, "Avantage compté", 0) or 0)
        except (TypeError, ValueError):
            avantage = 0.0

        e = Etudiant(nom=nom_ok, prenom=prenom_ok, avantage=avantage, leader=is_leader, polarite=pol_ok)
        groupe.etudiants.append(e)

    return groupes

def load_groupe_tp(filename: str, sheet: str, nom_groupe: str) -> GroupeTP:
    d = load_groups(filename, sheet)
    if nom_groupe not in d:
        raise KeyError(f"Groupe {nom_groupe} introuvable dans {filename}/{sheet}")
    return d[nom_groupe]
