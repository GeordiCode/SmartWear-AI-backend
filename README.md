
# 🧠 Backend - SmartWear AI

Este backend alimenta una aplicación web de recomendación de ropa basada en el estado emocional del usuario, usando un sistema híbrido de lógica heurística y aprendizaje por refuerzo con red neuronal. Se incluye un modelo tipo Multi-Armed Bandit mejorado y una API construida con FastAPI.

## 🚀 Tecnologías Usadas

- 🐍 Python 3.12
- ⚡ FastAPI + Uvicorn
- 🤖 PyTorch (Red neuronal Bandit)
- 🧪 Pandas (procesamiento de CSV)
- 📊 Scikit-learn (evaluación y pruebas)
- 📦 JSON y CSV como fuentes de datos
- 🧠 Multi-Armed Bandit personalizado (exploración/explotación)
- 🧠 Dropout + BatchNorm en modelos
- 📈 Scripts de validación: AUC, ROC, K-Fold, ruido

---

## 📁 Estructura del Proyecto

```
backend/
├── app.py                         # API principal (FastAPI)
├── bandits/
│   └── bandit_manager.py          # Lógica del modelo Bandit (mejorado y simple)
├── recommendations/
│   ├── recommendations.json       # Recomendaciones base por emoción
├── data/
│   └── prendas.csv                # Dataset de entrada
├── feedback.json                  # Historial de retroalimentación
├── scripts/
│   └── generate_recommendations.py    # Script de generación de recomendaciones
```

---

## ✅ Funcionalidades

- 🔍 Recomendaciones por emoción, género y categoría
- 💡 Heurísticas basadas en emociones y colores
- 🎯 Sistema tipo Tinder (selección visual)
- 🧠 Multi-Armed Bandit con red neuronal personalizada
- 🔁 Entrenamiento online con feedback (`like` o `dislike`)
- 📩 Endpoint REST para recibir feedback por lote
- ⚙️ Filtrado dinámico por CSV y JSON

---

## 📡 Endpoints (FastAPI)

- `GET /api/recommendations/{emotion}`  
  Recomendaciones según emoción, género, categoría.

- `POST /api/tinder-recommendation`  
  Endpoint principal para Shinder. Usa Bandit para seleccionar.

- `POST /api/tinder-feedback-batch`  
  Entrena el modelo con una lista de prendas tipo "like".

- `POST /api/feedback/`  
  Feedback individual: item + emoción + recompensa.

- `GET /api/ping`  
  Prueba de vida del servidor.

---

## 🔧 Ejecución

Instala dependencias:

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Ejecuta FastAPI:

```bash
uvicorn app:app --reload
```

Genera las recomendaciones base:

```bash
python generate_recommendations.py
```

---

## 📊 Evaluaciones

El modelo mejorado fue evaluado con:

- ✅ Métricas clásicas: Accuracy, Precision, Recall, F1
- 📈 AUC y curva ROC
- 🔄 Validación cruzada (K-Fold)
- 🔀 Datos ruidosos (5%, 10%, 15%, 20%, 30%)

Scripts disponibles en https://colab.research.google.com/drive/1VlfHfrpQCC2bqrGxICkDt-jUprHXJL7R?usp=sharing para pruebas reproducibles.

---

## 🧠 Modelo Bandit Mejorado

- Entrada: 23 características (7 emociones + 16 colores)
- Arquitectura:
  - Capa 1: Linear(23→64) + LayerNorm + ReLU + Dropout(0.3)
  - Capa 2: Linear(64→32) + ReLU
  - Salida: Linear(32→1) (estimación de recompensa)
- Entrenamiento por retroalimentación (online learning)
- Compatible con feedback tipo lote o individual

---

## 👤 Autores

Proyecto de grado en Ingeniería de Sistemas (Universidad del Valle):

- **Jordi Santiago Ledesma Arboleda**  
  [GitHub](https://github.com/GeordiCode/SmartWear-AI-backend)

- **Diego Llanos**  
  [GitHub](https://github.com/Dife2703/ProyectoGradoRopa)

---

## 📜 Licencia

Uso académico con fines investigativos. Todos los derechos reservados.
