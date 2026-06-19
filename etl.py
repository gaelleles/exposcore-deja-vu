"""
ETL : transforme les fichiers Excel sources (1 par matériau) en base SQLite.
On accède directement aux fichiers par nextcloud (nuage)
> On les télécharge via le lien de partage public (WebDAV) et on les lit avec pandas.
> On normalise les colonnes et on sélectionne les 3 types d'impact qui nous intéressent : écologique, social et usage.
> On les stocke dans une base SQLite locale (exposcore.db) pour pouvoir les interroger facilement (via pandas ou SQL).
"""

import io
import sqlite3
import pandas as pd
import warnings
from nextcloud import download_file

################################
# PARAMETERS
################################

DB_PATH = "exposcore.db"
MATERIALS_FILEPATH = [
    {"material": "PVC neuf", "filepath": "3222 - PVC/critères-tests-PVC-NEUF.xlsx"},
    {"material": "Carton", "filepath": "3223 - Carton /critères-tests-Carton.xlsx"},
    {"material": "Aquapaper", "filepath": "3224 - Aquapaper /critères-Aquapaper.xlsx"},
    {
        "material": "Adhésif mat pour découpe",
        "filepath": "3225 - Adhésif mat pour découpe /critères-adhésif-expr.xlsx",
    },
    {"material": "Jet Tex", "filepath": "3226 - Jet Tex/critères-Jet-Tex.xlsx"},
]

################################
# ETL PIPELINE
################################


def etl_pipeline(share_url):
    """
    Exécute le pipeline ETL pour extraire les données des fichiers Excel, les transformer et les charger dans la base de données SQLite.
    """
    data = []

    # Extract data from each material's Excel file and combine into a single DataFrame
    for mfp in MATERIALS_FILEPATH:
        data.append(read_material_sheets(share_url, mfp["filepath"], mfp["material"]))

    # Combine all data into a single DataFrame for each category
    df_eco = pd.DataFrame()
    df_social = pd.DataFrame()
    df_usage = pd.DataFrame()

    for d in data:
        if d["eco"] is not None:
            df_eco = pd.concat([df_eco, d["eco"]], ignore_index=True)
        df_social = pd.concat([df_social, d["social"]], ignore_index=True)
        df_usage = pd.concat([df_usage, d["usage"]], ignore_index=True)

    # Load into database
    conn = init_db(DB_PATH)

    load_eco_df_to_db(df_eco, conn)
    load_social_df_to_db(df_social, conn)
    load_usage_df_to_db(df_usage, conn)

    conn.close()


################################
# EXTRACT AND CLEAN DATA FROM EXCEL FILES
################################


def read_material_sheets(share_url, filepath, material_name: str):
    """Lit les 3 feuilles d'un fichier Excel (écologique, social, usage) et retourne un dict de DataFrames.
    filepath : chemin relatif dans le partage Nextcloud (ex: "3222 - PVC/critères-tests-PVC-NEUF.xlsx")
    material_name : nom du matériau (ex: "PVC neuf")
    """

    file_bytes_or_path = download_file(share_url, filepath)
    if isinstance(file_bytes_or_path, bytes):
        file_bytes_or_path = io.BytesIO(file_bytes_or_path)

    # Select sheet names
    file = pd.ExcelFile(file_bytes_or_path)
    sheet_names = file.sheet_names

    eco_sheet = [x for x in sheet_names if "comparaison" in x.lower()]
    social_sheet = [x for x in sheet_names if x.lower().startswith("sociaux")]
    usage_sheet = [x for x in sheet_names if x.lower().startswith("usage")]

    if eco_sheet:
        eco_sheet_name = eco_sheet[0]
        df_eco = file.parse(sheet_name=eco_sheet_name)
        # Normaliser les colonnes
        df_eco.columns = [
            "Catégorie",
            "Description de la catégorie",
            "Valeur",
            "Unité",
            "Commentaire",
            "Source",
            "Année",
        ]
        df_eco.insert(0, "Matériau", material_name)
    else:
        # Warning ici pour ne pas interrompre le processus, mais signaler que la feuille n'a pas été trouvée
        warnings.warn(
            f"Aucune feuille 'écologique pour comparaison' trouvée dans le fichier Excel. Fichier : {filepath}. Feuilles disponibles : {sheet_names}"
        )
        df_eco = None

    if social_sheet:
        social_sheet_name = social_sheet[0]
        df_social = file.parse(sheet_name=social_sheet_name, skiprows=1)
        df_social.columns = [
            "Catégorie",
            "Typologie",
            "Critère",
            "Unité",
            "Description",
            "Données",
            "Sources",
            "Année",
        ]
        df_social.insert(0, "Matériau", material_name)
    else:
        raise ValueError(
            f"Aucune feuille 'Impact sociaux' trouvée dans le fichier Excel. Fichier : {filepath}. Feuilles disponibles : {sheet_names}"
        )

    if usage_sheet:
        usage_sheet_name = usage_sheet[0]
        df_usage = file.parse(sheet_name=usage_sheet_name, skiprows=1)
        df_usage.columns = [
            "Catégorie",
            "Critère",
            "Unité",
            "Description",
            "Données",
            "Sources",
            "Année",
        ]
        df_usage.insert(0, "Matériau", material_name)
    else:
        raise ValueError(
            f"Aucune feuille 'Usage' trouvée dans le fichier Excel. Fichier : {filepath}. Feuilles disponibles : {sheet_names}"
        )

    return {"eco": df_eco, "social": df_social, "usage": df_usage}


################################
# LOAD INTO DATABASE SQLITE
################################


def init_db(db_path=DB_PATH):
    """Initialise la base SQLite (création des tables si elles n'existent pas) et retourne la connexion."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS impact_eco (
            material TEXT NOT NULL,
            category TEXT NOT NULL,
            category_description TEXT,
            value TEXT,
            unit TEXT,
            comment TEXT,
            source TEXT,
            year TEXT,
            PRIMARY KEY (material, category)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS impact_social (
            material TEXT NOT NULL,
            category TEXT NOT NULL,
            typology TEXT,
            criterion TEXT,
            unit TEXT,
            description TEXT,
            value TEXT, --données
            source TEXT,
            year TEXT,
            PRIMARY KEY (material, category)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS impact_usage (
            material TEXT NOT NULL,
            category TEXT NOT NULL,
            criterion TEXT,
            unit TEXT,
            description TEXT,
            value TEXT,
            source TEXT,
            year TEXT,
            PRIMARY KEY (material, category)
        );
    """)
    conn.commit()
    print(f"Base SQLite initialisée : {db_path}")
    return conn


def load_eco_df_to_db(df_eco, conn):
    cur = conn.cursor()
    for _, row in df_eco.iterrows():
        cur.execute(
            """
        INSERT INTO impact_eco (
            material,
            category,
            category_description,
            value,
            unit,
            comment,
            source,
            year
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(material, category) DO UPDATE SET
            category_description = excluded.category_description,
            value = excluded.value,
            unit = excluded.unit,
            comment = excluded.comment,
            source = excluded.source,
            year = excluded.year
        """,
            (
                str(row["Matériau"]).strip(),
                str(row["Catégorie"]).strip(),
                str(row["Description de la catégorie"])
                if pd.notna(row["Description de la catégorie"])
                else None,
                str(row["Valeur"]) if pd.notna(row["Valeur"]) else None,
                str(row["Unité"]) if pd.notna(row["Unité"]) else None,
                str(row["Commentaire"]) if pd.notna(row["Commentaire"]) else None,
                str(row["Source"]) if pd.notna(row["Source"]) else None,
                str(row["Année"]) if pd.notna(row["Année"]) else None,
            ),
        )
    conn.commit()
    print(f"Inséré {len(df_eco)} rows dans la table impact_eco")


def load_social_df_to_db(df_social, conn):
    cur = conn.cursor()
    for _, row in df_social.iterrows():
        cur.execute(
            """
            INSERT INTO impact_social (
                material,
                category,
                typology,
                criterion,
                unit,
                description,
                value,
                source,
                year
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(material, category) DO UPDATE SET
                typology = excluded.typology,
                criterion = excluded.criterion,
                unit = excluded.unit,
                description = excluded.description,
                value = excluded.value,
                source = excluded.source,
                year = excluded.year
        """,
            (
                str(row["Matériau"]).strip(),
                str(row["Catégorie"]).strip(),
                str(row["Typologie"]) if pd.notna(row["Typologie"]) else None,
                str(row["Critère"]) if pd.notna(row["Critère"]) else None,
                str(row["Unité"]) if pd.notna(row["Unité"]) else None,
                str(row["Description"]) if pd.notna(row["Description"]) else None,
                str(row["Données"]) if pd.notna(row["Données"]) else None,
                str(row["Sources"]) if pd.notna(row["Sources"]) else None,
                str(row["Année"]) if pd.notna(row["Année"]) else None,
            ),
        )

    conn.commit()
    print(f"Inséré {len(df_social)} rows dans la table impact_social")


def load_usage_df_to_db(df_usage, conn):
    cur = conn.cursor()
    for _, row in df_usage.iterrows():
        cur.execute(
            """
            INSERT INTO impact_usage (
                material,
                category,
                criterion,
                unit,
                description,
                value,
                source,
                year
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(material, category) DO UPDATE SET
                criterion = excluded.criterion,
                unit = excluded.unit,
                description = excluded.description,
                value = excluded.value,
                source = excluded.source,
                year = excluded.year
        """,
            (
                str(row["Matériau"]).strip(),
                str(row["Catégorie"]).strip(),
                str(row["Critère"]) if pd.notna(row["Critère"]) else None,
                str(row["Unité"]) if pd.notna(row["Unité"]) else None,
                str(row["Description"]) if pd.notna(row["Description"]) else None,
                str(row["Données"]) if pd.notna(row["Données"]) else None,
                str(row["Sources"]) if pd.notna(row["Sources"]) else None,
                str(row["Année"]) if pd.notna(row["Année"]) else None,
            ),
        )

    conn.commit()
    print(f"Inséré {len(df_usage)} rows dans la table impact_usage")
