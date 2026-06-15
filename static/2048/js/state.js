let board = [];
let lastAddedPos = null;

function createGridCells() {
    const gridEl = document.getElementById('grid');
    gridEl.innerHTML = '';
    for (let i = 0; i < SIZE * SIZE; i++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.setAttribute('data-value', '0');
        gridEl.appendChild(cell);
    }
}

function addRandomTile() {
    const emptyCells = getEmptyCells(board);
    if (emptyCells.length === 0) return false;
    const { r, c } = emptyCells[Math.floor(Math.random() * emptyCells.length)];
    board[r][c] = Math.random() < 0.9 ? 2 : 4;
    lastAddedPos = { r, c };
    return true;
}

function getEmptyCells(board) {
    const cells = [];
    for (let r = 0; r < SIZE; r++) {
        for (let c = 0; c < SIZE; c++) {
            if (board[r][c] === 0) cells.push({ r, c });
        }
    }
    return cells;
}

function getCurrentMax() {
    let max = 0;
    for (let r = 0; r < SIZE; r++) {
        for (let c = 0; c < SIZE; c++) {
            if (board[r][c] > max) max = board[r][c];
        }
    }
    return max;
}

function initBoard() {
    board = Array.from({ length: SIZE }, () => Array(SIZE).fill(0));
    gameOver = false;
    winNotified = false;
    lastAddedPos = null;
    addRandomTile();
    addRandomTile();
    renderBoard();
    hideAllDialogs();
}

function moveLeft() {
    let moved = false;
    for (let r = 0; r < SIZE; r++) {
        const oldRow = [...board[r]];
        const newRow = slideAndMerge(oldRow);
        if (newRow.join(',') !== oldRow.join(',')) moved = true;
        board[r] = newRow;
    }
    return moved;
}

function moveRight() {
    let moved = false;
    for (let r = 0; r < SIZE; r++) {
        const originalRow = board[r];
        const reversed = [...originalRow].reverse();
        const merged = slideAndMerge(reversed);
        const newRow = merged.reverse();
        if (newRow.join(',') !== originalRow.join(',')) {
            moved = true;
            board[r] = newRow;
        }
    }
    return moved;
}

function moveUp() {
    let moved = false;
    for (let c = 0; c < SIZE; c++) {
        const column = [board[0][c], board[1][c], board[2][c], board[3][c]];
        const newColumn = slideAndMerge(column);
        if (newColumn.join(',') !== column.join(',')) moved = true;
        for (let r = 0; r < SIZE; r++) board[r][c] = newColumn[r];
    }
    return moved;
}

function moveDown() {
    let moved = false;
    for (let c = 0; c < SIZE; c++) {
        const column = [board[3][c], board[2][c], board[1][c], board[0][c]];
        const newColumn = slideAndMerge(column);
        const finalColumn = newColumn.reverse();
        const originalColumn = [board[0][c], board[1][c], board[2][c], board[3][c]];
        if (finalColumn.join(',') !== originalColumn.join(',')) moved = true;
        for (let r = 0; r < SIZE; r++) board[r][c] = finalColumn[r];
    }
    return moved;
}

function move(direction) {
    if (gameOver || dialogOpen) return;
    let moved = false;
    if (direction === 'left') moved = moveLeft();
    else if (direction === 'right') moved = moveRight();
    else if (direction === 'up') moved = moveUp();
    else if (direction === 'down') moved = moveDown();
    if (moved) {
        addRandomTile();
        renderBoard();
    } else {
        checkAndShowGameOver();
    }
}

function checkAndShowGameOver() {
    if (!gameOver && !dialogOpen && isGameOver(board)) {
        gameOver = true;
        showGameOverDialog();
    }
}

function renderBoard() {
    const gridEl = document.getElementById('grid');
    const cells = gridEl.children;
    const currentMax = getCurrentMax();
    saveHistoryMax(currentMax);

    if (currentMax >= 2048 && !winNotified && !gameOver) {
        winNotified = true;
        showWinDialog();
    }

    for (let i = 0, r = 0; r < SIZE; r++) {
        for (let c = 0; c < SIZE; c++, i++) {
            const val = board[r][c];
            cells[i].textContent = val === 0 ? '' : val;
            cells[i].setAttribute('data-value', val);
            cells[i].classList.remove('pop-in');
        }
    }

    if (lastAddedPos) {
        const cellIndex = lastAddedPos.r * SIZE + lastAddedPos.c;
        cells[cellIndex].classList.add('pop-in');
        lastAddedPos = null;
    }

    if (!gameOver && isGameOver(board)) {
        gameOver = true;
        showGameOverDialog();
    }
}
