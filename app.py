import streamlit as st
import etl
import analysis
from nextcloud import download_file
from usage import (
    r_list,
    r_list_eol,
    no_r_list_eol,
    ecopense_dict,
    local_dict,
    knowledge_dict,
    get_lifespan_category,
)


WEBSITE = "https://www.deja-vu-ass.fr/"
INTRO_TEXT = f"""
**👋 Bienvenue dans l’ExpoScore V0.2026 de Déjà-vu !**

Cet outil est la V0 d’une solution de visualisation des impacts écologiques et sociaux d’un projet (artistique, culturel, associatif, tournage...). Aujourd’hui principalement destiné au secteur des expositions, il a pour objectif de s’adresser à l’ensemble des projets culturels et artistiques dans un second temps.
Les données et la méthodologie ont été développées par les membres bénévoles de l’association [Déjà-Vu]({WEBSITE}) portée par Emie Baud. L'application a été codée par [Gaëlle Lescop](https://github.com/gaelleles) en 2026.
L’association Déjà-vu est une association à but non lucratif de vulgarisation scientifique dans le secteur des arts et de la culture afin de favoriser l’éco-conception des projets et de réduire le greenwashing, les fausses croyances et les impacts écologiques et sociaux de ces derniers.


**❓ À quoi vous sert l’ExpoScore V0.2026 ?**
L’outil vous permet de visualiser les impacts écologiques de vos matériaux, leurs impacts sociaux et enfin les impacts des usages que vous en ferez. L’ensemble de ces données vous aidera à mieux choisir les matériaux et comprendre les différents impacts. Il est pensé pour être utilisé à toutes les étapes des projets :
–	En amont pour vous aider à éco-concevoir (ce qui est le mieux, on n’éco-conçoit jamais en fin de projet).
–	Durant le projet pour visualiser les impacts.
–	En fin de projet comme retour d’expérience et d’amélioration.
Il s’agit d’un outil d’aide, pédagogique et en aucun cas d’un calculateur pouvant être utilisé à des fins marketing ou pouvant justifier d’un choix de matériau. Il vous aidera a affiner vos connaissances, connaître les impacts et les minimiser. Il est interdit de commercialiser cet outil.
Chaque projet étant unique, l’ExpoScore ne peut être un outil de choix de matériau mais bien un outil d’aide à la décision selon certains critères.
Les données seront mises à jour annuellement et de nouveaux matériaux seront disponibles à partir de 2027.


🌍 Pour un numérique libre, OpenSource et responsable, cette solution est sous la licence CC NC-SA-4.0, les données sont hébergées sur NextCloud, la solution de visualisation est sur Streamlit (outil de visualisation open source) et le code accessible sur GitHub.

📩 Utilisez-la ! Testez-la ! Bidouillez le code de votre côté pour permettre une amélioration commune et faites nous vos retours -> dejavu.asso@gmail.com 

🌱 *Rendons l’éphémère durable.*

"""

################################
# DL IMAGES FUNCTION
################################


# Moved the function here so caching is directly in the app
# This allows access to logo img + material pictures. For now material pictures are not used
@st.cache_data
def download_img(share_url):
    img_dict = {"Logo": download_file(share_url=share_url, path=etl.LOGO_FILEPATH)}
    for mat in etl.MATERIALS_FILEPATH:
        if mat["imagepath"] is not None:
            img_bytes = download_file(share_url=share_url, path=mat["imagepath"])
            img_dict[mat["material"]] = img_bytes
        else:
            img_dict[mat["material"]] = None
    return img_dict


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
            img_dict = download_img(share_url)
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
    st.markdown(
        "<span style='font-size:14px;'>🕘 Quelle est la **durée** de votre projet (hors étude et démontage, uniquement durée utilisateur/visiteur) ?</span>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        mois = st.number_input("Mois", min_value=0, max_value=12, value=0, step=1)

    with col2:
        annees = st.number_input("Années", min_value=0, value=0, step=1)

    project_length_months = mois + annees * 12

    no_r = ["❌ Aucun principe R appliqué"]

    # Respect des 7R en sourcing du matériau
    sourcing_selection = st.multiselect(
        "♻️ Quel(s) principe(s) avez-vous utilisé parmi les 7R pour choisir vos matériaux ?",
        r_list + no_r,
    )

    if no_r[0] in sourcing_selection:
        sourcing_selection = []

    st.caption(
        "ℹ️ Les R sont une variante des [5R du zéro déchet](https://fr.wikipedia.org/wiki/5_R_du_z%C3%A9ro_d%C3%A9chet)."
    )

    # Eco-pensé au début ou à la fin
    ecopense_selection = st.selectbox(
        "🎚️ Pour quelle raison avez-vous choisi ce matériau ?",
        list(ecopense_dict.keys()),
        index=None,
    )

    st.caption("ℹ️ 1 seule réponse possible, choisissez la plus contraignante.")

    # Impact local ( sourçage, répartition des richesses…)
    local_selection = st.selectbox(
        "🌍 D'où **provient** ce matériau ?",
        list(local_dict.keys()),
        index=None,
    )

    # Eco-conception en fin de vie
    grave_selection = st.multiselect(
        "🗑️ Quel(s) principe(s) avez-vous appliqué pour la **fin de vie** de ce matériau ?",
        r_list_eol + no_r_list_eol,
    )

    if any(opt in grave_selection for opt in no_r_list_eol):
        grave_selection = []

    # Échange avec sachant sur les questions écologiques
    knowledge_selection = st.selectbox(
        "🔎 Avez-vous échangé avec des **expert·es** pour le choix de vos matériaux et leur usage ?",
        list(knowledge_dict.keys()),
        index=None,
    )

    submitted = st.form_submit_button("✅ Valider les données d'usage")

# ---------------------------------------------------------------------------
# MAIN APP : AFFICHAGE DES DONNÉES D'IMPACT
# ---------------------------------------------------------------------------

col_logo, col_title = st.columns([1, 8])

with col_logo:
    st.image(img_dict["Logo"], width=100, link=WEBSITE)

with col_title:
    st.title("ExpoScore V0.2026")

# st.subheader(
#     "Analyse d'impact des matériaux utilisés en exposition, par l'association Déjà-Vu"
# )


tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🌱 Impact écologique",
        "👥 Impact social",
        "⚡ Impact d'usage",
        "📄 En savoir plus",
    ],
    default="📄 En savoir plus",
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
            grave_pct = grave_score / (len(r_list_eol) + 1)

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
            lifespan_months, lifespan_category = get_lifespan_category(
                lifespan_description
            )

            # Old logic, based off lifespan length
            # lifespan_score = lifespan_dict[lifespan_category] / len(lifespan_dict)

            # New logic : compare lifespan_months and project_length_months
            # 0.1 is very bad (project length <<< lifespan material)
            # 1 is perfect (length >>> lifespan material)
            # 0.5 is project length == lifespan material)

            lifespan_score = 0.1 + 0.9 * (
                project_length_months / (project_length_months + lifespan_months)
            )

            usage_selections["Durée d’usage adapté au matériau"] = (
                f"Votre projet dure {annees} année(s) et {mois} mois, comparé à la durée de vie du matériau : {lifespan_description}"
            )
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
                lambda x: "❌ Aucun principe R appliqué" if x == "[]" else x
            )  # Clean empty lists for 7R criterion

            ordre = {
                "Durée d’usage adapté au matériau": 1,
                "Eco-conception en fin de vie": 5,
                "Eco-pensé au début ou à la fin": 3,
                "Impact local ( sourçage, répartition des richesses…)": 4,
                "Respect des 7R en sourcing du matériau": 2,
                "Échange avec sachant sur les questions écologiques": 6,
            }

            df_usage = (
                df_usage[["category", "Score", "details", "source", "year"]]
                .sort_values(by="category", key=lambda x: x.map(ordre))
                .rename(
                    columns={
                        "category": "Catégorie",
                        "details": "Détails",
                        "source": "Source",
                        "year": "Année",
                    }
                )
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

with tab4:
    st.markdown(INTRO_TEXT)
