import streamlit as st
import requests
import pandas as pd

# Configuration de la page Streamlit : titre :
st.set_page_config(page_title="Prédiction pluie", layout="wide")

# Titre principal de l'application :
st.title("Prédiction du risque de pluie")

# URL de l'API FastAPI :
API_URL = "http://127.0.0.1:8000"

# Fonction de récupération des données via API :
@st.cache_data
def get_all_data():
    response = requests.get(f"{API_URL}/all_predictions")
    data = response.json()
    return pd.DataFrame(data)

# Chargement des données globales :
df = get_all_data()

# Récupération des stations et des dates disponibles :
stations = sorted(df["station_id"].unique())
dates = sorted(df["date"].unique())

# Dictionnaire de correspondance
stations_labels = {
    "000CT": "Paris 6ème - Saint Germain des Prés",
    "000EW": "Paris 20ème - Porte de Vincennes",
    "ME098": "Paris 16ème - Trocadero"
}

# Création de deux colonnes pour les éléments à selectionner :
col1, col2 = st.columns(2)

# Sélection de la station :
with col1:
    station = st.selectbox(
        "Choisir une station",
        stations,
        format_func=lambda x: f"{stations_labels.get(x, x)} ({x})"
    )

# Sélection de la date :
with col2:
    date = st.selectbox("Choisir une date", dates)

# Appel API pour récupérer la prédiction correspondant à la sélection :
response = requests.get(
    f"{API_URL}/prediction",
    params={"station_id": station, "date": date}
)
data = response.json()
st.subheader("Résultats :")

# Vérification de la présence de données :
if "error" in data:
    st.warning("Aucune donnée disponible")
else:

    # Affichage des résultats sous forme de métriques :
    col1, col2, col3 = st.columns(3)

    # Probabilité de pluie :
    with col1:
        st.metric("Probabilité de pluie", data["probabilite"])

    # Interprétation métier :
    with col2:
        st.metric("Interprétation", data["interpretation"])

    # Indicateur d'alerte basé sur le seuil métier :
    with col3:
        if data["proba_pluie"] > 0.65:
            st.error("Alerte envoyée")
        else:
            st.success("Pas d'alerte")


# Création d'un graphique global qui permet d'observer l'évolution du risque maximal de pluie sur l'ensemble de nos stations : 
st.subheader("Pour tout PARIS : probabilité maximale de pluie")
df_global = df.groupby("date")["proba_pluie"].max().reset_index()
st.line_chart(
    df_global.set_index("date")["proba_pluie"]
)
