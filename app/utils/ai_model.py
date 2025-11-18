import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import chess
import os
import traceback

# ------------------------------------------------------------
# 🧩 Piece → Plane Mapping
# ------------------------------------------------------------
PIECE_TO_PLANE = {
    chess.PAWN: 0,
    chess.KNIGHT: 1,
    chess.BISHOP: 2,
    chess.ROOK: 3,
    chess.QUEEN: 4,
    chess.KING: 5
}

# ------------------------------------------------------------
# ♟️ FEN → Tensor Conversion
# ------------------------------------------------------------
def fen_to_tensor(fen: str) -> torch.Tensor:
    """Convert FEN into a 12×8×8 binary tensor for the CNN."""
    try:
        board = chess.Board(fen.split()[0])
    except Exception as e:
        print(f"⚠️ Invalid FEN: {fen} ({e})")
        return torch.zeros((12, 8, 8), dtype=torch.float32)

    planes = np.zeros((12, 8, 8), dtype=np.float32)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        row = 7 - (square // 8)
        col = square % 8
        idx = PIECE_TO_PLANE[piece.piece_type]
        plane = idx if piece.color == chess.WHITE else idx + 6
        planes[plane, row, col] = 1.0

    return torch.tensor(planes, dtype=torch.float32)


# ------------------------------------------------------------
# 🧠 CNN Model Definition
# ------------------------------------------------------------
class ChessNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(12, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1)
        )
        self.flatten = nn.Flatten()
        self.fc_common = nn.Sequential(
            nn.Linear(256, 256),
            nn.ReLU()
        )
        self.head_from = nn.Linear(256, 64)
        self.head_to = nn.Linear(256, 64)

    def forward(self, x):
        x = self.conv(x)
        x = self.flatten(x)
        x = self.fc_common(x)
        return self.head_from(x), self.head_to(x)


# ------------------------------------------------------------
# ⚙️ Model Initialization
# ------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_PATH = os.path.join(BASE_DIR, "models", "chess_cnn.pth")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_model = ChessNet().to(device)
if os.path.exists(MODEL_PATH):
    _model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    _model.eval()
    print(f"✅ Loaded trained model from: {MODEL_PATH}")
else:
    raise FileNotFoundError(f"❌ Trained model not found at: {MODEL_PATH}")


# ------------------------------------------------------------
# 🧮 Helper Function
# ------------------------------------------------------------
def idx_to_square(idx: int) -> str:
    """Convert a square index (0–63) → algebraic notation."""
    return chess.square_name(idx)


# ------------------------------------------------------------
# 🧠 AI Move Prediction (Model-Only)
# ------------------------------------------------------------

def get_ai_move(fen: str):
    """
    Predict AI move using your trained CNN model only.
    Selects the *most confident legal move* based on model output.
    """
    try:
        print(f"\n=== ♟️ New Move Request ===")
        print(f"Received FEN: {fen}")

        board = chess.Board(fen)
        if board.is_game_over():
            print("🏁 Game over — no legal moves left.")
            return None

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            print("⚠️ No legal moves found.")
            return None

        # Convert FEN to tensor
        x = fen_to_tensor(fen).unsqueeze(0).to(device)
        with torch.no_grad():
            pred_from, pred_to = _model(x)
            probs_from = F.softmax(pred_from, dim=1).cpu().numpy().flatten()
            probs_to = F.softmax(pred_to, dim=1).cpu().numpy().flatten()

        # Score each legal move
        legal_scores = []
        for move in legal_moves:
            from_sq, to_sq = move.from_square, move.to_square
            score = float(probs_from[from_sq]) * float(probs_to[to_sq])
            legal_scores.append((move, score))

        # Pick best move
        best_move, best_score = max(legal_scores, key=lambda x: x[1])
        print(f"🤖 ThinkMate Move: {best_move.uci()} | Confidence: {best_score:.6f}")

        # Return in UCI format (like "e2e4") — frontend understands this
        return best_move.uci()

    except Exception as e:
        print("🔥 ERROR in get_ai_move():")
        traceback.print_exc()
        return None



# ------------------------------------------------------------
# 🧪 Standalone Test
# ------------------------------------------------------------
if __name__ == "__main__":
    sample_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    print("Testing ThinkMate model-only move prediction...")
    move = get_ai_move(sample_fen)
    print("Predicted move:", move)
