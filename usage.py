"""
Helper functions for usage impact analysis and parameter selections.

Usage logic:

D : durée d'usage minimum (extraite des données en mois)
DR : durée réelle d'usage (durée du projet)

Si D = DR on est neutre curseur au milieu
Si DR > D On est vert c'est top (DR plsu de 2 ans c'est le + vert)
Si DR < D On est rouge c'est nul (DR moins de 3 mois c'est le + rouge )
"""

import re

# ---------------------------------------------------------------------------
# Listes des options et critères pour le questionnaire d'usage
# (à retrouver dans n'importe quel onglet usage)
# ---------------------------------------------------------------------------

r_list = [
    "Reconception",
    "Réduire / refuser",
    "Réutilisation",
    "Réparation",
    "Récupération",
    "Recycler",
    "Rendre à la Terre",
]

r_list_eol = [
    "Reconception pour un autre projet",
    "Recyclage",
    "Récupéré par un tiers",
    "Réutilisé",
    "Composté",
]

no_r_list_eol = [
    "❌ Jeté",
    "❌ Je ne sais pas",
]


ecopense_dict = {
    "En stock seconde main": 1,
    "Pour plusieurs projets": 2,
    "Critères techniques": 3,
    "En milieu de projet par habitude": 4,
    "Esthétisme green": 5,
    "Prix": 6,
    "Recyclable / réutilisable": 7,
}

local_dict = {
    "Production locale réemploi": 1,
    "Production locale neuve": 2,
    "Artisanat": 3,
    "Revendeur régional": 4,
    "Revendeur national": 5,
    "Revendeur europe et monde": 6,
}

knowledge_dict = {
    "Échange en début de projet (avant choix MOE)": 1,
    "Échange après choix MOE": 2,
    "Pas d’échange avant choix fournisseur (procédure classique AO)": 3,
    "Pas d’échange après choix (liste de course)": 4,
    "Pas de demande de RETEX aux fournisseurs ou a des experts": 5,
}

lifespan_dict = {
    "6 mois": 1,
    "1 an": 2,
    "Moins de 5 ans": 3,
    "Plus de 5 ans": 4,
    "Moins de 10 ans": 5,
    "Plus de 10 ans": 6,
}


def _in_months(value: int, unit: str) -> int:
    return value if "mois" in unit else value * 12


def extract_lifespan(text: str):
    """Renvoie une liste de tuples (duree_en_mois, qualificatif).
    qualificatif ∈ {"plus", "moins", "exact"}"""
    t = text.lower()
    durees = []

    # "plus de X (mois|an|ans)"
    for m in re.finditer(r"plus de\s+(\d+)\s*(mois|ans?)", t):
        durees.append((_in_months(int(m.group(1)), m.group(2)), "plus"))

    # "moins de X (mois|an|ans)"
    for m in re.finditer(r"moins de\s+(\d+)\s*(mois|ans?)", t):
        durees.append((_in_months(int(m.group(1)), m.group(2)), "moins"))

    # "X à Y (mois|ans)" -> on retient Y comme borne haute (qualificatif "moins")
    for m in re.finditer(r"(\d+)\s*à\s*(\d+)\s*(mois|ans?)", t):
        durees.append((_in_months(int(m.group(2)), m.group(3)), "moins"))

    # Nombre seul ex: "5 ans" -> on retire d'abord ce qui a déjà été capté plus haut
    t_restant = re.sub(r"plus de\s+\d+\s*(mois|ans?)", "", t)
    t_restant = re.sub(r"moins de\s+\d+\s*(mois|ans?)", "", t_restant)
    t_restant = re.sub(r"\d+\s*à\s*\d+\s*(mois|ans?)", "", t_restant)
    for m in re.finditer(r"(\d+)\s*(mois|ans?)", t_restant):
        durees.append((_in_months(int(m.group(1)), m.group(2)), "exact"))

    return durees


def get_lifespan_category(text: str) -> str:
    """Renvoie uniquement le critère (str), ou "Non catégorisé" si aucune durée détectée."""
    durees = extract_lifespan(text)
    if not durees:
        durees = [[120, "plus"]]

    # on garde la durée la plus longue mentionnée dans la cellule
    mois, qualif = max(durees, key=lambda d: d[0])

    label = "Plus de 10 ans"

    if mois <= 6:
        label = "6 mois"
    elif mois <= 12:
        label = "1 an"
    elif mois < 60:
        label = "Moins de 5 ans"
    elif mois == 60:
        label = "Moins de 5 ans" if qualif == "moins" else "Plus de 5 ans"
    elif mois < 120:
        label = "Plus de 5 ans"
    elif mois == 120:
        label = "Moins de 10 ans" if qualif == "moins" else "Plus de 10 ans"

    return mois, label
