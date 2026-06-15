let gameOver = false;
let historyMax = 0;
let winNotified = false;
let dialogOpen = false;

const maxValueEl = document.getElementById('maxValue');
const winModal = document.getElementById('winModal');
const gameOverModal = document.getElementById('gameOverModal');

function hideAllDialogs() {
    winModal.style.display = 'none';
    gameOverModal.style.display = 'none';
    dialogOpen = false;
}

function showWinDialog() {
    dialogOpen = true;
    winModal.style.display = 'flex';
}

function showGameOverDialog() {
    dialogOpen = true;
    gameOverModal.style.display = 'flex';
}

function loadHistoryMax() {
    const saved = localStorage.getItem('2048_max');
    historyMax = saved ? parseInt(saved) : 0;
    maxValueEl.textContent = historyMax;
}

function saveHistoryMax(value) {
    if (value > historyMax) {
        historyMax = value;
        localStorage.setItem('2048_max', historyMax);
        maxValueEl.textContent = historyMax;
    }
}

let touchStartX = 0;
let touchStartY = 0;

function initTouchSupport() {
    document.addEventListener('touchstart', (e) => {
        if (dialogOpen) return;
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }, { passive: true });

    document.addEventListener('touchmove', (e) => {
        if (dialogOpen) return;
        e.preventDefault();
    }, { passive: false });

    document.addEventListener('touchend', (e) => {
        if (dialogOpen) return;
        const dx = e.changedTouches[0].clientX - touchStartX;
        const dy = e.changedTouches[0].clientY - touchStartY;
        const absDx = Math.abs(dx);
        const absDy = Math.abs(dy);
        const minSwipe = 30;

        if (Math.max(absDx, absDy) < minSwipe) return;

        if (absDx > absDy) {
            move(dx > 0 ? 'right' : 'left');
        } else {
            move(dy > 0 ? 'down' : 'up');
        }
    }, { passive: true });
}

function initEventListeners() {
    document.getElementById('continueBtn').addEventListener('click', () => {
        hideAllDialogs();
        if (!gameOver && isGameOver(board)) {
            gameOver = true;
            showGameOverDialog();
        }
    });

    document.getElementById('newGameFromWinBtn').addEventListener('click', () => {
        initBoard();
        hideAllDialogs();
    });

    document.getElementById('newGameFromOverBtn').addEventListener('click', () => {
        initBoard();
        hideAllDialogs();
    });

    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', () => move(btn.dataset.dir));
    });

    document.getElementById('resetBtn').addEventListener('click', initBoard);

    window.addEventListener('keydown', (e) => {
        if (dialogOpen) {
            e.preventDefault();
            return;
        }
        const key = e.key;
        if (key === 'ArrowUp' || key === 'w' || key === 'W') { e.preventDefault(); move('up'); }
        else if (key === 'ArrowDown' || key === 's' || key === 'S') { e.preventDefault(); move('down'); }
        else if (key === 'ArrowLeft' || key === 'a' || key === 'A') { e.preventDefault(); move('left'); }
        else if (key === 'ArrowRight' || key === 'd' || key === 'D') { e.preventDefault(); move('right'); }
    });

    initTouchSupport();
}
