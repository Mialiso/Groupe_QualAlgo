#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark comparatif entre:
- Version "base" (exhaustive)  -> dossier: code_base/code_base
- Version "ref"  (glouton)     -> dossier: code_ref_Mi/code_ref_Mi

Sortie: report/benchmark_results.json

Usage (défauts OK si l'arborescence est intacte):
    python benchmark_both.py
ou avec chemins explicites:
    python benchmark_both.py --base ./code_base/code_base --ref ./code_ref_Mi/code_ref_Mi \
        --xlsx "Groupes SAÉ S3 -constitution.xlsx" --sheet "Liste S3" --timeout 60
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from collections import Counter


# ---------- Résultats ----------
@dataclass
class BenchmarkResult:
    scenario: str
    method: str              # "exhaustive" | "heuristic" | "exhaustive_timeout" | "exhaustive_error" | "heuristic_error"
    fairness: Optional[float]
    conflicts: Optional[int]
    duration_s: float
    iterations: Optional[int] = None
    attempts: Optional[int] = None
    note: Optional[str] = None

    def as_dict(self) -> Dict[str, object]:
        data = asdict(self)
        # Ne garder que les champs non nuls
        return {k: v for k, v in data.items() if v is not None}


# ---------- Utils communs ----------
def group_totals_and_conflicts(groups: Dict[object, object]) -> Tuple[float, int]:
    """Calcule (fairness, conflicts) de manière agnostique aux deux versions.

    fairness = (max total avantage) - (min total avantage)
    conflicts = nombre de groupes qui contiennent un doublon de polarité
    """
    totals: List[float] = []
    conflicts = 0
    for g in groups.values():
        members = getattr(g, "members", [])  # commun aux deux versions
        # Somme des avantages
        total = 0.0
        polarites: List[Optional[int]] = []
        for e in members:
            total += float(getattr(e, "avantage", 0.0))
            pol = getattr(e, "polarite", None)
            if pol is not None:
                polarites.append(pol)
        totals.append(total)
        # Conflits: doublon de polarité dans un groupe
        if len(polarites) != len(set(polarites)):
            conflicts += 1

    if not totals:
        return 0.0, conflicts
    fairness = max(totals) - min(totals)
    return fairness, conflicts


def build_subset(groupe, taille: int, nb_groupes: int):
    """Crée un sous-ensemble faisable (chaque polarité apparaît au plus nb_groupes fois)."""
    etudiants: List = []
    polarites = Counter()
    for etu in getattr(groupe, "etudiants", []):
        if len(etudiants) >= taille:
            break
        pol = getattr(etu, "polarite", None)
        if pol is not None and polarites[pol] >= nb_groupes:
            continue
        etudiants.append(etu)
        if pol is not None:
            polarites[pol] += 1
    # Le constructeur prend (nom, etudiants)
    GroupeTP_cls = type(groupe)
    return GroupeTP_cls(f"{getattr(groupe, 'nom', 'groupe')}-subset{len(etudiants)}", etudiants)


# ---------- Chargement des APIs des deux versions ----------
def load_base_api(base_root: Path):
    """Charge l'API de la version 'base' (exhaustive)."""
    students = SourceFileLoader("base_students", str(base_root / "students.py")).load_module()
    creer = SourceFileLoader("base_creer_groupes", str(base_root / "creer_groupes.py")).load_module()
    # grouping existe mais tout est déjà exposé côté students/creer
    return {
        "GroupeTP": students.GroupeTP,
        "Repartition": students.Repartition,
        "load_groups": creer.load_groups,
    }


def load_ref_api(ref_root: Path):
    """Charge l'API de la version 'ref' (glouton)."""
    models = SourceFileLoader("ref_models", str(ref_root / "models.py")).load_module()
    xlsx_loader = SourceFileLoader("ref_xlsx_loader", str(ref_root / "xlsx_loader.py")).load_module()
    glouton = SourceFileLoader("ref_glouton", str(ref_root / "glouton.py")).load_module()
    return {
        "GroupeTP": models.GroupeTP,
        "load_groups": xlsx_loader.load_groups,   # même signature (xlsx_path, sheet)
        "heuristic": glouton.creer_groupes_glouton,
    }


# ---------- Exécution d'un scénario ----------
def run_exhaustive(base_api, groupe, nb: int, timeout: Optional[int]) -> BenchmarkResult:
    """Version exhaustive (base). Utilise Repartition.faire → renvoie un dict de groupes."""
    start = time.perf_counter()
    try:
        if timeout is not None:
            # Timeout soft : on mesure et on laisse l'utilisateur gérer si ça dépasse
            pass
        groupes = base_api["Repartition"].faire(groupe, nb=nb)
        duration = time.perf_counter() - start
        if not groupes:
            return BenchmarkResult(
                scenario=getattr(groupe, "nom", "scenario"),
                method="exhaustive_error",
                fairness=None,
                conflicts=None,
                duration_s=duration,
                note="Aucune répartition trouvée (exhaustive)",
            )
        fairness, conflicts = group_totals_and_conflicts(groupes)
        return BenchmarkResult(
            scenario=getattr(groupe, "nom", "scenario"),
            method="exhaustive",
            fairness=round(fairness, 6),
            conflicts=int(conflicts),
            duration_s=duration,
        )
    except KeyboardInterrupt:
        # Si l'utilisateur stoppe manuellement
        duration = time.perf_counter() - start
        return BenchmarkResult(
            scenario=getattr(groupe, "nom", "scenario"),
            method="exhaustive_timeout",
            fairness=None,
            conflicts=None,
            duration_s=duration,
            note="Interrompu manuellement",
        )
    except Exception as e:
        duration = time.perf_counter() - start
        return BenchmarkResult(
            scenario=getattr(groupe, "nom", "scenario"),
            method="exhaustive_error",
            fairness=None,
            conflicts=None,
            duration_s=duration,
            note=f"{type(e).__name__}: {e}",
        )


def run_heuristic(ref_api, groupe, nb: int, attempts: Optional[int] = None) -> BenchmarkResult:
    """Version gloutonne (ref). Utilise creer_groupes_glouton → renvoie un dict de groupes."""
    start = time.perf_counter()
    try:
        # L'implémentation fournie n'accepte pas attempts/allow_conflicts
        groupes = ref_api["heuristic"](groupe, nb)
        duration = time.perf_counter() - start
        if not groupes:
            return BenchmarkResult(
                scenario=getattr(groupe, "nom", "scenario"),
                method="heuristic_error",
                fairness=None,
                conflicts=None,
                duration_s=duration,
                note="Aucune répartition retournée (heuristic)",
            )
        fairness, conflicts = group_totals_and_conflicts(groupes)
        return BenchmarkResult(
            scenario=getattr(groupe, "nom", "scenario"),
            method="heuristic",
            fairness=round(fairness, 6),
            conflicts=int(conflicts),
            duration_s=duration,
            attempts=attempts,
        )
    except Exception as e:
        duration = time.perf_counter() - start
        return BenchmarkResult(
            scenario=getattr(groupe, "nom", "scenario"),
            method="heuristic_error",
            fairness=None,
            conflicts=None,
            duration_s=duration,
            note=f"{type(e).__name__}: {e}",
        )


# ---------- Programme principal ----------
def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark helpers comparing exhaustive and heuristic group generation for both project versions.")
    parser.add_argument("--base", type=Path, default=Path("code_base") / "code_base", help="Chemin vers la racine de la version base")
    parser.add_argument("--ref", type=Path, default=Path("code_ref_Mi") / "code_ref_Mi", help="Chemin vers la racine de la version ref")
    parser.add_argument("--xlsx", type=Path, default=Path("Groupes SAÉ S3 -constitution.xlsx"), help="Fichier Excel des étudiants")
    parser.add_argument("--sheet", type=str, default="Liste S3", help="Nom de la feuille Excel")
    parser.add_argument("--timeout", type=int, default=None, help="Timeout doux (secondes) pour l'exhaustif (indicatif)")
    parser.add_argument("--output", type=Path, default=Path("report") / "benchmark_results.json", help="Fichier de sortie JSON")
    args = parser.parse_args()

    # Charger APIs
    base_api = load_base_api(args.base)
    ref_api = load_ref_api(args.ref)

    # Charger données — on tente d'abord à partir de --xlsx tel quel.
    xlsx_file = args.xlsx
    if not xlsx_file.exists():
        # Essais relatifs aux deux racines si besoin
        c1 = args.base / xlsx_file.name
        c2 = args.ref / xlsx_file.name
        if c1.exists():
            xlsx_file = c1
        elif c2.exists():
            xlsx_file = c2
        else:
            raise FileNotFoundError(f"Impossible de trouver le fichier Excel: {args.xlsx}")

    # Groupes depuis les deux versions (pour robustesse, on lit via la version 'ref' qui a un loader dédié)
    try:
        groupes_ref = ref_api["load_groups"](str(xlsx_file), args.sheet)
        groupes_base = base_api["load_groups"](str(xlsx_file), args.sheet)
    except Exception:
        # fallback : si un des loaders ne passe pas, on réutilise l'autre
        groupes_ref = ref_api["load_groups"](str(xlsx_file), args.sheet)
        groupes_base = groupes_ref

    results: List[BenchmarkResult] = []

    # -------- Scénario 1 : 1A, deux méthodes --------
    if "1A" in groupes_base:
        g1a_base = groupes_base["1A"]
        g1a_ref = groupes_ref["1A"]
        results.append(run_exhaustive(base_api, g1a_base, nb=3, timeout=args.timeout))
        results.append(run_heuristic(ref_api, g1a_ref, nb=3, attempts=None))

    # -------- Scénario 2 : 2B subset (12 étudiants), comparatif --------
    if "2B" in groupes_base:
        g2b_base = groupes_base["2B"]
        g2b_ref = groupes_ref["2B"]
        subset_base = build_subset(g2b_base, taille=12, nb_groupes=3)
        subset_ref = build_subset(g2b_ref, taille=12, nb_groupes=3)
        results.append(run_exhaustive(base_api, subset_base, nb=3, timeout=args.timeout))
        results.append(run_heuristic(ref_api, subset_ref, nb=3, attempts=None))

    # -------- Scénario 3 : 2B complet (heuristic only) --------
    if "2B" in groupes_ref:
        g2b_full = groupes_ref["2B"]
        r = run_heuristic(ref_api, g2b_full, nb=3, attempts=None)
        # On marque explicitement le scénario
        r.scenario = "2B_full"
        results.append(r)

    # Écriture
    out_path = args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump([r.as_dict() for r in results], fh, indent=2, ensure_ascii=False)

    # Affichage console
    print(f"\nRésultats ({out_path}):")
    for r in results:
        print(
            f"- {r.scenario:>12s} | {r.method:18s} | "
            f"fairness={r.fairness!s:>8s} | conflicts={r.conflicts!s:>4s} | "
            f"t={r.duration_s:.4f}s"
        )


if __name__ == "__main__":
    main()
