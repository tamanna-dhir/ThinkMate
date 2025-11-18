# ThinkMate/app/routes.py
from flask import Blueprint, render_template, jsonify, request
from app.utils.ai_model import get_ai_move
import traceback

# ----------------------------
# 📘 Create Blueprint
# ----------------------------
main = Blueprint('main', __name__)

# ----------------------------
# 🌐 HTML Page Routes
# ----------------------------
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/play')
def play():
    return render_template('play.html')

@main.route('/multiplayer')
def multiplayer():
    return render_template('multiplayer.html')

@main.route('/play-ai')
def play_ai():
    return render_template('play_ai.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/watch')
def watch():
    return render_template('watch.html')


# ----------------------------
# 🤖 AI Move API Endpoint
# ----------------------------
@main.route("/move", methods=["POST"])
def get_ai_move_route():
    try:
        data = request.get_json()
        fen = data.get("fen", "")
        print("\n=== 🎯 Received FEN from frontend ===")
        print(fen)

        move = get_ai_move(fen)
        print(f"✅ AI move returned: {move}")

        return jsonify({"move": move})
    except Exception as e:
        print("🔥 ERROR in /get_ai_move route:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
