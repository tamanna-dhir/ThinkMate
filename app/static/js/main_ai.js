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

  setTimeout(fetchAIMove, 700);
}

// ---------------------------------------------
// 🤖 Fetch AI Move (correct endpoint!)
// ---------------------------------------------
async function fetchAIMove() {
  const fen = game.fen();

  try {
    console.log("📤 Sending FEN to backend:", fen);

    const response = await fetch("/move", {   // ✅ Correct Flask route
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({ fen })
    });

    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text();
      console.error("❌ Non-JSON response from backend:", text);
      alert("Server returned invalid data. Check backend logs.");
      return;
    }

    const data = await response.json();
    console.log("📥 AI Response:", data);

    if (data.move) {
  const move = game.move(data.move, { sloppy: true });

      if (move) {
        board.position(game.fen());
        moveHistory.push(move.san);
        updateHistory();
        updateStatus();
      } else {
        console.warn("⚠️ Invalid AI move:", data.ai_move);
        alert("AI generated an invalid move.");
      }
    } else {
      console.error("❌ AI move missing:", data);
      alert("AI failed to respond. Check Flask logs.");
    }
  } catch (err) {
    console.error("🚨 Error contacting backend:", err);
    alert("Could not reach backend. Make sure Flask is running.");
  }
}

// ---------------------------------------------
// ♟️ Board UI Helpers
// ---------------------------------------------
function updateHistory() {
  const el = document.getElementById('move-history');
  if (el) el.innerHTML = moveHistory.join(' • ');
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

  document.getElementById('status').textContent = status;
}

// ---------------------------------------------
// 🎮 Color Selection
// ---------------------------------------------
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById("whiteBtn").onclick = () => initBoard('white');
  document.getElementById("blackBtn").onclick = () => initBoard('black');
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

  document.getElementById('color-choice').style.display = 'none';
  document.getElementById('board-container').style.display = 'block';

  console.log(`✅ Initialized as ${color}`);
  if (color === 'black') setTimeout(fetchAIMove, 500);
}
