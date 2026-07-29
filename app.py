import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant Culinaire SIBO", page_icon="🌿", layout="wide")

# --- INITIALISATION DE LA MÉMOIRE (SESSION STATE) ---
if "saved_recipes" not in st.session_state:
    st.session_state.saved_recipes = []
if "generated_recipes" not in st.session_state:
    st.session_state.generated_recipes = []

# --- BARRE LATÉRALE (SIDEBAR) ---
st.sidebar.title("⚙️ Configuration")
api_key = st.sidebar.text_input("Clé API Google Gemini", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("Phase du Régime SIBO")
phase = st.sidebar.radio(
    "Sélectionnez votre phase actuelle :",
    ["Phase 1 : Réduction", "Phase 2 : Réintroduction"]
)

# --- INITIALISATION DU MODÈLE IA ---
model = None
if api_key:
    genai.configure(api_key=api_key)
    try:
        # 1. On récupère la liste des modèles
        modeles_autorises = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 2. On filtre le modèle "fantôme" qui pose problème
        modeles_valides = [m for m in modeles_autorises if "2.5-flash" not in m]
        
        if not modeles_valides:
            st.sidebar.error("Votre clé n'a accès à aucun modèle valide.")
        else:
            # 3. On crée un menu déroulant pour que VOUS choisissiez le modèle
            nom_modele = st.sidebar.selectbox(
                "🤖 Modèle d'IA (changez en cas d'erreur) :", 
                modeles_valides
            )
            # 4. On charge le modèle sélectionné dans le menu
            model = genai.GenerativeModel(nom_modele)
            
    except Exception as e:
        st.sidebar.error(f"Erreur d'initialisation de l'API : {e}")
else:
    st.sidebar.warning("Veuillez entrer votre clé API pour utiliser l'IA.")

# --- DÉFINITION DU CONTEXTE SELON LA PHASE ---
if phase == "Phase 1 : Réduction":
    contexte_phase = """
    L'utilisateur suit la 'Phase 1 (Reduce)' du régime SIBO Bi-Phasic du Dr Nirala Jacobi (pauvre en FODMAP). 
    Applique strictement les règles de la Phase 1 (Restricted / Semi-Restricted) : interdiction absolue des sucres, de la majorité des produits laitiers, des céréales non germées, de l'ail, de l'oignon, des légumineuses non autorisées, et restriction sévère des amidons et fibres fermentescibles.
    """
else:
    contexte_phase = """
    L'utilisateur suit la 'Phase 2 (Reintroduce)' du régime SIBO Bi-Phasic du Dr Nirala Jacobi (pauvre en FODMAP). 
    Applique les règles de la Phase 2 : réintroduction progressive de certains aliments comme les lentilles, le riz, le quinoa, certains fromages affinés et certains fruits, mais l'ail, l'oignon et les légumes riches en FODMAP restent strictement interdits.
    """

# --- TITRE DE L'APPLICATION ---
st.title(f"🌿 Assistant Culinaire SIBO ({phase})")

# Création des 3 onglets
tab1, tab2, tab3 = st.tabs(["🔍 Vérificateur d'aliment", "🍳 Générateur de recettes", "📖 Mon Carnet"])


# ==========================================
# ONGLET 1 : VÉRIFICATEUR D'ALIMENT (HYBRIDE & COULEURS)
# ==========================================
with tab1:
    st.header("Vérifier un ingrédient")
    
    # --- VOS BASES DE DONNÉES MANUELLES ---
    db_phase_1 = {
        "poulet": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "boeuf": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "canard": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "coquelet": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "kangourou": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "agneau": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "abats": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "porc": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "caille": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "dinde": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "gibier": "[Autorisé] Les viandes simples, organiques si possible, sont parfaitement autorisées.",
        "oeufs": "[Autorisé] Les oeufs de poule, de caille, de canard, organiques si possible, sont parfaitement autorisées.",
        "saumon sauvage d'alaska ou du pacifique": "[Autorisé] Les produits de la mer simples, organiques si possible, sont parfaitement autorisés.",
        "barramundi": "[Autorisé] Les produits de la mer simples, organiques si possible, sont parfaitement autorisés.",
        "hareng et morue du pacifique": "[Autorisé] Les produits de la mer simples, organiques si possible, sont parfaitement autorisés.",
        "huîtres": "[Autorisé] Les produits de la mer simples, organiques si possible, sont parfaitement autorisés.",
        "sardines": "[Autorisé] Les produits de la mer simples, organiques si possible, sont parfaitement autorisés.",
        "coquilles saint-jacques": "[Autorisé] Les produits de la mer simples, organiques si possible, sont parfaitement autorisés.",
        "crevettes": "[Autorisé] Les produits de la mer simples, organiques si possible, sont parfaitement autorisés.",
        "vivaneau": "[Autorisé] Les produits de la mer simples, organiques si possible, sont parfaitement autorisés.",
        "truite": "[Autorisé] Les produits de la mer simples, organiques si possible, sont parfaitement autorisés.",
        "merlan": "[Autorisé] Les produits de la mer simples, organiques si possible, sont parfaitement autorisés.",
        "tofu ferme": "[Autorisé] (100g) Certaines protéines à base de plantes, organiques si possible, sont parfaitement autorisées dans des quantités précises.",
        "tempeh": "[Autorisé] (100g) Certaines protéines à base de plantes, organiques si possible, sont parfaitement autorisées dans des quantités précises.",
        "laitues à feuilles libres": "[Autorisé] (de manière illimitée) Les laitues, organiques si possible, sont parfaitement autorisées de manière illimitée.",
        "chicorée": "[Autorisé] (de manière illimitée) Les laitues, organiques si possible, sont parfaitement autorisées de manière illimitée.",
        "endives": "[Autorisé] (de manière illimitée) Les laitues, organiques si possible, sont parfaitement autorisées de manière illimitée.",
        "radicchio ou chicorée rouge d'hiver": "[Autorisé] (de manière illimitée) Les laitues, organiques si possible, sont parfaitement autorisées de manière illimitée.",
        "roquette": "[Autorisé] (de manière illimitée) Les laitues, organiques si possible, sont parfaitement autorisées de manière illimitée.",
        "pousses de bambou": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "gingembre": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "poivrons rouges": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "concombre": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "aubergine": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "olives (en saumure ou à l'huile d'olive)": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "oignons nouveaux (partie verte uniquement)": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "tomates": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "courges jaunes (d'été / pâtisson)": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "pakchoï": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "feuilles de blette (blette à carde blanche, etc.)": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "chou cantonnais": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "chou kale / chou frisé (variété toscane ou frisée)": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "luzerne / alfalfa": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "brocolis": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "haricots mungo (sprout length = 7cm)": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "radis": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "pois mange-tout": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "tournesol": "[Autorisé] (de manière illimitée) Les légumes, organiques si possible, sont parfaitement autorisés de manière illimitée.",
        "asperges": "[Autorisé] (Une) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "cœurs d'artichauts": "[Autorisé] (1/8 tasse) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "betteraves": "[Autorisé] (1/4 tasse) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "choux de bruxelles": "[Autorisé] (Deux) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "choux": "[Autorisé] (1/2 tasse) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "choux (de milan, wombok, rouge, vert)": "[Autorisé] (1/2 tasse) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "carottes oranges": "[Autorisé] (1 tasse) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "céleri": "[Autorisé] (1 bâton) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "céleri-rave": "[Autorisé] (1/2 tasse) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "bulbe de fenouil": "[Autorisé] (1/2 tasse) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "haricots verts": "[Autorisé] (Dix) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "poireaux (feuilles vertes)": "[Autorisé] (1/3 tasse) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "algues nori": "[Autorisé] (1 feuille) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "pois (verts)": "[Autorisé] (1/4 tasse) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "pois mange-tout ou pois gourmands": "[Autorisé] (5 cosses) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "jeunes pousses d'épinards": "[Autorisé] (1 tasse 1/2) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "épinards (anglais, mature)": "[Autorisé] (2 tasses) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "courges spaghetti": "[Autorisé] (1/2 tasse) Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "courgettes (jaune/verte)": "[Autorisé] (3/4 tasse)Les légumes, organiques si possible, sont parfaitement autorisés dans la limite de deux portions par repas.",
        "carottes (jaune/violette/rouge/blanche)": "[Autorisé] (1/4 tasse) Les légumes féculents, organiques si possible, sont parfaitement autorisés dans la limite d'une portion par repas.",
        "courge (kabocha, kent, butternut)": "[Autorisé] (1/4 tasse) Les légumes féculents, organiques si possible, sont parfaitement autorisés dans la limite d'une portion par repas.",
        "citrons jaunes": "[Autorisé] Les fruits, organiques si possible, peuvent être parfaitement autorisés dans la limite de deux portions par repas.",
        "citrons verts": "[Autorisé] Les fruits, organiques si possible, peuvent être parfaitement autorisés dans la limite de deux portions par repas.",
        "soupes": "[Autorisé] Les soupes peuvent être parfaitement autorisées si elles sont faites avce les légumes et les protéines autorisés.",
        "café organique": "[Autorisé] (1 tasse par jour) Certaines boissons peuvent être parfaitement autorisées.",
        "laits (amande, noix de coco, chanvre ou riz - sans sucre ajouté, gommes ni épaississants -": "[Autorisé] (1 tasse par jour) Certaines boissons peuvent être parfaitement autorisées.",
        "thés (noir/tisane)": "[Autorisé] Certaines boissons peuvent être parfaitement autorisées.",
        "eau filtrée": "[Autorisé] Certaines boissons peuvent être parfaitement autorisées.",
        "stevia (100% pure, no inulin)": "[Autorisé] Certains édulcorants peuvent être parfaitement autorisés.",
        "amandes": "[Autorisé] (10 unités) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "farine d'amande / poudre d'amande": "[Autorisé] (2 cuillères à soupe) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "beurre d'amande": "[Autorisé] (1 cuillère à soupe) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "graines de chia": "[Autorisé] (1 cuillère à soupe) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "noix de coco (farine/râpée)": "[Autorisé] (1/4 tasse) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "crème de coco (2 cuillères à soupe)": "[Autorisé] Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "lait de coco (sans épaississants ni gommes)": "[Autorisé] (1/4 tasse) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "graines de lin": "[Autorisé] (1/2 cuillère à soupe) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "noisettes": "[Autorisé] (Cinq) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "graines de chanvre": "[Autorisé] (2 cuillères à soupe) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "noix de macadamia": "[Autorisé] (Dix) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "mélange de noix": "[Autorisé] (2 cuillères à soupe) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "noix de pécans": "[Autorisé] (10 moitiés) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "pignons de pin": "[Autorisé] (1 cuillère à soupe) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "graines de citrouille": "[Autorisé] (2 cuillères à soupe) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "graines de sésame": "[Autorisé] (1 cuillère à soupe) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "graines de tournesol": "[Autorisé] (2 cuillères à café) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "noix": "[Autorisé] (10 moitiés) Certaines noix et graines peuvent être parfaitement autorisées dans la limite d'une portion par repas.",
        "ciboulette / ciboule de chine": "[Autorisé] Certains condiments, herbes, épices peuvent être parfaitement autorisés.",
        "chili": "[Autorisé] (11cm / 28g) Certains condiments, herbes, épices peuvent être parfaitement autorisés.",        
        "mayonnaise (sans sucre ajouté)": "[Autorisé] Certains condiments, herbes, épices peuvent être parfaitement autorisés.",
        "moutarde (sans ail)": "[Autorisé] Certains condiments, herbes, épices peuvent être parfaitement autorisés.",        
        "tabasco": "[Autorisé] Certains condiments, herbes, épices peuvent être parfaitement autorisés.",
        "herbes et épices (fraîches ou séchées), mais pas les mélanges d'épices. le curcuma et le gingembre sont particulièrement bénéfiques car ils sont anti-inflammatoires.": "[Autorisé] Certains condiments, herbes, épices peuvent être parfaitement autorisées.",        
        "huile d'avocat": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile de noix de coco": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile de lin (à faible teneur en lignine)": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "ghi / ghee": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile de pépin de raisin": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile tcm": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile d'olive (y compris infusée, par exemple à l'ail ou au piment)": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile de son de riz": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile de citrouille": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile de carthame": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile de sésame": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile de tournesol": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",        
        "huile de noix": "[Autorisé] Certaines graisses et huiles peuvent être parfaitement autorisées.",            
        "haricots à l'oeil noir": "[À consommer avec modération] (1/4 tasse) Certaines protéines à base de plantes, organiques si possible, sont autorisées dans le régime semi-restreint dans des quantités précises.",
        "haricots de lima (beurre)": "[À consommer avec modération] (1/4 tasse) Certaines protéines à base de plantes, organiques si possible, sont autorisées dans le régime semi-restreint dans des quantités précises.",
        "lentilles rouges/brunes": "[À consommer avec modération] (1/4 tasse) Certaines protéines à base de plantes, organiques si possible, sont autorisées dans le régime semi-restreint dans des quantités précises.",
        "panais": "[À consommer avec modération] Les légumes, organiques si possible, sont autorisés dans le régime semi-restreint.",
        "pommes de terre pelées": "[À consommer avec modération] (1/2 tasse) Les légumes féculents, organiques si possible, sont autorisés dans le régime semi-restreint dans la limite d'une portion par repas.",
        "avocats": "[À consommer avec modération] (1/4) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "bananes": "[À consommer avec modération] (1/2) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "fruits rouges (hors mûres)": "[À consommer avec modération] (1/2 tasse) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "caramboles": "[À consommer avec modération] (1 moyen) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "cerises": "[À consommer avec modération] (Trois) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "agrumes (hors citrons et citrons verts)": "[À consommer avec modération] (Un) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "raisins": "[À consommer avec modération] (Dix) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "miellats": "[À consommer avec modération] (1/4 tasse) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "kiwis": "[À consommer avec modération] (Un) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "litchis": "[À consommer avec modération] (Cinq) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "papayes": "[À consommer avec modération] (1/4 tasse) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "fruits de la passion": "[À consommer avec modération] (Un) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "ananas": "[À consommer avec modération] (1/4 tasse) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "grenades": "[À consommer avec modération] (1/2 petit ou 1/4 tasse de graines) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "rhubarbes": "[À consommer avec modération] (1 tige) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "melons rock / cantaloups": "[À consommer avec modération] (1/4 tasse) Les fruits, organiques si possible, peuvent être autorisés dans le régime semi-restreint.",
        "sarrasin trempé et cuit": "[À consommer avec modération] (1/2 tasse) Les céréales, fécules et pains peuvent être autorisés dans le régime semi-restreint.",
        "millet décortiqué, trempé et cuit": "[À consommer avec modération] (1/2 tasse) Les céréales, fécules et pains peuvent être autorisés dans le régime semi-restreint.",
        "quinoa (blanc et rouge) trempé et cuit": "[À consommer avec modération] (1/2 tasse) Les céréales, fécules et pains peuvent être autorisés dans le régime semi-restreint.",
        "riz (basmati / jasmin) trempé et cuit": "[À consommer avec modération] (1/2 tasse) Les céréales, fécules et pains peuvent être autorisés dans le régime semi-restreint.",
        "nouilles de varech": "[À consommer avec modération] (1/2 tasse) Les céréales, fécules et pains peuvent être autorisés dans le régime semi-restreint.",
        "nouilles de konjac": "[À consommer avec modération] (1/2 tasse) Les céréales, fécules et pains peuvent être autorisés dans le régime semi-restreint.",
        "flocons de porridge": "[À consommer avec modération] (1/4 tasse) Les céréales, fécules et pains peuvent être autorisés dans le régime semi-restreint.",
        "farine d'arrow-root": "[À consommer avec modération] (2 cuillères à soupe) Les céréales, fécules et pains peuvent être autorisés dans le régime semi-restreint.",
        "alcool (spiritueux clairs)": "[À consommer avec modération] (pas plus de 30ml deux fois par semaine) Certaines boissons peuvent être autorisées dans le régime semi-restreint.",
        "lait de soja": "[À consommer avec modération] (3 cuillères à soupe) Certaines boissons peuvent être autorisées dans le régime semi-restreint.",
        "dextrose": "[À consommer avec modération] Certains édulcorants peuvent être autorisés dans le régime semi-restreint.",
        "glucose": "[À consommer avec modération] Certains édulcorants peuvent être autorisés dans le régime semi-restreint.",
        "miel": "[À consommer avec modération] (pas plus de 2 cuillères à soupe par jour) Certains édulcorants peuvent être autorisés dans le régime semi-restreint.",
        "sauce poisson": "[À consommer avec modération] Certains condiments, herbes, épices peuvent être autorisés dans le régime semi-restreint.",        
        "miso": "[À consommer avec modération] Certains condiments, herbes, épices peuvent être autorisés dans le régime semi-restreint.",        
        "tamari": "[À consommer avec modération] Certains condiments, herbes, épices peuvent être autorisés dans le régime semi-restreint.",        
        "beurre": "[À consommer avec modération] Certaines graisses et huiles peuvent être autorisées dans le régime semi-restreint.",        
        "marlin": "[À éviter] Certains produits de la mer ne sont pas autorisés.",
        "requin": "[À éviter] Certains produits de la mer ne sont pas autorisés.",
        "espadon": "[À éviter] Certains produits de la mer ne sont pas autorisés.",
        "thon": "[À éviter] Certains produits de la mer ne sont pas autorisés.",
        "lait": "[À éviter] Les produits laitiers sont pas autorisés.",
        "fromage": "[À éviter] Les produits laitiers sont pas autorisés.",
        "chou-fleur": "[À éviter] Certains légumes ne sont pas autorisés dans le régime semi-restreint.",
        "maïs": "[À éviter] Certains légumes ne sont pas autorisés dans le régime semi-restreint.",
        "ail": "[À éviter] Certains légumes ne sont pas autorisés dans le régime semi-restreint.",
        "champignons": "[À éviter] Certains légumes ne sont pas autorisés dans le régime semi-restreint.",
        "oignons": "[À éviter] Certains légumes ne sont pas autorisés dans le régime semi-restreint.",
        "pommes de terre non pelées": "[À éviter] Certains légumes féculents ne sont pas autorisés dans le régime semi-restreint.",
        "patates douces": "[À éviter] Certains légumes féculents ne sont pas autorisés dans le régime semi-restreint.",
        "pommes": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "abricots": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "mûres": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "figues": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "confitures": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "mangues": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "nashis": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "nectarines": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "poires": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "pêches": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "kakis": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "prunes": "[À éviter] Certains fruits ne sont pas autorisés dans le régime semi-restreint.",
        "bières": "[À éviter] Certaines boissons ne sont pas autorisées dans le régime semi-restreint.",
        "boissons énergisantes": "[À éviter] Certaines boissons ne sont pas autorisées dans le régime semi-restreint.",
        "jus de fruits": "[À éviter] Certaines boissons ne sont pas autorisées dans le régime semi-restreint.",
        "liqueurs et spirits (dark)": "[À éviter] Certaines boissons ne sont pas autorisées dans le régime semi-restreint.",
        "boissons softs": "[À éviter] Certaines boissons ne sont pas autorisées dans le régime semi-restreint.",
        "vin": "[À éviter] Certaines boissons ne sont pas autorisées dans le régime semi-restreint.",
        "nectar d'agave": "[À éviter] Certains édulcorants ne sont pas autorisés dans le régime semi-restreint.",
        "édulcorants artificiels": "[À éviter] Certains édulcorants ne sont pas autorisés dans le régime semi-restreint.",
        "sirop d'érable": "[À éviter] Certains édulcorants ne sont pas autorisés dans le régime semi-restreint.",
        "xylitol": "[À éviter] Certains édulcorants ne sont pas autorisés dans le régime semi-restreint.",
        "noix de cajou": "[À éviter] Certaines noix et graines ne sont pas autorisées dans le régime semi-restreint.",
        "cacahuètes": "[À éviter] Certaines noix et graines ne sont pas autorisées dans le régime semi-restreint.",
        "pistaches": "[À éviter] Certaines noix et graines ne sont pas autorisées dans le régime semi-restreint.",
        "vinaigre balsamique": "[À éviter] Certains condiments, herbes, épices ne sont pas autorisés dans le régime semi-restreint.",
        "racines de chicorée": "[À éviter] Certains condiments, herbes, épices ne sont pas autorisés dans le régime semi-restreint.",
        "sauces soja": "[À éviter] Certains condiments, herbes, épices ne sont pas autorisés dans le régime semi-restreint."
    }
    
    db_phase_2 = {
        "poulet": "[Autorisé] Les viandes simples sont toujours autorisées.",
        "ail": "[À éviter] L'ail reste strictement interdit même en Phase 2.",
        "lentilles": "[Autorisé] Les lentilles rouges/brunes (1/2 tasse, trempées et cuites) peuvent être réintroduites."
    }
    
    # --- FONCTION DE COULEUR ---
    def afficher_resultat_couleur(texte):
        texte_min = texte.lower()
        if "[autorisé]" in texte_min:
            st.success(texte) # Vert
        elif "[à éviter]" in texte_min or "[non autorisé]" in texte_min:
            st.error(texte) # Rouge
        elif "[à consommer avec modération]" in texte_min or "[à limiter]" in texte_min:
            st.warning(texte) # Orange
        else:
            st.info(texte) # Bleu par défaut

    aliment = st.text_input("Entrez un aliment à vérifier (ex: ail, lentilles, poulet)")
    
    if st.button("Vérifier"):
        if aliment:
            aliment_propre = aliment.strip().lower()
            db_actuelle = db_phase_1 if phase == "Phase 1 : Réduction" else db_phase_2
            
            # 1. Vérification base locale
            if aliment_propre in db_actuelle:
                st.caption(f"✅ Aliment reconnu dans vos règles strictes ({phase})")
                afficher_resultat_couleur(db_actuelle[aliment_propre])
            
            # 2. Si inconnu -> IA
            else:
                if not model:
                    st.error("L'aliment est inconnu dans votre base. Veuillez entrer et valider une clé API valide dans le menu pour que l'IA puisse l'analyser.")
                else:
                    st.caption("🤖 Aliment inconnu dans vos règles. Analyse par l'IA en cours...")
                    with st.spinner("Recherche dans le savoir de l'IA..."):
                        prompt = f"""
                        {contexte_phase}
                        L'aliment suivant est-il acceptable dans cette phase exacte : '{aliment}' ? 
                        Réponds obligatoirement en commençant par l'une de ces 3 étiquettes : [Autorisé], [À éviter], ou [À consommer avec modération]. 
                        Ensuite, donne une explication claire et concise de 2 ou 3 phrases maximum en te basant sur le protocole SIBO Bi-Phasic.
                        """
                        try:
                            response = model.generate_content(prompt)
                            afficher_resultat_couleur(response.text)
                        except Exception as e:
                            st.error(f"🚨 Erreur exacte renvoyée par Google : {str(e)}")


# ==========================================
# ONGLET 2 : GÉNÉRATEUR ET AMÉLIORATION
# ==========================================
with tab2:
    st.header("Générateur de recettes SIBO")
    ingredients = st.text_area("Quels ingrédients avez-vous sous la main ?")
    
    if st.button("Générer des recettes"):
        if not model:
            st.error("Veuillez d'abord renseigner votre clé API dans la barre latérale.")
        elif ingredients:
            with st.spinner("Création des recettes adaptées..."):
                prompt = f"""
                {contexte_phase}
                L'utilisateur possède ces ingrédients : {ingredients}. 
                Génère 2 à 3 recettes STRICTEMENT adaptées à la phase en cours du régime SIBO. N'ajoute sous aucun prétexte de l'ail, de l'oignon ou des aliments interdits dans cette phase.
                Sépare CHAQUE recette par la chaîne de caractères exacte : "|||". Ne mets rien avant la première recette.
                """
                try:
                    response = model.generate_content(prompt)
                    recipes_raw = response.text.split("|||")
                    st.session_state.generated_recipes = [r.strip() for r in recipes_raw if len(r.strip()) > 20]
                except Exception as e:
                    st.error(f"🚨 Erreur exacte renvoyée par Google : {str(e)}")

    if st.session_state.generated_recipes:
        st.markdown("### Voici vos propositions :")
        
        for i, recipe in enumerate(st.session_state.generated_recipes):
            st.markdown(f"#### 🍲 Proposition n°{i+1}")
            st.write(recipe)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                improvement = st.text_input("Une envie spécifique ?", key=f"improve_input_{i}")
                if st.button("✨ Améliorer cette recette", key=f"btn_improve_{i}"):
                    if improvement and model:
                        with st.spinner("Modification de la recette..."):
                            prompt_improve = f"""
                            {contexte_phase}
                            Voici une recette existante : {recipe}. 
                            L'utilisateur demande cette modification : "{improvement}". 
                            Réécris la recette complète en appliquant cette modification tout en respectant strictement les règles de la phase du régime SIBO.
                            """
                            try:
                                response = model.generate_content(prompt_improve)
                                st.session_state.generated_recipes[i] = response.text
                                st.rerun() 
                            except Exception as e:
                                st.error(f"🚨 Erreur exacte renvoyée par Google lors de l'amélioration : {str(e)}")
            
            with col2:
                st.write("") 
                st.write("")
                if st.button("💾 Sauvegarder", key=f"btn_save_{i}", type="primary"):
                    if recipe not in st.session_state.saved_recipes:
                        st.session_state.saved_recipes.append(recipe)
                        st.success("Ajoutée au carnet !")
            
            st.divider()


# ==========================================
# ONGLET 3 : CARNET DE RECETTES
# ==========================================
with tab3:
    st.header("Mon Carnet de Recettes")
    
    if not st.session_state.saved_recipes:
        st.info("Votre carnet est vide pour le moment.")
    else:
        for i, recipe in enumerate(st.session_state.saved_recipes):
            with st.expander(f"📖 Recette sauvegardée n°{i+1}"):
                st.write(recipe)
                if st.button("❌ Supprimer du carnet", key=f"btn_delete_{i}"):
                    st.session_state.saved_recipes.pop(i)
                    st.rerun()
