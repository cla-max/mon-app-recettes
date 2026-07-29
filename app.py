# ==========================================
# ONGLET 2 : GÉNÉRATEUR ET AMÉLIORATION
# ==========================================
with tab2:
    st.header("Générateur de recettes SIBO")
    ingredients = st.text_area("Quels ingrédients avez-vous sous la main ?")
    
    # --- CHANGEMENT DYNAMIQUE DU BOUTON ---
    if st.session_state.generated_recipes:
        texte_bouton = "🔄 Générer 3 nouvelles recettes"
    else:
        texte_bouton = "🍳 Générer 3 recettes"
    
    if st.button(texte_bouton):
        if not model:
            st.error("Veuillez d'abord renseigner votre clé API et sélectionner un modèle dans la barre latérale.")
        elif ingredients:
            with st.spinner("Création de 3 nouvelles recettes adaptées..."):
                prompt = f"""
                {contexte_phase}
                L'utilisateur possède ces ingrédients : {ingredients}. 
                Génère EXACTEMENT 3 recettes STRICTEMENT adaptées à la phase en cours du régime SIBO. N'ajoute sous aucun prétexte de l'ail, de l'oignon ou des aliments interdits dans cette phase.
                Si tu es sollicité plusieurs fois, propose des idées de recettes différentes et variées.
                Sépare CHAQUE recette par la chaîne de caractères exacte : "|||". Ne mets rien avant la première recette.
                """
                try:
                    response = model.generate_content(prompt)
                    recipes_raw = response.text.split("|||")
                    # On remplace l'ancienne liste par la nouvelle
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
