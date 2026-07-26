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

if api_key:
    genai.configure(api_key=api_key)
    # Déclaration du modèle avec son chemin complet pour limiter les erreurs 404
    model = genai.GenerativeModel('models/gemini-1.5-flash') 
else:
    st.sidebar.warning("Veuillez entrer votre clé API pour utiliser l'IA.")

# Définition du contexte pour l'IA en fonction de la phase sélectionnée
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
# ONGLET 1 : VÉRIFICATEUR D'ALIMENT
# ==========================================
with tab1:
    st.header("Vérifier un ingrédient")
    aliment = st.text_input("Entrez un aliment à vérifier (ex: ail, lentilles, poulet)")
    
    if st.button("Vérifier"):
        if not api_key:
            st.error("Veuillez d'abord renseigner votre clé API dans la barre latérale.")
        elif aliment:
            with st.spinner("Analyse en cours..."):
                prompt = f"""
                {contexte_phase}
                L'aliment suivant est-il acceptable dans cette phase exacte : '{aliment}' ? 
                Réponds obligatoirement en commençant par l'une de ces 3 étiquettes : [Autorisé], [À éviter], ou [À consommer avec modération]. 
                Ensuite, donne une explication claire et concise de 2 ou 3 phrases maximum en te basant sur le protocole SIBO Bi-Phasic.
                """
                try:
                    response = model.generate_content(prompt)
                    st.info(response.text)
                except Exception as e:
                    # Affichage clair de l'erreur sans faire planter l'application
                    st.error(f"🚨 Erreur exacte renvoyée par Google : {str(e)}")


# ==========================================
# ONGLET 2 : GÉNÉRATEUR ET AMÉLIORATION
# ==========================================
with tab2:
    st.header("Générateur de recettes SIBO")
    ingredients = st.text_area("Quels ingrédients avez-vous sous la main ?")
    
    if st.button("Générer des recettes"):
        if not api_key:
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
                    if improvement:
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
