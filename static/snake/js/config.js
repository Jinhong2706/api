var SnakeGame = SnakeGame || {};

SnakeGame.canvas = document.getElementById('gameCanvas');
SnakeGame.ctx = SnakeGame.canvas.getContext('2d');
SnakeGame.currentScoreSpan = document.getElementById('currentScore');
SnakeGame.bestScoreSpan = document.getElementById('bestScore');
SnakeGame.modeButtons = document.querySelectorAll('.mode-btn');
SnakeGame.colorSwatches = document.querySelectorAll('.swatch');
SnakeGame.restartBtn = document.getElementById('restartBtn');
SnakeGame.pauseBtn = document.getElementById('pauseBtn');
SnakeGame.canvasWrapper = document.getElementById('canvasWrapper');
SnakeGame.dpad = document.getElementById('dpad');
SnakeGame.toggleDpadBtn = document.getElementById('toggleDpadBtn');
SnakeGame.hintEl = document.getElementById('hint');

SnakeGame.isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);

if (SnakeGame.isTouchDevice) {
    SnakeGame.GRID = 20;
    SnakeGame.COLS = 20;
    SnakeGame.ROWS = 20;
} else {
    SnakeGame.GRID = 22;
    SnakeGame.COLS = 24;
    SnakeGame.ROWS = 24;
}
SnakeGame.SIZE = SnakeGame.COLS * SnakeGame.GRID;

SnakeGame.canvas.width = SnakeGame.SIZE;
SnakeGame.canvas.height = SnakeGame.SIZE;

SnakeGame.startBtnW = Math.round(SnakeGame.SIZE * 0.45);
SnakeGame.startBtnH = Math.round(SnakeGame.SIZE * 0.135);
SnakeGame.startBtnX = (SnakeGame.SIZE - SnakeGame.startBtnW) / 2;
SnakeGame.startBtnY = (SnakeGame.SIZE - SnakeGame.startBtnH) / 2 - Math.round(SnakeGame.SIZE * 0.02);
SnakeGame.startBtnRadius = Math.round(SnakeGame.SIZE * 0.04);

SnakeGame.pauseBarW = Math.round(SnakeGame.SIZE * 0.035);
SnakeGame.pauseBarH = Math.round(SnakeGame.SIZE * 0.12);
SnakeGame.pauseBarGap = Math.round(SnakeGame.SIZE * 0.045);
SnakeGame.pauseIconCX = SnakeGame.SIZE / 2;
SnakeGame.pauseIconCY = SnakeGame.SIZE / 2 - Math.round(SnakeGame.SIZE * 0.025);
SnakeGame.pauseBarRadius = Math.round(SnakeGame.SIZE * 0.01);

SnakeGame.notifyDialogW = Math.round(SnakeGame.SIZE * 0.68);
SnakeGame.notifyDialogH = Math.round(SnakeGame.SIZE * 0.40);
SnakeGame.notifyDialogX = Math.round((SnakeGame.SIZE - SnakeGame.notifyDialogW) / 2);
SnakeGame.notifyDialogY = Math.round((SnakeGame.SIZE - SnakeGame.notifyDialogH) / 2);
SnakeGame.notifyDialogR = Math.round(SnakeGame.SIZE * 0.03);
SnakeGame.notifyBtnW = Math.round(SnakeGame.notifyDialogW * 0.4);
SnakeGame.notifyBtnH = Math.round(SnakeGame.SIZE * 0.09);
SnakeGame.notifyBtnR = Math.round(SnakeGame.SIZE * 0.02);
SnakeGame.notifyBtnX = SnakeGame.notifyDialogX + Math.round((SnakeGame.notifyDialogW - SnakeGame.notifyBtnW) / 2);
SnakeGame.notifyBtnY = SnakeGame.notifyDialogY + SnakeGame.notifyDialogH - SnakeGame.notifyBtnH - Math.round(SnakeGame.SIZE * 0.05);

SnakeGame.confirmDialogW = Math.round(SnakeGame.SIZE * 0.72);
SnakeGame.confirmDialogH = Math.round(SnakeGame.SIZE * 0.4);
SnakeGame.confirmDialogX = Math.round((SnakeGame.SIZE - SnakeGame.confirmDialogW) / 2);
SnakeGame.confirmDialogY = Math.round((SnakeGame.SIZE - SnakeGame.confirmDialogH) / 2);
SnakeGame.confirmDialogR = Math.round(SnakeGame.SIZE * 0.03);
SnakeGame.confirmBtnW = Math.round(SnakeGame.confirmDialogW * 0.35);
SnakeGame.confirmBtnH = Math.round(SnakeGame.SIZE * 0.1);
SnakeGame.confirmBtnR = Math.round(SnakeGame.SIZE * 0.02);
SnakeGame.confirmBtnY = SnakeGame.confirmDialogY + SnakeGame.confirmDialogH - SnakeGame.confirmBtnH - Math.round(SnakeGame.SIZE * 0.04);
SnakeGame.confirmBtnX = SnakeGame.confirmDialogX + SnakeGame.confirmDialogW / 2 - SnakeGame.confirmBtnW - Math.round(SnakeGame.SIZE * 0.03);
SnakeGame.cancelBtnX = SnakeGame.confirmDialogX + SnakeGame.confirmDialogW / 2 + Math.round(SnakeGame.SIZE * 0.03);

SnakeGame.getCanvasCoords = function(clientX, clientY) {
    const rect = SnakeGame.canvas.getBoundingClientRect();
    const scaleX = SnakeGame.SIZE / rect.width;
    const scaleY = SnakeGame.SIZE / rect.height;
    return {
        x: (clientX - rect.left) * scaleX,
        y: (clientY - rect.top) * scaleY
    };
};

SnakeGame.isInStartBtn = function(cx, cy) {
    return cx >= SnakeGame.startBtnX && cx <= SnakeGame.startBtnX + SnakeGame.startBtnW &&
           cy >= SnakeGame.startBtnY && cy <= SnakeGame.startBtnY + SnakeGame.startBtnH;
};

SnakeGame.isInConfirmBtn = function(cx, cy) {
    return cx >= SnakeGame.confirmBtnX && cx <= SnakeGame.confirmBtnX + SnakeGame.confirmBtnW &&
           cy >= SnakeGame.confirmBtnY && cy <= SnakeGame.confirmBtnY + SnakeGame.confirmBtnH;
};

SnakeGame.isInCancelBtn = function(cx, cy) {
    return cx >= SnakeGame.cancelBtnX && cx <= SnakeGame.cancelBtnX + SnakeGame.confirmBtnW &&
           cy >= SnakeGame.confirmBtnY && cy <= SnakeGame.confirmBtnY + SnakeGame.confirmBtnH;
};
