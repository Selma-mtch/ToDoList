# fichier : app.py
import streamlit as st

from backend import (
    create_user,
    login_user,
    add_task,
    get_tasks,
    mark_done,
    delete_task
)


# ==========================================
# Session utilisateur
# ==========================================

if "user_id" not in st.session_state:
    st.session_state.user_id = None

#########################################
##FRONT

st.title("Ma TodoList")

# ==========================================
# UTILISATEUR NON CONNECTÉ
# ==========================================

if st.session_state.user_id is None:

    st.subheader("Connexion / Inscription")

    choix = st.radio(
        "Choisir une action",
        ["Connexion", "Inscription"]
    )

    username = st.text_input("Nom d'utilisateur")

    password = st.text_input(
        "Mot de passe",
        type="password"
    )

    if choix == "Inscription":

        if st.button("Créer un compte"):

            if username.strip() == "" or password.strip() == "":
                st.error("Veuillez remplir tous les champs")
            else:
                success = create_user(username, password)
                if success:
                    st.success("Compte créé avec succès")
                else:
                    st.error("Nom d'utilisateur déjà utilisé")

    else:

        if st.button("Se connecter"):

            user_id = login_user(username, password)

            if user_id:
                st.session_state.user_id = user_id
                st.success("Connexion réussie")
                st.rerun()
            else:
                st.error("Identifiants incorrects")

# ==========================================
# UTILISATEUR CONNECTÉ
# ==========================================

else:

    st.success("Vous êtes connecté")

    if st.button("Déconnexion"):
        st.session_state.user_id = None
        st.rerun()

    st.divider()

    st.subheader("Ajouter une tâche")

    new_task = st.text_input("Nouvelle tâche")

    if st.button("Ajouter"):

        if new_task.strip() != "":
        
            add_task(st.session_state.user_id, new_task)
            st.session_state.task_input = ""  # Vider le champ input
            st.rerun()
        else:
            st.warning("Veuillez écrire une tâche")

    st.divider()

    st.subheader("Mes tâches")

    tasks = get_tasks(st.session_state.user_id)

    if len(tasks) == 0:
        st.info("Aucune tâche pour le moment")
    else:

        for _, t in tasks.iterrows():

            task_id = int(t["id"])
            task = t["description"]
            done = t["status"]

            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

            with col1:
                if done:
                    st.write(f"Fait : {task}")
                else:
                    st.write(f"A faire : {task}")

            with col2:
                if not done:
                    if st.button("Terminer", key=f"done_{task_id}"):
                        mark_done(task_id)
                        st.rerun()

            with col3:
                if st.button("Supprimer", key=f"delete_{task_id}"):
                    delete_task(task_id)
                    st.rerun()