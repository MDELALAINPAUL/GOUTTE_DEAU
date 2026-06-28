from fastapi import FastAPI
import sqlite3
import pandas as pd

# Initialisation de l'application FastAPI.
app = FastAPI()

# Fonction de connexion à la base SQLite.
def get_connection():
    return sqlite3.connect("GoutteDEAU.db")

# Endpoint principal permettant de récupérer une prédiction :
# Il prend en entrée :
    # Station_id : identifiant de la station.
    # Date : date pour laquelle on souhaite connaître le risque de pluie.
@app.get("/prediction")
def get_prediction(station_id: str, date: str):
    # Connexion à la base SQLite :
    conn = get_connection()
    query = f"""
    SELECT *
    FROM proba_pluie_station_jour
    WHERE station_id = '{station_id}'
    AND date = '{date}'
    """

    # Exécution de la requête et chargement dans un DataFrame :
    df = pd.read_sql(query, conn)

    # Fermeture de la connexion :
    conn.close()

    # Vérification de la présence de données :
    if df.empty:
        return {"error": "Aucune donnée trouvée"}

    # Récupération de la première ligne :
    row = df.iloc[0]

    # Retour des données sous forme JSON :
    return {
        "station_id": row["station_id"],
        "date": row["date"],
        "proba_pluie": float(row["proba_pluie"]),
        "interpretation": row["Interpretation"],
        "probabilite": row["Probabilité"]
    }

# Endpoint permettant de récupérer toutes les données
@app.get("/all_predictions")
def get_all_predictions():

    # Connexion à la base
    conn = get_connection()

    query = "SELECT * FROM proba_pluie_station_jour"

    df = pd.read_sql(query, conn)
    conn.close()

    # Conversion du DataFrame en format JSON
    return df.to_dict(orient="records")
