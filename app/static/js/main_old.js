let board = null;
let game = new Chess();
let playerColor = 'white';
let moveHistory = [];

// ---------------------------------------------
// 🧠 Player Move Logic
// ---------------------------------------------
function onDragStart(source, piece) {
  if (
    game.game_over() ||
    (game.turn() === 'w' && playerColor !== 'white') ||
    (game.turn() === 'b' && playerColor !== 'black')
  ) return false;
}

function makeMove(source, target) {
  const move = game.move({ from: source, to: target, promotion: 'q' });
  if (move === null) return 'snapback';

  moveHistory.push(move.san);
  updateHistory();
  updateStatus();

  // ✅ Ask AI to respond
  setTimeout(fetchAIMove, 700);
}

// ---------------------------------------------
// 🤖 Fetch AI Move from Flask Backend
// ---------------------------------------------
async function fetchAIMove() {
  const fen = game.fen();

  try {
    console.log("📤 Sending FEN to backend:", fen);

    const response = await fetch("/move", {  // ✅ Corrected endpoint
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({ fen: fen })
    });

    // ✅ Handle non-JSON responses (like HTML errors)
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text();
      console.error("❌ Non-JSON response from server:", text);
      alert("Server returned invalid response. Check Flask logs.");
      return;
    }

    const data = await response.json();
    console.log("📥 Response from backend:", data);

    if (data.ai_move) {
      const aiMove = data.ai_move.trim();
      console.log("🤖 AI Move received:", aiMove);

      // ✅ Apply AI move
      const move = game.move(aiMove, { sloppy: true });
      if (move) {
        board.position(game.fen());
        moveHistory.push(move.san);
        updateHistory();
        updateStatus();
      } else {
        console.warn("⚠️ Invalid AI move:", aiMove);
        alert("AI generated an invalid move. Model may need retraining.");
      }
    } else {
      console.error("❌ AI move missing:", data);
      alert("AI move could not be generated. Check backend logs.");
    }
  } catch (err) {
    console.error("🚨 Error contacting backend:", err);
    alert("Failed to contact backend. Make sure Flask is running on port 5000.");
  }
}

// ---------------------------------------------
// ♟️ Board UI and Status
// ---------------------------------------------
function updateHistory() {
  const historyElement = document.getElementById('move-history');
  if (historyElement) {
    historyElement.innerHTML = moveHistory.join(' • ');
  }
}

function onDrop(source, target) {
  makeMove(source, target);
}

function onSnapEnd() {
  board.position(game.fen());
}

function updateStatus() {
  const moveColor = game.turn() === 'w' ? 'White' : 'Black';
  let status = `${moveColor} to move`;

  if (game.in_checkmate()) status = "Checkmate!";
  else if (game.in_draw()) status = "Draw!";
  else if (game.in_stalemate()) status = "Stalemate!";

  const statusElement = document.getElementById('status');
  if (statusElement) statusElement.textContent = status;
}

// ---------------------------------------------
// 🎮 Player Color Selection
// ---------------------------------------------
document.addEventListener('DOMContentLoaded', function() {
  const whiteBtn = document.getElementById("whiteBtn");
  const blackBtn = document.getElementById("blackBtn");

  if (whiteBtn) whiteBtn.onclick = () => initBoard('white');
  if (blackBtn) blackBtn.onclick = () => initBoard('black');
});

function initBoard(color) {
  playerColor = color;
  game.reset();

  board = Chessboard('board', {
    draggable: true,
    position: 'start',
    orientation: color,
    onDragStart,
    onDrop,
    onSnapEnd,
    pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
  });

  moveHistory = [];
  updateHistory();
  updateStatus();

  const colorChoice = document.getElementById('color-choice');
  const boardContainer = document.getElementById('board-container');
  if (colorChoice) colorChoice.style.display = 'none';
  if (boardContainer) boardContainer.style.display = 'block';

  console.log(`✅ Board initialized as ${color}`);

  if (color === 'black') setTimeout(fetchAIMove, 500);
}
