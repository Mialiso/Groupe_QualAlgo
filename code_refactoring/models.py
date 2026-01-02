
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Iterable
from partition import BoundedGroup

# -----------------------------
# Modèles
# -----------------------------
@dataclass(order=True)
class Etudiant:
    nom: str
    prenom: str
    avantage: float = 0.0
    leader: bool = False
    polarite: Optional[int] = None

    def display(self) -> str:
        tag = " (L)" if self.leader else ""
        pol = f" [p{self.polarite}]" if self.polarite is not None else ""
        return f"{self.prenom} {self.nom}{tag}{pol} (adv={self.avantage:g})"


@dataclass
class GroupeTP:
    nom: str
    etudiants: List[Etudiant] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.etudiants)

    def repartition(self, nb_groupes: int) -> List[int]:
        """Retourne une liste de capacités équilibrées pour nb_groupes."""
        if nb_groupes <= 0:
            raise ValueError("Le nombre de groupes doit être > 0")
        n = len(self.etudiants)
        base, r = divmod(n, nb_groupes)
        return [base + 1 if i < r else base for i in range(nb_groupes)]


class GroupeProjet(BoundedGroup[Etudiant]):
    def avantage_total(self) -> float:
        return sum(e.avantage for e in self.members)

    def a_un_leader(self) -> bool:
        return any(e.leader for e in self.members)

    def _polarites(self) -> set[int]:
        return {e.polarite for e in self.members if e.polarite is not None}

    def can_accept(self, e: Etudiant) -> bool:
        if self.is_full():
            return False
        if e.polarite is not None and e.polarite in self._polarites():
            return False
        return True


@dataclass
class Repartition:
    groups: Dict[str, GroupeProjet]

    @classmethod
    def from_sizes(cls, sizes: Iterable[int]) -> "Repartition":
        d = {f"G{i+1}": GroupeProjet(name=f"G{i+1}", room=size) for i, size in enumerate(sizes)}
        return cls(groups=d)

    def tous_les_etudiants(self) -> List[Etudiant]:
        res: List[Etudiant] = []
        for g in self.groups.values():
            res.extend(g.members)
        return res
