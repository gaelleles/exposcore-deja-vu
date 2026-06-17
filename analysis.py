import pandas as pd
import sqlite3
from etl import DB_PATH

################################
# ANALYSE / REQUETAGE DE LA BASE
################################

def connect_db(db_path=DB_PATH):
    """Connexion à la base SQLite."""
    conn = sqlite3.connect(db_path)
    return conn

def convert_if_float(x):
    x_str = str(x).replace(",", ".").strip()
    try:
        return float(x_str)
    except:
        return x

def get_materials(db_path=DB_PATH):
    conn = connect_db(db_path)
    materials = pd.read_sql(
        "SELECT DISTINCT material FROM impact_social ORDER BY material", conn
    )["material"].tolist()
    conn.close()
    return materials

def get_ecological_impact(material, db_path=DB_PATH):
    conn = connect_db(db_path)
    df = pd.read_sql("""
        SELECT category, 
                category_description,
                CASE
                    WHEN REPLACE(value, ',', '.') GLOB '-?[0-9]*'
                    OR REPLACE(value, ',', '.') GLOB '-?[0-9]*.[0-9]*'
                    THEN CAST(REPLACE(value, ',', '.') AS REAL)
                    ELSE value
                END value, 
                SUBSTR(unit, 1, INSTR(unit, '/') - 1) unit, 
                comment,
                source, 
                year
        FROM impact_eco WHERE material=? ORDER BY category
        """,
        conn,
        params=(material,),
    )
    conn.close()
    return df

def get_social_impact(material, db_path=DB_PATH):
    conn = connect_db(db_path)
    df = pd.read_sql("""
        SELECT category,
            value,
            description,
            source,
            year
        FROM impact_social WHERE material=? ORDER BY category
        """,
        conn,
        params=(material,),
    )
    conn.close()
    return df

def get_usage_impact(material, db_path=DB_PATH):
    conn = connect_db(db_path)
    df = pd.read_sql("""
        SELECT category,
                criterion,
                description,
                source,
                year
        FROM impact_usage WHERE material=? ORDER BY category
        """,
        conn,
        params=(material,),
    )
    conn.close()
    return df


def get_comparison_table(db_path=DB_PATH):
    """Tableau pivot : critères en lignes, matériaux en colonnes (valeurs brutes)."""
    conn = connect_db(db_path)
    df = pd.read_sql("SELECT materiau, critere, valeur, unite FROM impact_eco", conn)
    conn.close()
    if df.empty:
        return df, {}
    units = df.groupby("critere")["unite"].first().to_dict()
    pivot = df.pivot(index="critere", columns="materiau", values="valeur")
    return pivot, units