import streamlit as st
import random
import requests
import json
import pandas as pd


RECSYS_URL="http://localhost:8000"
DATASYS_URL="http://localhost:8001"

# Configuration de la page
st.set_page_config(
    page_title="Dishcovery",
    page_icon="🍽️",
    layout="wide"
)

# Styles CSS
st.markdown(
    """
    <style>
        /* Sidebar styling */
        section[data-testid="stSidebar"] .stRadio label, 
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] * {
            color: #FFFFFF !important;
        }
        
        .main {
            background: linear-gradient(180deg, #1C0B0B 0%, #3A120D 100%);
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #7A1C1C 0%, #3A0F0F 100%);
            color: white;
        }
        
        /* Titles */
        .dish-title {
            font-size: 60px;
            font-weight: 900;
            color: #FFB703;
            text-align: center;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }
        .dish-subtitle {
            text-align: center;
            font-size: 22px;
            font-weight: 600;
            color: #FFB703;
            margin-bottom: 40px;
        }
        .section-title {
            font-size: 32px;
            font-weight: 900;
            color: #FFB703;
            margin-top: 20px;
            margin-bottom: 20px;
            border-left: 8px solid #E63946;
            padding-left: 16px;
        }
        
        /* Cards */
        .card {
            background: linear-gradient(145deg, #FFF2E0, #FFD6A5);
            padding: 28px;
            border-radius: 24px;
            box-shadow: 0px 12px 40px rgba(0,0,0,0.4);
            margin-bottom: 28px;
            border: 2px solid #E63946;
        }
        
        /* Restaurant card */
        .restaurant-card {
            background: linear-gradient(145deg, #FFF2E0, #FFD6A5);
            padding: 24px;
            border-radius: 24px;
            box-shadow: 0px 12px 40px rgba(0,0,0,0.4);
            margin-bottom: 20px;
            border: 2px solid #E63946;
            text-align: center;
        }
        .restaurant-name {
            font-size: 28px;
            font-weight: 900;
            color: #9B111E;
            margin-bottom: 12px;
        }
        .restaurant-cuisine {
            font-size: 18px;
            font-weight: 700;
            color: #E63946;
            margin-bottom: 16px;
        }
        .restaurant-address {
            font-size: 14px;
            color: #9B111E;
            margin-bottom: 16px;
            font-style: italic;
        }
        .restaurant-description {
            font-size: 16px;
            color: #9B111E;
            line-height: 1.6;
            margin-top: 16px;
        }
        .restaurant-photo {
            width: 100%;
            height: 300px;
            background: linear-gradient(135deg, #E63946, #9B111E);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 80px;
            margin-bottom: 20px;
        }
        
        /* Badge */
        .badge {
            display: inline-block;
            background: linear-gradient(135deg, #E63946, #9B111E);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            margin-right: 6px;
            margin-top: 6px;
        }
        
        /* User info in sidebar */
        .user-info {
            background: rgba(255, 255, 255, 0.1);
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 20px;
            color: white;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ========================================
# DONNÉES FACTICES - À REMPLACER PAR LA BDD
# ========================================

# Base de restaurants factices
FAKE_RESTAURANTS = [
    {"business_id": 1, "name": "La Bella Vita", "cuisine": "Italienne", "address": "15 Rue de la Paix, 75002 Paris", "description": "Trattoria authentique proposant des pâtes fraîches et des pizzas au feu de bois dans une ambiance chaleureuse.", "icon": "🍝"},
    {"business_id": 2, "name": "Le Petit Gourmet", "cuisine": "Française", "address": "8 Avenue Montaigne, 75008 Paris", "description": "Bistrot raffiné offrant une cuisine française moderne avec des produits de saison et une carte des vins exceptionnelle.", "icon": "🥖"},
    {"business_id": 3, "name": "Sakura Garden", "cuisine": "Japonaise", "address": "42 Rue Sainte-Anne, 75001 Paris", "description": "Restaurant japonais traditionnel spécialisé dans les sushis, sashimis et ramens préparés par des chefs expérimentés.", "icon": "🍣"},
    {"business_id": 4, "name": "El Camino Real", "cuisine": "Mexicaine", "address": "23 Rue Oberkampf, 75011 Paris", "description": "Cuisine mexicaine authentique avec tacos, quesadillas et cocktails maison dans une atmosphère festive et colorée.", "icon": "🌮"},
    {"business_id": 5, "name": "Golden Dragon", "cuisine": "Chinoise", "address": "56 Avenue d'Ivry, 75013 Paris", "description": "Restaurant chinois proposant dim sum, canard laqué et plats sichuan dans un cadre élégant et traditionnel.", "icon": "🥟"},
    {"business_id": 6, "name": "Taj Mahal", "cuisine": "Indienne", "address": "12 Rue de la Harpe, 75005 Paris", "description": "Saveurs indiennes authentiques avec currys, tandooris et naans préparés selon les recettes traditionnelles du Punjab.", "icon": "🍛"},
    {"business_id": 7, "name": "Athens Taverna", "cuisine": "Grecque", "address": "34 Rue Mouffetard, 75005 Paris", "description": "Taverne grecque familiale servant moussaka, souvlaki et mezze dans une ambiance méditerranéenne conviviale.", "icon": "🫒"},
    {"business_id": 8, "name": "Bangkok Street", "cuisine": "Thaïlandaise", "address": "18 Rue de Belleville, 75020 Paris", "description": "Street food thaïlandaise raffinée avec pad thaï, currys parfumés et desserts exotiques dans un décor moderne.", "icon": "🍜"},
    {"business_id": 9, "name": "Beirut Express", "cuisine": "Libanaise", "address": "67 Rue du Faubourg Saint-Denis, 75010 Paris", "description": "Cuisine libanaise généreuse proposant houmous, falafels, chawarmas et pâtisseries orientales faites maison.", "icon": "🥙"},
    {"business_id": 10, "name": "Seoul Kitchen", "cuisine": "Coréenne", "address": "89 Rue Sainte-Anne, 75002 Paris", "description": "Restaurant coréen contemporain spécialisé dans le BBQ coréen, bibimbap et kimchi maison fermenté traditionnellement.", "icon": "🍲"},
    {"business_id": 11, "name": "Casa Española", "cuisine": "Espagnole", "address": "45 Rue des Martyrs, 75009 Paris", "description": "Bar à tapas authentique proposant paella, jambon ibérique et une sélection de vins espagnols dans une ambiance festive.", "icon": "🥘"},
    {"business_id": 12, "name": "Marrakech Palace", "cuisine": "Marocaine", "address": "28 Rue des Rosiers, 75004 Paris", "description": "Palais marocain offrant tajines, couscous royal et pâtisseries orientales dans un décor somptueux aux mille et une nuits.", "icon": "🫕"},
]

# _,RESTAURANTS,_,_=requests.get(DATASYS_URL+"/data/dataframes")
restaurants=pd.read_json(r"services\data_service\data\businessfinal.json")
users=pd.read_parquet(r"services\data_service\data\userfinal.parquet")



CUISINE_TYPES = ['Restaurants', 'Food', 'Sandwiches', 'Fast Food', 'Pizza', 'American (Traditional)', 'Breakfast & Brunch', 'Burgers', 'Nightlife', 'Bars', 'Mexican', 'American (New)', 'Italian', 'Coffee & Tea', 'Chinese', 'Seafood', 'Salad', 'Chicken Wings', 'Delis', 'Cafes', 'Japanese', 'Desserts', 'Event Planning & Services', 'Bakeries', 'Caterers']

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "username" not in st.session_state:
    st.session_state.username = ""

if "cold_start_done" not in st.session_state:
    st.session_state.cold_start_done = False

if "selected_cuisines" not in st.session_state:
    st.session_state.selected_cuisines = []

if "cold_start_restaurants" not in st.session_state:
    st.session_state.cold_start_restaurants = []

if "current_restaurant_index" not in st.session_state:
    st.session_state.current_restaurant_index = 0

if "liked_restaurants" not in st.session_state:
    st.session_state.liked_restaurants = []

if "disliked_restaurants" not in st.session_state:
    st.session_state.disliked_restaurants = []

if "label_tastes" not in st.session_state:
    st.session_state.label_tastes=[]

if "recommended_restaurants" not in st.session_state:
    st.session_state.recommended_restaurants=[]


def create_user_account(email, username, password):
    """Crée un utilisateur via le backend FastAPI."""
    try:
        payload = {
            "user_id": email,
            "name": username,
            "mdp": password
        }
        response = requests.post(f"{RECSYS_URL}/app/create_user", params={
            "user_id": email,
            "name": username,
            "mdp": password
        })

        if response.status_code != 200:
            return {"success": False, "error": "Erreur serveur"}

        data = response.json()

        if data.get("create_user"):
            return {"success": True, "username": username}
        else:
            return {"success": False, "error": "Email déjà utilisé"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify_login(email, password):
    """Vérifie un login via le backend FastAPI."""
    try:
        payload = {
            "user_id": email,
            "mdp": password
        }
        response = requests.post(f"{RECSYS_URL}/app/sign_in", params=payload)

        if response.status_code != 200:
            return {"success": False, "error": "Erreur serveur"}

        data = response.json()
        result = data.get("check_mdp")

        if result:
            # Backend only returns True/False
            return {
                "success": True,
                "username": email.split("@")[0],
                "cold_start_done": False
            }
        else:
            return {"success": False, "error": "Identifiants incorrects"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def logout_user():
    """Déconnexion de l'utilisateur"""
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.username = ""
    st.session_state.cold_start_done = False
    st.session_state.selected_cuisines = []
    st.session_state.cold_start_restaurants = []
    st.session_state.current_restaurant_index = 0
    st.session_state.liked_restaurants = []
    st.session_state.disliked_restaurants = []


if not st.session_state.logged_in:
    st.markdown('<div class="dish-title">Dishcovery</div>', unsafe_allow_html=True)
    st.markdown('<div class="dish-subtitle">Découvrez les restaurants faits pour vous</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        auth_mode = st.radio(
            "Choisissez une option",
            ["Se connecter", "Créer un compte"],
            horizontal=True
        )
        
        st.markdown("---")
        
        if auth_mode == "Se connecter":
            email_input = st.text_input("📧 Email", key="email_login")
            username_input=email_input
            password_input = st.text_input("🔒 Mot de passe", type="password", key="password_login")
            
            if st.button("🔓 Connection", use_container_width=True):
                if email_input and password_input:
                    check=requests.post(DATASYS_URL+"/app/sign_in",params={
                        "user_id":email_input,
                        "mdp":password_input
                    })
                    if check:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.session_state.username = email_input
                        st.session_state.cold_start_done = True
                        st.rerun()
                    else:
                        st.warning("⚠️ Wrong password / user id")
                        
                else:
                    st.warning("⚠️ Please fill the blank spaces")
        
        else:  # Créer un compte
            email_input = st.text_input("📧 Email", key="email_signup")
            username_input = st.text_input("👤 Username (email again)", key="username_signup")
            password_input = st.text_input("🔒 Password", type="password", key="password_signup")
            
            if st.button("✨ Register", use_container_width=True):
                if email_input and username_input and password_input:
                    result = create_user_account(email_input, username_input, password_input)
                    if result["success"]:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.session_state.username = result["username"]
                        st.session_state.cold_start_done = False
                        st.success("✅ Registered !")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")
                else:
                    st.warning("⚠️ Please fill the blank spaces")
        
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.logged_in:
    
    # Affichage des informations utilisateur
    st.sidebar.markdown(
        f'<div class="user-info">👤 <strong>{st.session_state.username}</strong></div>',
        unsafe_allow_html=True
    )
    
    if st.sidebar.button("🚪 Log out", use_container_width=True):
        logout_user()
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🍽️ Dishcovery")
    st.sidebar.markdown("**Your personal restaurant guide**")
    
    
    if not st.session_state.cold_start_done and not st.session_state.selected_cuisines:
        
        st.markdown('<div class="section-title">🎯 Tell us what are your tastes</div>', unsafe_allow_html=True)
        st.markdown("Select at least one type of food to provide personalised recommendations")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            selected_cuisines = st.multiselect(
                "🍽️ Type of food that you like",
                CUISINE_TYPES,
                help="You can chose multiple"
            )
            
            if st.button("✅ Lock in your choices", use_container_width=True, type="primary"):
                if selected_cuisines:
                    st.session_state.selected_cuisines = selected_cuisines
                    filtered_restaurants = [r for r in FAKE_RESTAURANTS if r["cuisine"] in selected_cuisines]
                    st.session_state.cold_start_restaurants = random.sample(
                        filtered_restaurants, 
                        min(5, len(filtered_restaurants))
                    )
                    st.session_state.current_restaurant_index = 0
                    st.rerun()
                else:
                    st.warning("⚠️ Enter at least a type of food")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif not st.session_state.cold_start_done and st.session_state.selected_cuisines:
        
        if st.session_state.current_restaurant_index < len(st.session_state.cold_start_restaurants):
            
            current_resto = st.session_state.cold_start_restaurants[st.session_state.current_restaurant_index]
            

            st.markdown('<div class="section-title">👍 Do you like this restaurant ?</div>', unsafe_allow_html=True)
            st.markdown(f"**Restaurant {st.session_state.current_restaurant_index + 1} sur {len(st.session_state.cold_start_restaurants)}**")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown('<div class="restaurant-card">', unsafe_allow_html=True)
                
                # Photo du restaurant (placeholder avec icône)
                st.markdown(
                    f'<div class="restaurant-photo">{current_resto["icon"]}</div>',
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f'<div class="restaurant-name">{current_resto["name"]}</div>',
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f'<div class="restaurant-cuisine">{current_resto["cuisine"]}</div>',
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f'<div class="restaurant-address">📍 {current_resto["address"]}</div>',
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f'<div class="restaurant-description">{current_resto["description"]}</div>',
                    unsafe_allow_html=True
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Boutons Like / Dislike
                col_dislike, col_like = st.columns(2)
                
                with col_dislike:
                    if st.button("👎 I don't like", use_container_width=True, key=f"dislike_{current_resto['business_id']}"):
                        st.session_state.label_tastes.append(False)
                        st.rerun()
                
                with col_like:
                    if st.button("❤️ I like", use_container_width=True, type="primary", key=f"like_{current_resto['business_id']}"):
                        st.session_state.label_tastes.append(True)
                        st.rerun()
        
        else:
            # Cold start terminé
            st.session_state.cold_start_done = True
            link_tastes=[]
            for restaurant in st.session_state.cold_start_restaurants:
                link_tastes.append(restaurant["business_id"])
            
            payload = {
                "user_id": st.session_state.username,
                "cold_start_restaurants": st.session_state.selected_cuisines,
                "link_tastes": link_tastes,
                "label_tastes": st.session_state.label_tastes
}
            cold=requests.post(RECSYS_URL+"/recommender/cold_start",json=payload)
            if "user_db" in st.session_state and st.session_state.user_email in st.session_state.user_db:
                st.session_state.user_db[st.session_state.user_email]["cold_start_done"] = True
            st.rerun()

    
    else:
        
        st.markdown('<div class="dish-title">Your recommendations</div>', unsafe_allow_html=True)
        
        # Barre de recherche avec LLM
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Smart research")
        
        search_query = st.text_input(
            "Décrivez ce que vous recherchez...",
            placeholder="Example: A french restaurant to get dinner with my girlfriend.",
            label_visibility="collapsed"
        )
        
        if st.button("🔎 Search", use_container_width=True):
            if search_query:
                user_query={
                    "user_id":st.session_state.username,
                    "user_input":search_query,
                    "top_k":30
                }
                responseLLM=requests.post(RECSYS_URL+"/recommender/get_rec",json=user_query)
                st.session_state.recommended_restaurants=responseLLM.json()
                st.info(f"🤖 Active research for : '{search_query}'")
            else:
                st.warning("⚠️ Enter a research")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recommandations personnalisées
        st.markdown('<div class="section-title">Your recommendations</div>', unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        for idx, resto in enumerate(st.session_state.recommended_restaurants):
            with cols[idx % 3]:
                st.markdown('<div class="restaurant-card">', unsafe_allow_html=True)
                
                st.markdown(
                    f'<div class="restaurant-photo">{resto["icon"]}</div>',
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f'<div class="restaurant-name">{resto["name"]}</div>',
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f'<span class="badge">{resto["cuisine"]}</span>',
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f'<div class="restaurant-address">📍 {resto["address"]}</div>',
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f'<div class="restaurant-description">{resto["description"]}</div>',
                    unsafe_allow_html=True
                )
                
                # Boutons Like / Dislike pour chaque restaurant
                col_dislike, col_like = st.columns(2)
                
                with col_dislike:
                    if st.button("👎", use_container_width=True, key=f"rec_dislike_{resto['business_id']}_{idx}"):
                        review_added=requests.post(RECSYS_URL+"/app/add_review",st.session_state.username, [resto['business_id']], False)
                        st.session_state.disliked_restaurants.append(resto["business_id"])
                        st.success(f"👎 {resto['name']} removed from your recommendations")
                
                with col_like:
                    if st.button("❤️", use_container_width=True, key=f"rec_like_{resto['business_id']}_{idx}"):
                        review_added=requests.post(RECSYS_URL+"/app/add_review",st.session_state.username, [resto['business_id']], [True])
                        st.session_state.liked_restaurants.append(resto["business_id"])
                        st.success(f"❤️ {resto['name']} added to your favorites")
                
                st.markdown('</div>', unsafe_allow_html=True)