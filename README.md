# Exposcore

ExpoScore est une petite application web (faite avec un outil appelé Streamlit) créée par l'association Déjà-Vu. Elle permet de :

- Choisir un matériau utilisé en exposition (PVC, carton, Aquapaper, etc.)
- Indiquer son poids et répondre à quelques questions sur la façon dont il a été utilisé (sourcing, fin de vie, durée de vie...)
- Voir s'afficher son impact écologique, social et d'usage, sous forme de tableaux clairs.

Déployée gratuitement sur Streamlit Community.

Plus d'informations sur le projet dans `project.md`.

## Structure du projet

L'application récupère des fichiers Excel d'analyse d'impact produits par l'association Déjà-Vu, par le biais d'un lien NextCloud.
**Attention** : le fonctionnement de l'application repose sur le fait que les catégories, colonnes, et la structure des fichiers ne change pas.

Les données sont lues et intégrées dans une base SQLite à l'aide des fonctions dans le fichier `etl.py`. Les fonctions pour lire les fichiers de NextCloud sont dans `nextcloud.py`.

Elles sont ensuite mises en forme (à l'aide d'`analysis.py`) pour produire un dashboard d'analyse d'impact, développé dans `app.py` (fichier principal). En entrée, vous pouvez sélectionner un matériau et un poids, les données et les scores s'actualisent automatiquement.

L'onglet d'usage dépend aussi en partie du questionnaire à gauche. Les calculs sont aidés de l'onglet `usage.py`.

```
Fichiers Excel (1 par matériau, stockés sur Nextcloud)
        │
        ▼
  nextcloud.py   →  va chercher les fichiers Excel sur le cloud
        │
        ▼
     etl.py      →  nettoie les données et les range dans une base
        │              (le "ETL" = Extract, Transform, Load)
        ▼
  exposcore.db   →  une base de données locale (SQLite), créée
                     automatiquement à chaque lancement
        │
        ▼
  analysis.py    →  va piocher dans cette base les infos demandées
        │
        ▼
  usage.py       →  fournit les listes de réponses du questionnaire
        │              (ex : "Plus de 5 ans", "Réparation"...)
        ▼
     app.py      →  affiche tout ça dans l'interface (le site web)
```

Le fichier `params.py` contient les variables fixes du projet. @ Emie, si tu veux modifier le lien et le texte pour les 7R, tu as juste à aller sur ce fichier, appuyer sur edit, et changer le lien / le texte de `R_EXPLAIN`.

## 💻 Lancer l'application **en local** (sur votre ordinateur)

C'est la méthode à utiliser pour tester le projet ou pour développer dessus.

### Étape 1 — Installer les outils de base

- **Python 3.13** : [python.org](https://www.python.org/downloads/)
- **uv** (le gestionnaire utilisé par ce projet, plus simple et plus rapide que pip) : suivez les instructions sur [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### Étape 2 — Télécharger le projet

Ouvrez un terminal (l'application "Terminal" sur Mac/Linux, ou "PowerShell"/"Invite de commandes" sur Windows) et tapez :

```bash
git clone https://github.com/gaelleles/exposcore-deja-vu.git
cd exposcore-deja-vu
```

### Étape 3 — Installer les "ingrédients" du projet

```bash
uv sync
```

Cette commande lit `pyproject.toml` et `uv.lock`, installe automatiquement Python 3.13 si besoin, crée un environnement isolé, et installe toutes les bibliothèques nécessaires (Streamlit, pandas, etc.).

### Étape 4 — Configurer le lien secret

Créez un dossier `.streamlit` à la racine du projet, et un fichier `secrets.toml` dedans :

```bash
mkdir .streamlit
cp secrets.toml.example .streamlit/secrets.toml
```

Puis ouvrez `.streamlit/secrets.toml` avec un éditeur de texte et remplacez la valeur par le vrai lien Nextcloud fourni par Déjà-Vu.

### Étape 5 — Lancer l'application 🚀

```bash
uv run streamlit run app.py
```

Une page va automatiquement s'ouvrir dans votre navigateur, à l'adresse `http://localhost:8501`. Pour l'arrêter : retournez dans le terminal et faites `Ctrl + C`.

---

## ☁️ Lancer l'application **sans rien installer** (en ligne, pour la partager)

Si vous voulez que d'autres personnes puissent utiliser l'app sans installer quoi que ce soit, le plus simple est d'utiliser **Streamlit Community Cloud**, un service d'hébergement gratuit fait pour ce type d'application.

### Étape 1 — Avoir le projet sur GitHub

Si vous reprenez ce projet, vous pouvez tout à fait le cloner pour avoir tous les droits sur un repo. Ce code reste accessible en open source.

### Étape 2 — Créer un compte sur Streamlit Community Cloud

Rendez-vous sur [share.streamlit.io](https://share.streamlit.io) et connectez-vous avec votre compte GitHub.

### Étape 3 — Créer une nouvelle app

- Cliquez sur **"New app"**
- Choisissez votre dépôt / repo git
- Branche : `main`
- Fichier principal : `app.py`

### Étape 4 — Ajouter le lien secret

Dans les **"Advanced settings"** (paramètres avancés) avant de déployer, ou ensuite dans **Settings > Secrets**, collez le contenu de `secrets.toml.example` rempli avec le vrai lien :

```toml
NEXTCLOUD_SHARE_URL = "https://nuage.relief-aura.fr/s/VOTRE_TOKEN"
```

### Étape 5 — Déployer

Cliquez sur **"Deploy"**. Au bout de quelques minutes, vous obtenez une URL publique (du type `https://xxxxx.streamlit.app`) que vous pouvez partager avec qui vous voulez. L'application se reconstruit automatiquement à chaque fois que vous poussez du nouveau code sur GitHub.

## Comment ajouter des nouveaux fichiers ?

**Ajouter des fichiers** : pour ajouter des fichiers et des nouveaux matériaux, il faut update la liste MATERIALS_FILEPATH dans `etl.py`.
Rajouter une ligne de cette forme : `{"material": NOM_DE_MATERIAU, "filepath": DOSSIER_NUAGE/NOM_DE_FICHIER.XLSX},`

## CI/CD

J'ai utilisé `pre-commit` dans ce repo. Pour le lancer, installez pre-commit puis lancez : `pre-commit run --all-files`.
