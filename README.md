
# 🧠 Backend - SmartWear AI

Este backend está diseñado para alimentar una aplicación web de recomendación de ropa basada en el estado emocional del usuario. Utiliza técnicas de aprendizaje por refuerzo (Multi-Armed Bandit), una red neuronal y lógica de filtrado para proporcionar recomendaciones personalizadas de prendas.

## 🚀 Tecnologías Usadas

- 🐍 Python 3.12
- ⚡ FastAPI
- 🔁 Uvicorn
- 🤖 PyTorch (Red neuronal para aprendizaje por refuerzo)
- 🧪 Pandas (procesamiento del CSV)
- 📦 JSON y CSV como estructuras de datos
- 💡 Algoritmo Multi-Armed Bandit personalizado
- 🎨 Reglas heurísticas para emociones y categorías

---

## 📁 Estructura del Proyecto

```
backend/
├── app.py                         # Archivo principal con todos los endpoints
├── bandit_manager.py              # Modelo de aprendizaje por refuerzo y red neuronal
├── generate_recommendations.py    # Script para preprocesar el CSV y generar recomendaciones base por emoción
├── recommendations/
│   ├── recommendations.json       # Archivo JSON con las recomendaciones generadas
│   └── recomendaciones_emocion_categoria.csv
├── data/
│   └── prendas.csv                # Dataset de prendas base
```

---

## ✅ Funcionalidades Principales

- Recomendación personalizada de prendas basada en:
  - Estado emocional del usuario
  - Género seleccionado
  - Categoría general de la prenda
- Entrenamiento en línea (online learning) con feedback del usuario (`like` o `dislike`)
- Algoritmo de tipo **Multi-Armed Bandit** para balancear exploración y explotación
- Filtro inteligente por color base y categorías específicas
- Recomendaciones tipo "Tinder" que muestran una prenda a la vez
- Actualización dinámica del modelo tras cada retroalimentación

---

## 📡 Endpoints Disponibles (FastAPI)

- `GET /tinder-recommendations`  
  Retorna 1 prenda optimizada según emoción, género y categoría.  
  **Parámetros**: `emotion`, `gender`, `categoria_general`

- `POST /feedback-tinder`  
  Registra la retroalimentación del usuario (like/dislike) y entrena el modelo.  
  **Body JSON**: `emotion`, `id`, `feedback` (1 o 0)

- `GET /prendas`  
  Muestra todas las prendas disponibles en el sistema

- `GET /categorias`  
  Muestra las categorías de ropa filtradas por género

- `GET /recomendaciones-emocion`  
  Muestra recomendaciones basadas en la emoción, sin necesidad de feedback

---

## 🔧 Cómo Ejecutar

Instala dependencias:

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # o 'source venv/bin/activate' en Unix
pip install -r requirements.txt
```

Corre el servidor:

```bash
uvicorn app:app --reload
```

---

## 🧪 Preprocesamiento del Dataset

Antes de ejecutar el backend, asegúrate de generar el archivo `recommendations.json` con:

```bash
python generate_recommendations.py
```

Este script:

- Carga el dataset `prendas.csv`
- Lo filtra por emoción y categoría
- Genera recomendaciones en `recommendations/recommendations.json`

---

## 🧠 Detalles del Modelo Bandit

- Codifica emociones y colores con vectores one-hot
- Red neuronal:
  - Entrada: 23 (7 emociones + 16 colores base)
  - Capa oculta: 32 neuronas + ReLU
  - Salida: puntuación estimada (recompensa)
- Aprende en línea con retroalimentación directa
- Selecciona las mejores prendas por puntuación o aleatoriamente con `epsilon`

---

## 👤 Autores

Proyecto desarrollado por:

- **Jordi Santiago Ledesma Arboleda**  
  [GitHub - GeordiCode](https://github.com/GeordiCode/SmartWear-AI-backend)

- **Diego Llanos**
  ([GitHub](https://github.com/Dife2703/ProyectoGradoRopa))

---

## 📜 Licencia

Este software se desarrolla como parte de un trabajo de grado en Ingeniería de Sistemas y está disponible bajo licencia de uso académico.
