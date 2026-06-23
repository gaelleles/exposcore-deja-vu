import streamlit as st
import etl
import analysis
from usage import (
    r_list,
    ecopense_dict,
    local_dict,
    knowledge_dict,
    get_lifespan_category,
    lifespan_dict,
)

st.set_page_config(page_title="ExpoScore", layout="wide")

# ---------------------------------------------------------------------------
# Sidebar : DONNÉES UTILISATEUR
# ---------------------------------------------------------------------------
st.sidebar.subheader("📝 Sélectionnez un matériau")

share_url = st.secrets.get("NEXTCLOUD_SHARE_URL", "")

if share_url:
    try:
        with st.spinner("Importation des données d'impact..."):
            etl.etl_pipeline(share_url)
    except Exception as e:
        st.sidebar.error(f"Erreur de connexion Nextcloud : {e}")

materials = analysis.get_materials()

# ---------------------------------------------------------------------------
# Sidebar : DONNÉES MATÉRIAUX
# ---------------------------------------------------------------------------

selected = st.sidebar.selectbox(
    "Sélectionnez un matériau",
    index=2,
    options=materials,
)

mass = st.sidebar.number_input(
    "Poids du matériau (kg)", min_value=0.0, value=1.0, step=0.01, format="%.2f"
)

if not selected:
    st.warning("Sélectionnez au moins un matériau.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar : DONNÉES USAGE
# ---------------------------------------------------------------------------
st.sidebar.subheader("⚡ Vos données d'usage")

with st.sidebar.form("questionnaire_usage"):
    # Eco-conception en fin de vie
    grave_selection = st.multiselect(
        "Quels principes avez-vous utilisés pour la **fin de vie** de ce matériau ?",
        r_list,
    )

    # Respect des 7R en sourcing du matériau
    sourcing_selection = st.multiselect(
        "Quels principes avez-vous utilisés pour le **sourcing** de ce matériau ?",
        r_list,
    )

    # Eco-pensé au début ou à la fin
    ecopense_selection = st.selectbox(
        "Pour quelles raisons avez-vous choisi ce matériau ?",
        list(ecopense_dict.keys()),
        index=None,
    )

    # Impact local ( sourçage, répartition des richesses…)
    local_selection = st.selectbox(
        "D'où provient ce matériau ?",
        list(local_dict.keys()),
        index=None,
    )

    # Échange avec sachant sur les questions écologiques
    knowledge_selection = st.selectbox(
        "Avez-vous échangé avec un·e expert·e sur les questions écologiques ?",
        list(knowledge_dict.keys()),
        index=None,
    )

    submitted = st.form_submit_button("✅ Valider les données d'usage")

# ---------------------------------------------------------------------------
# MAIN APP : AFFICHAGE DES DONNÉES D'IMPACT
# ---------------------------------------------------------------------------

st.title("🖼️ ExpoScore")
st.subheader(
    "Analyse d'impact des matériaux utilisés en exposition, par l'association Déjà-Vu"
)


tab1, tab2, tab3 = st.tabs(
    ["🌱 Impact écologique", "👥 Impact social", "⚡ Impact d'usage"]
)

# ---------------------------------------------------------------------------
# ONGLET IMPACT ÉCOLOGIQUE
# ---------------------------------------------------------------------------

with tab1:
    st.subheader("🌱 Impact écologique")
    df_eco = analysis.get_ecological_impact(selected)
    if df_eco.empty:
        st.info("Aucune donnée d'impact écologique disponible pour ce matériau.")
    else:
        df_eco = df_eco.rename(
            columns={
                "category": "Catégorie",
                "category_description": "Description",
                "value": "Données",
                "unit": "Unité",
                "comment": "Commentaire",
                "source": "Source",
                "year": "Année",
            }
        )
        df_eco["Données"] = (
            df_eco["Données"]
            .apply(analysis.convert_if_float)
            .apply(lambda x: x * mass if isinstance(x, (int, float)) else x)
        )
        df_eco = df_eco[
            [
                "Catégorie",
                "Données",
                "Unité",
                "Description",
                "Commentaire",
                "Source",
                "Année",
            ]
        ]
        st.dataframe(df_eco, width="content", hide_index=True)

# ---------------------------------------------------------------------------
# ONGLET IMPACT SOCIAL
# ---------------------------------------------------------------------------

with tab2:
    st.subheader("👥 Impact social")
    df_social = analysis.get_social_impact(selected)
    df_social = df_social.rename(
        columns={
            "category": "Catégorie",
            "value": "Score",
            "description": "Description",
            "source": "Source",
            "year": "Année",
        }
    )
    df_social["Score"] = df_social["Score"].apply(lambda x: str(x).strip().capitalize())
    df_social["Score visuel"] = (
        df_social["Score"]
        .str.strip()
        .apply(str.lower)
        .replace("oui", "1")
        .replace("non", "10")
        .replace("possible", "5")
        .apply(int)
    )
    df_social = df_social[
        ["Catégorie", "Score", "Score visuel", "Description", "Source", "Année"]
    ]
    st.dataframe(
        df_social,
        column_config={
            "Score visuel": st.column_config.ProgressColumn(
                "Score visuel",
                min_value=0,
                max_value=10,
                format="%d",
                color="auto",
            )
        },
        width="content",
        hide_index=True,
    )
    st.info(
        "Le score d'impact social est calculé sur une échelle de 1 à 10 (1 étant le pire, 10 le meilleur)."
    )

# ---------------------------------------------------------------------------
# ONGLET IMPACT D'USAGE
# ---------------------------------------------------------------------------

with tab3:
    st.subheader("⚡ Impact d'usage")
    st.caption(
        "L'impact d'usage est calculé en fonction de la durabilité du matériau (Durée d'usage) et des réponses au questionnaire d'usage à gauche de votre écran."
    )

    # On n'affiche l'onglet usage que si toutes les questions ont été remplies

    if submitted:
        usage_responses = [
            grave_selection,
            sourcing_selection,
            ecopense_selection,
            local_selection,
            knowledge_selection,
        ]

        if all(r is not None for r in usage_responses):
            # Calcul des scores selon les réponses aux questions

            grave_score = (
                len(grave_selection) + 1
            )  # Allows for the score to show up even if 0
            grave_pct = grave_score / (len(r_list) + 1)

            sourcing_score = len(sourcing_selection) + 1
            sourcing_pct = sourcing_score / (len(r_list) + 1)

            ecopense_score = ecopense_dict[ecopense_selection]
            ecopense_pct = ecopense_score / len(ecopense_dict)

            local_score = local_dict[local_selection]
            local_pct = local_score / len(local_dict)

            knowledge_score = knowledge_dict[knowledge_selection]
            knowledge_pct = knowledge_score / len(knowledge_dict)

            # Dictionnaire des scores d'usage pour calcul du score final

            usage_scores = {
                "Eco-conception en fin de vie": grave_pct,
                "Respect des 7R en sourcing du matériau": sourcing_pct,
                "Eco-pensé au début ou à la fin": ecopense_pct,
                "Impact local ( sourçage, répartition des richesses…)": local_pct,
                "Échange avec sachant sur les questions écologiques": knowledge_pct,
            }

            usage_selections = {
                "Eco-conception en fin de vie": grave_selection,
                "Respect des 7R en sourcing du matériau": sourcing_selection,
                "Eco-pensé au début ou à la fin": ecopense_selection,
                "Impact local ( sourçage, répartition des richesses…)": local_selection,
                "Échange avec sachant sur les questions écologiques": knowledge_selection,
            }

            # Récupération des données d'usage (notamment pour la durée du matériau)

            df_usage = analysis.get_usage_impact(selected)

            lifespan_description = df_usage.loc[
                df_usage["category"] == "Durée d’usage adapté au matériau",
                "description",
            ].values[0]
            lifespan_category = get_lifespan_category(lifespan_description)
            lifespan_score = lifespan_dict[lifespan_category] / len(lifespan_dict)

            usage_selections["Durée d’usage adapté au matériau"] = lifespan_description
            usage_scores["Durée d’usage adapté au matériau"] = lifespan_score

            # Ajuster les scores à 10 pour une meilleure visualisation, normalisée avec les scores d'impact social
            usage_scores = {k: v * 10 for k, v in usage_scores.items()}

            df_usage["details"] = df_usage["category"].apply(
                lambda x: str(usage_selections.get(x, ""))
            )

            df_usage["Score"] = df_usage["category"].apply(
                lambda x: usage_scores.get(x, 0)
            )

            df_usage.loc[
                df_usage["category"].isin(
                    [
                        "Eco-conception en fin de vie",
                        "Respect des 7R en sourcing du matériau",
                    ]
                ),
                "details",
            ] = df_usage.loc[
                df_usage["category"].isin(
                    [
                        "Eco-conception en fin de vie",
                        "Respect des 7R en sourcing du matériau",
                    ]
                ),
                "details",
            ].apply(
                lambda x: "Aucun 7R sélectionné" if x == "[]" else x
            )  # Clean empty lists for 7R criterion

            df_usage = df_usage[
                ["category", "Score", "details", "source", "year"]
            ].rename(
                columns={
                    "category": "Catégorie",
                    "details": "Détails",
                    "source": "Source",
                    "year": "Année",
                }
            )

            st.dataframe(
                df_usage,
                column_config={
                    "Score": st.column_config.ProgressColumn(
                        "Score",
                        min_value=0,
                        max_value=10,
                        format="%d",
                        color="auto",
                    )
                },
                width="content",
                hide_index=True,
            )

        else:
            st.info(
                '👉 Répondez à toutes les questions dans "Vos données d\'usage" et validez le questionnaire à nouveau pour voir les résultats.'
            )

    else:
        st.info(
            "👉 Veuillez appuyer sur le bouton Valider en bas du questionnaire d'usage pour voir les résultats."
        )
