import torch
import torch.nn.functional as F
import pandas as pd
import chess
import os
from sklearn.model_selection import train_test_split
from app.utils.ai_model import fen_to_tensor, ChessNet  # uses your trained model class

# ---------------------------------------------------------
#  Load model
# ---------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(BASE_DIR, "models", "chess_cnn.pth")
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "processed.csv")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = ChessNet().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()
print(f"✅ Loaded model from {MODEL_PATH}")

# ---------------------------------------------------------
#  Load dataset
# ---------------------------------------------------------
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=["FEN", "Move"])

# Split data into train/test sets
train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)
print(f"Dataset size: {len(df)} | Test samples: {len(test_data)}")

# ---------------------------------------------------------
#  Evaluate
# ---------------------------------------------------------
correct = 0
total = 0

for _, row in test_data.iterrows():
    fen = row["FEN"]
    true_move = row["Move"]

    try:
        x = fen_to_tensor(fen).unsqueeze(0).to(device)
        with torch.no_grad():
            pred_from, pred_to = model(x)
            probs_from = F.softmax(pred_from, dim=1).cpu().numpy().flatten()
            probs_to = F.softmax(pred_to, dim=1).cpu().numpy().flatten()

        board = chess.Board(fen)
        legal_moves = list(board.legal_moves)

        # Choose the model’s best predicted legal move
        best_move, best_score = max(
            ((move, probs_from[move.from_square] * probs_to[move.to_square]) for move in legal_moves),
            key=lambda x: x[1]
        )

        pred_move = best_move.uci()

        if pred_move == true_move:
            correct += 1
        total += 1

    except Exception as e:
        continue

accuracy = correct / total * 100 if total > 0 else 0
print(f"\n Model Accuracy: {accuracy:.2f}% ({correct}/{total})")

