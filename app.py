import streamlit as st
import pandas as pd
import numpy as np
import etl
import analysis

st.set_page_config(page_title="ExpoScore", layout="wide")

# ---------------------------------------------------------------------------
# Sidebar : ETL - synchronisation Nextcloud (lien de partage public)
# ---------------------------------------------------------------------------
st.sidebar.title("📝 Vos données")

share_url = st.secrets.get("NEXTCLOUD_SHARE_URL", "")

if share_url:
    try:
        with st.spinner("Importation des données d'impact..."):
            etl.etl_pipeline(share_url)
    except Exception as e:
        st.sidebar.error(f"Erreur de connexion Nextcloud : {e}")

materials = analysis.get_materials()

selected = st.sidebar.selectbox(
    "Sélectionnez un matériau",
    options=materials,
)

mass = st.sidebar.number_input(
    "Poids du matériau (kg)",
    min_value=0.0,
    value=1.0,
    step=0.01,
    format="%.2f"
)

if not selected:
    st.warning("Sélectionnez au moins un matériau.")
    st.stop()

st.sidebar.header("⚡ Vos données d'usage")

# Eco-conception en fin de vie
ecoconception = st.sidebar.selectbox(
    "Eco-conception en fin de vie",
    [
        "Reconception",
        "Réduire / refuser",
        "Réutilisation",
        "Réparation",
        "Récupération",
        "Recycler",
        "Rendre à la Terre"
    ]
)

score_ecoconception = {
    "Reconception": 1,
    "Réduire / refuser": 1,
    "Réutilisation": 2,
    "Réparation": 3,
    "Récupération": 4,
    "Recycler": 5,
    "Rendre à la Terre": 6
}[ecoconception]

# Eco-pensé au début ou à la fin

ecopense = st.sidebar.selectbox(
    "Matériau ajouté car",
    [
        "En stock seconde main",
        "Pour plusieurs projets",
        "Critères techniques",
        "En milieu de projet par habitude",
        "Esthétisme green",
        "Prix",
        "Recyclable / réutilisable"
    ]
)

score_ecopense = {
    "En stock seconde main": 1,
    "Pour plusieurs projets": 2,
    "Critères techniques": 2,
    "En milieu de projet par habitude": 4,
    "Esthétisme green": 5,
    "Prix": 6,
    "Recyclable / réutilisable": 7
}[ecopense]

st.title("🖼️ ExpoScore")
st.subheader("Analyse d'impact des matériaux utilisés en exposition, par l'association Déjà-Vu")


tab1, tab2, tab3 = st.tabs(["🌱 Impact écologique", "👥 Impact social", "⚡ Impact d'usage"])

with tab1:
    st.subheader("🌱 Impact écologique")
    df_eco = analysis.get_ecological_impact(selected)
    if df_eco.empty:
        st.info("Aucune donnée d'impact écologique disponible pour ce matériau.")
    else:
        df_eco = df_eco.rename(columns={
            "category": "Catégorie",
            "category_description": "Description",
            "value": "Données",
            "unit": "Unité",
            "comment": "Commentaire",
            "source": "Source",
            "year": "Année"
        })
        df_eco["Données"] = df_eco["Données"].apply(analysis.convert_if_float).apply(
                lambda x: x * mass if isinstance(x, (int, float)) else x
            )
        st.dataframe(df_eco, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("👥 Impact social")
    df_social = analysis.get_social_impact(selected)
    df_social = df_social.rename(columns={
        "category": "Catégorie",
        "value": "Score",
        "description": "Description",
        "source": "Source",
        "year": "Année"
    })
    df_social["Score"] = df_social["Score"].apply(lambda x: str(x).strip().capitalize())
    df_social["Score visuel"] = df_social["Score"].str.strip().apply(str.lower).replace("oui", "1").replace("non", "10").replace("possible", "5").apply(int)
    df_social = df_social[[
        "Catégorie",
        "Score",
        "Score visuel",
        "Description",
        "Source",
        "Année"
    ]]
    st.dataframe(df_social, 
                     column_config={
        "Score visuel": st.column_config.ProgressColumn(
            "Score visuel",
            min_value=0,
            max_value=10,
            format="%d",
            color="auto",
        )
    },
    use_container_width=True, hide_index=True)
    st.info("Le score d'impact social est calculé sur une échelle de 1 à 10 (1 étant le pire, 10 le meilleur).")

with tab3:
    st.subheader("⚡ Impact d'usage")
    df_usage = analysis.get_usage_impact(selected)
    st.dataframe(df_usage, use_container_width=True, hide_index=True)



# # ---------------------------------------------------------------------------
# # Sélection des matériaux à comparer
# # ---------------------------------------------------------------------------

# pivot, units = etl.get_comparison_table()
# pivot = pivot[selected]

# # ---------------------------------------------------------------------------
# # Tableau de comparaison
# # ---------------------------------------------------------------------------
# st.subheader("Tableau comparatif")

# display_df = pivot.copy()
# display_df.insert(0, "Unité", [units.get(c, "") for c in display_df.index])
# display_df.index.name = "Critère"
# st.dataframe(display_df, use_container_width=True)

# # ---------------------------------------------------------------------------
# # Graphiques par critère (un par catégorie écologique)
# # ---------------------------------------------------------------------------
# st.subheader("Comparaison par critère")

# for critere in pivot.index:
#     col1, col2 = st.columns([3, 1])
#     with col1:
#         chart_df = pivot.loc[[critere]].T
#         chart_df.columns = [critere]
#         st.bar_chart(chart_df)
#     with col2:
#         st.markdown(f"**{critere}**")
#         st.caption(f"Unité : {units.get(critere, '—')}")

# st.markdown(
#     """
#     <div style="background:#f2c9c9; border:1px solid #b56b6b; padding:10px; margin-top:10px;">
#     ⚠️ Pas d'éléments pour "comparer" ou donner un score à ces calculs — comparaison limitée aux valeurs brutes.
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

# # ---------------------------------------------------------------------------
# # Détails par matériau
# # ---------------------------------------------------------------------------
# st.subheader("Détails par matériau")
# tabs = st.tabs(selected)
# for tab, materiau in zip(tabs, selected):
#     with tab:
#         df_detail = etl.get_ecological_impact(materiau)
#         st.dataframe(
#             df_detail[["critere", "valeur", "unite", "description", "source", "annee"]],
#             use_container_width=True,
#             hide_index=True,
#         )
