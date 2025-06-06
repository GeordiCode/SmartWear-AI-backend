from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from typing import List
import json
import random
import csv
import pandas as pd


from bandits.bandit_manager import MultiArmedBandit

app = FastAPI()
bandit = MultiArmedBandit()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

emotion_fallback = {
    "neutral": "happy",
    "disgusted": "sad",
    "fearful": "surprised"
}
gender_map = {
    "male": "men",
    "female": "women"
}
emotion_colors = {
    "happy": ["yellow", "orange", "pink", "white"],
    "sad": ["blue", "grey", "black", "brown", "purple"],
    "angry": ["red", "black", "orange"],
    "surprised": ["white", "silver", "cyan"],
    "fearful": ["grey", "black", "blue", "purple"],
    "disgusted": ["green", "brown", "olive", "grey"],
    "neutral": ["beige", "white", "grey", "light blue"],
}

recom_path = Path("recommendations/recommendations.json")
if not recom_path.exists():
    raise FileNotFoundError("❌ El archivo recommendations.json no existe.")

with open(recom_path, "r", encoding="utf-8") as f:
    RECOMMENDATIONS = json.load(f)

feedback_path = Path("feedback.json")
if not feedback_path.exists():
    feedback_path.write_text("[]", encoding="utf-8")

ropa_df = pd.read_csv("data/prendas.csv")
ropa_df.fillna("", inplace=True)

@app.get("/api/recommendations/{emotion}")
async def get_recommendations(emotion: str, request: Request):
    gender = request.query_params.get("gender", "").lower()
    categoria = request.query_params.get("categoria", "").lower()

    mapped_emotion = emotion_fallback.get(emotion.lower(), emotion.lower())
    mapped_gender = gender_map.get(gender, gender)
    preferred_colors = emotion_colors.get(mapped_emotion, [])

    emotion_data = RECOMMENDATIONS.get(mapped_emotion, [])
    filtered_items = [
        item for item in emotion_data
        if (not mapped_gender or item.get("gender", "").lower() == mapped_gender)
        and (not categoria or item.get("category", "").lower() == categoria)
        and (item.get("baseColour", "").strip().lower() in [c.lower() for c in preferred_colors])
    ]

    combined = filtered_items[:8]

    if len(combined) < 12:
        prendas_path = Path("data/prendas.csv")
        if prendas_path.exists():
            with open(prendas_path, "r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                colores_permitidos = [c.strip().lower() for c in preferred_colors]
                colores_excluidos = ["brown", "dark grey", "dark green", "dark blue", "dark red", "maroon"]

                extras = [
                    {
                        "id": row["id"],
                        "link": row["link"],
                        "productDisplayName": row["productDisplayName"],
                        "gender": row["gender"],
                        "category": row["categoria_general"],
                        "baseColour": row.get("baseColour", "").strip().lower()
                    }
                    for row in reader
                    if row.get("categoria_general", "").lower() == categoria
                    and row.get("gender", "").lower() in [mapped_gender, "unisex"]
                    and row.get("baseColour", "").strip().lower() in colores_permitidos
                    and row.get("baseColour", "").strip().lower() not in colores_excluidos
                ]

                random.shuffle(extras)
                combined += extras[:(12 - len(combined))]

    bandit.set_last_seen_items(mapped_emotion, combined)
    selected = bandit.choose_multiple(mapped_emotion, combined, k=min(12, len(combined)))
    return selected



class ItemInput(BaseModel):
    id: str
    productDisplayName: str
    link: str
    gender: str = ""
    category: str = ""
    baseColour: str = ""

class RecommendationRequest(BaseModel):
    emotion: str
    items: List[ItemInput]

# 🔁 NUEVO endpoint POST para recibir JSON y dar recomendación con la red neuronal NO MOVER!!!
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class TinderRecommendationInput(BaseModel):
    emotion: str
    gender: str
    category: str

@app.post("/api/tinder-recommendation")
async def tinder_recommendation(data: TinderRecommendationInput):
    print("📩 Recibido POST con:", data.dict())
    emotion = data.emotion.lower()
    gender = data.gender.lower()
    # Normalizar categoría antes de seguir
    categoria_raw = data.category.lower()
    categoria = "falda/vestido" if categoria_raw == "falda-vestido" else categoria_raw
    

    mapped_emotion = emotion_fallback.get(emotion, emotion)
    mapped_gender = gender_map.get(gender, gender)
    preferred_colors = emotion_colors.get(mapped_emotion, [])

    emotion_data = RECOMMENDATIONS.get(mapped_emotion, [])
    filtered_items = [
        item for item in emotion_data
        if (not mapped_gender or item.get("gender", "").lower() == mapped_gender)
        and (not categoria or item.get("category", "").lower() == categoria)
        and (item.get("baseColour", "").strip().lower() in [c.lower() for c in preferred_colors])
    ]

    combined = filtered_items[:8]

    if len(combined) < 12:
        prendas_path = Path("data/prendas.csv")
        if prendas_path.exists():
            with open(prendas_path, "r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                colores_permitidos = [c.strip().lower() for c in preferred_colors]
                colores_excluidos = ["brown", "dark grey", "dark green", "dark blue", "dark red", "maroon"]

                extras = [
                    {
                        "id": row["id"],
                        "link": row["link"],
                        "productDisplayName": row["productDisplayName"],
                        "gender": row["gender"],
                        "category": row["categoria_general"],
                        "baseColour": row.get("baseColour", "").strip().lower()
                    }
                    for row in reader
                    if row.get("categoria_general", "").lower() == categoria
                    and row.get("gender", "").lower() in [mapped_gender, "unisex"]
                    and row.get("baseColour", "").strip().lower() in colores_permitidos
                    and row.get("baseColour", "").strip().lower() not in colores_excluidos
                ]

                random.shuffle(extras)
                combined += extras[:(12 - len(combined))]

    if not combined:
        return JSONResponse(status_code=404, content={"message": "No hay recomendaciones disponibles"})

    bandit.set_last_seen_items(mapped_emotion, combined)
    recommended_items = bandit.choose_multiple(mapped_emotion, combined, k=10)

    return {"recommendations": recommended_items}

"""
@app.post("/api/tinder-feedback")
async def tinder_feedback(request: Request):
    body = await request.json()
    emotion = body.get("emotion")
    item_id = body.get("item_id")
    reward = float(body.get("reward", 1.0))

    if not emotion or not item_id:
        return {"error": "Datos incompletos"}

    bandit.update(emotion, item_id, reward)

    with open(feedback_path, "r", encoding="utf-8") as f:
        feedbacks = json.load(f)

    feedbacks.append({"emotion": emotion, "item_id": item_id, "reward": reward})

    with open(feedback_path, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2, ensure_ascii=False)

    return {"message": "Feedback registrado"}
"""

def cargar_feedbacks(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Si no existe o está vacío o corrupto, lo inicializamos como lista vacía
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    
@app.post("/api/tinder-feedback-batch")
async def tinder_feedback_batch(request: Request):
    body = await request.json()
    emotion = body.get("emotion")
    likes = body.get("likes", [])

    if not emotion or not isinstance(likes, list):
        return {"error": "Datos incompletos o inválidos"}

    feedbacks = cargar_feedbacks(feedback_path)

    for item in likes:
        item_id = item.get("id")
        if not item_id:
            continue

        bandit.update(emotion, item_id, 1.0)
        feedbacks.append({"emotion": emotion, "item_id": item_id, "reward": 1.0})

    with open(feedback_path, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2, ensure_ascii=False)

    return {"message": f"{len(likes)} feedbacks registrados"}

@app.post("/api/feedback/")
async def register_feedback(request: Request):
    body = await request.json()
    emotion = body.get("emotion")
    item_id = body.get("item_id")
    reward = float(body.get("reward", 1.0))

    if not emotion or not item_id:
        return {"error": "Faltan datos para registrar feedback."}

    bandit.update(emotion, item_id, reward)

    with open(feedback_path, "r", encoding="utf-8") as f:
        feedbacks = json.load(f)

    feedbacks.append({
        "emotion": emotion,
        "item_id": item_id,
        "reward": reward
    })

    with open(feedback_path, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2, ensure_ascii=False)

    return {"message": "Feedback recibido"}

@app.get("/api/ping")
async def ping():
    return {"ok": True, "message": "pong"}



app.mount("/data", StaticFiles(directory="data"), name="data")
