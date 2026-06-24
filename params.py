# DB PARAMETERS AND INPUT

DB_PATH = "exposcore.db"
LOGO_FILEPATH = "32291 - Informations V0/322911 - Logo Déjà-vu/plein_bleu.png"
MATERIALS_FILEPATH = [
    {
        "material": "PVC neuf",
        "filepath": "3222 - PVC/critères-tests-PVC-NEUF.xlsx",
        "imagepath": None,
    },
    {
        "material": "Carton",
        "filepath": "3223 - Carton /critères-tests-Carton.xlsx",
        "imagepath": "32291 - Informations V0/322912 - Images matériaux/11-CARTON-WEB.jpg",
    },
    {
        "material": "Aquapaper",
        "filepath": "3224 - Aquapaper /critères-Aquapaper.xlsx",
        "imagepath": "32291 - Informations V0/322912 - Images matériaux/13-AQUAPEPER-WEB.jpg",
    },
    {
        "material": "Adhésif mat pour découpe",
        "filepath": "3225 - Adhésif mat pour découpe /critères-adhésif-expr.xlsx",
        "imagepath": "32291 - Informations V0/322912 - Images matériaux/20-ADHESIF-WEB.jpg",
    },
    {
        "material": "Jet Tex",
        "filepath": "3226 - Jet Tex/critères-Jet-Tex.xlsx",
        "imagepath": "32291 - Informations V0/322912 - Images matériaux/02-ROULEAU-JETTEX-WEB.jpg",
    },
]

# APP TEXT

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

R_EXPLAIN = "ℹ️ Les R sont une variante des [5R du zéro déchet](https://fr.wikipedia.org/wiki/5_R_du_z%C3%A9ro_d%C3%A9chet)."
