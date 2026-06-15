var SnakeGame = SnakeGame || {};

SnakeGame.setupUI = function() {
    SnakeGame.modeButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var spd = parseInt(btn.dataset.speed, 10);
            if (SnakeGame.gameState === 'playing') {
                SnakeGame.setGameState('notify');
                return;
            }
            if (SnakeGame.gameState === 'paused') return;
            if (SnakeGame.gameState === 'idle' || SnakeGame.gameState === 'gameover') {
                SnakeGame.pendingSpeed = spd;
                SnakeGame.prevStateBeforeConfirm = SnakeGame.gameState;
                SnakeGame.setGameState('confirming');
            }
        });
    });

    SnakeGame.colorSwatches.forEach(function(sw) {
        sw.addEventListener('click', function() {
            var color = sw.dataset.color;
            if (color) {
                SnakeGame.bgColor = color;
                SnakeGame.canvas.style.backgroundColor = color;
                SnakeGame.colorSwatches.forEach(function(s) {
                    s.classList.remove('active');
                    if (s.dataset.color === color) s.classList.add('active');
                });
            }
        });
    });

    SnakeGame.restartBtn.addEventListener('click', function() {
        if (SnakeGame.gameState === 'idle') {
            SnakeGame.startFromIdle();
        } else {
            SnakeGame.resetToIdle();
        }
    });

    SnakeGame.pauseBtn.addEventListener('click', function() {
        SnakeGame.togglePause();
    });

    var resizeCanvas = function() {
        var maxW = SnakeGame.canvasWrapper.clientWidth;
        var reservedVSpace = window.innerHeight <= 520 ? 80 : 120;
        var maxH = Math.max(window.innerHeight - reservedVSpace, 200);
        var displaySize = Math.min(maxW, maxH, SnakeGame.SIZE);
        SnakeGame.canvas.style.width = displaySize + 'px';
        SnakeGame.canvas.style.height = displaySize + 'px';
    };
    window.addEventListener('resize', resizeCanvas);
    window.addEventListener('orientationchange', function() {
        setTimeout(resizeCanvas, 150);
    });
    resizeCanvas();
};
