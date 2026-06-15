const SIZE = 4;

function slideAndMerge(line) {
    let filtered = line.filter(v => v !== 0);
    for (let i = 0; i < filtered.length - 1; i++) {
        if (filtered[i] === filtered[i + 1]) {
            filtered[i] *= 2;
            filtered[i + 1] = 0;
        }
    }
    filtered = filtered.filter(v => v !== 0);
    while (filtered.length < SIZE) filtered.push(0);
    return filtered;
}

function isGameOver(board) {
    for (let r = 0; r < SIZE; r++)
        for (let c = 0; c < SIZE; c++)
            if (board[r][c] === 0) return false;
    for (let r = 0; r < SIZE; r++)
        for (let c = 0; c < SIZE - 1; c++)
            if (board[r][c] === board[r][c + 1]) return false;
    for (let c = 0; c < SIZE; c++)
        for (let r = 0; r < SIZE - 1; r++)
            if (board[r][c] === board[r + 1][c]) return false;
    return true;
}
