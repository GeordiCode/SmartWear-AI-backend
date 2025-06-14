# === bandit_manager.py ===
import torch
import torch.nn as nn
import torch.optim as optim
from collections import defaultdict
import random

# Mapeo fijo
EMOTIONS = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted', 'neutral']
COLOR_LIST = [
    "black", "white", "blue", "grey", "red", "yellow", "green",
    "pink", "orange", "brown", "purple", "silver", "cyan", "olive", "beige", "light blue"
]

def encode_features(emotion, item):
    emotion_vector = [1 if emotion == emo else 0 for emo in EMOTIONS]
    color = item.get("baseColour", "").lower()
    color_vector = [1 if color == c else 0 for c in COLOR_LIST]
    return torch.tensor(emotion_vector + color_vector, dtype=torch.float)

# === Modelo mejorado ===
class ImprovedBanditNet(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        if x.dim() == 1:
            x = x.unsqueeze(0)  # Asegura que tenga batch_size > 1
        return self.model(x)

# === Clase Bandido ===
class MultiArmedBandit:
    def __init__(self, epsilon=0.2, lr=0.01, use_improved=True):
        self.epsilon = epsilon
        self.device = torch.device("cpu")
        self.input_dim = len(EMOTIONS) + len(COLOR_LIST)

        model_cls = ImprovedBanditNet if use_improved else BanditNet
        self.net = model_cls(self.input_dim).to(self.device)

        self.optimizer = optim.Adam(self.net.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()
        self.counts = defaultdict(lambda: defaultdict(int))

    def choose(self, emotion, options):
        if not options:
            return None

        if random.random() < self.epsilon:
            return random.choice(options)

        scored = []
        for item in options:
            x = encode_features(emotion, item).to(self.device)
            with torch.no_grad():
                score = self.net(x).item()
            scored.append((score, item))

        return max(scored, key=lambda x: x[0])[1]

    def choose_multiple(self, emotion, options, k=10):
        if not options:
            return []

        scored = []
        for item in options:
            x = encode_features(emotion, item).to(self.device)
            with torch.no_grad():
                score = self.net(x).item()
            scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        selected = []
        used_ids = set()
        tries = 0

        while len(selected) < min(k, len(scored)) and tries < 50:
            if random.random() < self.epsilon:
                _, candidate = random.choice(scored)
            else:
                _, candidate = scored[len(selected)]

            if candidate["id"] not in used_ids:
                used_ids.add(candidate["id"])
                selected.append(candidate)
            tries += 1

        return selected

    def update(self, emotion, item_id, reward):
        for item in self._last_seen_items:
            if item["id"] == item_id:
                x = encode_features(emotion, item).to(self.device)
                y_true = torch.tensor([reward], dtype=torch.float).to(self.device)
                y_pred = self.net(x)
                loss = self.loss_fn(y_pred, y_true)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                break

    def set_last_seen_items(self, emotion, items):
        self._last_seen_items = items

# === Modelo simple opcional ===
class BanditNet(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.model(x)
