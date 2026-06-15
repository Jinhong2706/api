var SnakeGame = SnakeGame || {};

SnakeGame.setupInput = function() {
    if (!SnakeGame.isTouchDevice) {
        SnakeGame.dpad.style.display = 'none';
        SnakeGame.toggleDpadBtn.style.display = 'inline-block';
        SnakeGame.hintEl.textContent = '方向键 / WASD 控制 | 空格键暂停/继续 | 点击色块切换背景 | 点击画布开始';
    } else {
        SnakeGame.toggleDpadBtn.style.display = 'none';
    }

    document.addEventListener('keydown', function(e) {
        var key = e.key;
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'w', 'W', 'a', 'A', 's', 'S', 'd', 'D', ' ', 'Escape', 'Enter'].includes(key)) {
            e.preventDefault();
        }
        var lowerKey = key.toLowerCase();

        if (SnakeGame.gameState === 'confirming') {
            if (lowerKey === ' ' || lowerKey === 'enter') {
                SnakeGame.confirmSpeedChange();
            } else if (lowerKey === 'escape') {
                SnakeGame.cancelSpeedChange();
            }
            return;
        }

        if (SnakeGame.gameState === 'notify') {
            if (lowerKey === ' ' || lowerKey === 'enter' || lowerKey === 'escape') {
                SnakeGame.setGameState('playing');
            }
            return;
        }

        if (lowerKey === ' ') {
            if (SnakeGame.gameState === 'idle') {
                SnakeGame.startFromIdle();
            } else if (SnakeGame.gameState === 'playing' || SnakeGame.gameState === 'paused') {
                SnakeGame.togglePause();
            } else if (SnakeGame.gameState === 'gameover') {
                SnakeGame.resetToIdle();
            }
            return;
        }

        if (SnakeGame.gameState !== 'playing') return;

        if (lowerKey === 'arrowup' || lowerKey === 'w') SnakeGame.setDirection(0, -1);
        else if (lowerKey === 'arrowdown' || lowerKey === 's') SnakeGame.setDirection(0, 1);
        else if (lowerKey === 'arrowleft' || lowerKey === 'a') SnakeGame.setDirection(-1, 0);
        else if (lowerKey === 'arrowright' || lowerKey === 'd') SnakeGame.setDirection(1, 0);
    });

    document.getElementById('dpadUp').addEventListener('pointerdown', function(e) {
        e.preventDefault();
        SnakeGame.setDirection(0, -1);
    });
    document.getElementById('dpadDown').addEventListener('pointerdown', function(e) {
        e.preventDefault();
        SnakeGame.setDirection(0, 1);
    });
    document.getElementById('dpadLeft').addEventListener('pointerdown', function(e) {
        e.preventDefault();
        SnakeGame.setDirection(-1, 0);
    });
    document.getElementById('dpadRight').addEventListener('pointerdown', function(e) {
        e.preventDefault();
        SnakeGame.setDirection(1, 0);
    });

    SnakeGame.canvas.addEventListener('click', function(e) {
        if (SnakeGame.gameState === 'notify') {
            SnakeGame.setGameState('playing');
            return;
        }
        if (SnakeGame.gameState === 'confirming') {
            var coords = SnakeGame.getCanvasCoords(e.clientX, e.clientY);
            if (SnakeGame.isInConfirmBtn(coords.x, coords.y)) {
                SnakeGame.confirmSpeedChange();
            } else if (SnakeGame.isInCancelBtn(coords.x, coords.y)) {
                SnakeGame.cancelSpeedChange();
            }
            return;
        }
        if (SnakeGame.gameState === 'idle') {
            var coords = SnakeGame.getCanvasCoords(e.clientX, e.clientY);
            if (SnakeGame.isInStartBtn(coords.x, coords.y)) {
                SnakeGame.startFromIdle();
            }
        } else if (SnakeGame.gameState === 'paused') {
            SnakeGame.togglePause();
        } else if (SnakeGame.gameState === 'gameover') {
            SnakeGame.resetToIdle();
        }
    });

    var mouseDown = null;
    var mouseDownTime = 0;
    SnakeGame.canvas.addEventListener('mousedown', function(e) {
        mouseDown = { x: e.clientX, y: e.clientY };
        mouseDownTime = Date.now();
    });

    SnakeGame.canvas.addEventListener('mouseup', function(e) {
        if (!mouseDown) return;
        var dx = e.clientX - mouseDown.x;
        var dy = e.clientY - mouseDown.y;
        var absDx = Math.abs(dx);
        var absDy = Math.abs(dy);
        var elapsed = Date.now() - mouseDownTime;
        var maxDist = Math.max(absDx, absDy);
        mouseDown = null;
        if (maxDist < 5 && elapsed < 400) return;
        if (maxDist >= 5 && SnakeGame.gameState === 'playing') {
            if (absDx > absDy) SnakeGame.setDirection(dx > 0 ? 1 : -1, 0);
            else SnakeGame.setDirection(0, dy > 0 ? 1 : -1);
        }
    });

    var touchStart = null;
    var touchStartTime = 0;
    SnakeGame.canvas.addEventListener('touchstart', function(e) {
        touchStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
        touchStartTime = Date.now();
        e.preventDefault();
    }, { passive: false });

    SnakeGame.canvas.addEventListener('touchend', function(e) {
        if (!touchStart) {
            if (SnakeGame.gameState === 'notify') {
                SnakeGame.setGameState('playing');
                touchStart = null;
                return;
            }
            if (SnakeGame.gameState === 'confirming') {
                var endPt = e.changedTouches[0];
                var coords = SnakeGame.getCanvasCoords(endPt.clientX, endPt.clientY);
                if (SnakeGame.isInConfirmBtn(coords.x, coords.y)) {
                    SnakeGame.confirmSpeedChange();
                } else {
                    SnakeGame.cancelSpeedChange();
                }
                touchStart = null;
                return;
            }
            if (SnakeGame.gameState === 'gameover') SnakeGame.resetToIdle();
            if (SnakeGame.gameState === 'paused') SnakeGame.togglePause();
            touchStart = null;
            return;
        }
        var end = e.changedTouches[0];
        var dx = end.clientX - touchStart.x;
        var dy = end.clientY - touchStart.y;
        var absDx = Math.abs(dx);
        var absDy = Math.abs(dy);
        var elapsed = Date.now() - touchStartTime;
        var maxDist = Math.max(absDx, absDy);

        if (maxDist < 10 && elapsed < 400) {
            if (SnakeGame.gameState === 'idle') {
                var coords = SnakeGame.getCanvasCoords(end.clientX, end.clientY);
                if (SnakeGame.isInStartBtn(coords.x, coords.y)) {
                    SnakeGame.startFromIdle();
                }
            } else if (SnakeGame.gameState === 'paused') {
                SnakeGame.togglePause();
            } else if (SnakeGame.gameState === 'confirming') {
                var coords = SnakeGame.getCanvasCoords(end.clientX, end.clientY);
                if (SnakeGame.isInConfirmBtn(coords.x, coords.y)) {
                    SnakeGame.confirmSpeedChange();
                } else {
                    SnakeGame.cancelSpeedChange();
                }
            } else if (SnakeGame.gameState === 'notify') {
                SnakeGame.setGameState('playing');
            } else if (SnakeGame.gameState === 'gameover') {
                SnakeGame.resetToIdle();
            }
        } else if (maxDist >= 10 && SnakeGame.gameState === 'playing') {
            if (absDx > absDy) SnakeGame.setDirection(dx > 0 ? 1 : -1, 0);
            else SnakeGame.setDirection(0, dy > 0 ? 1 : -1);
        }
        touchStart = null;
    });

    SnakeGame.toggleDpadBtn.addEventListener('click', function() {
        if (SnakeGame.dpad.style.display === 'none') {
            SnakeGame.dpad.style.display = 'grid';
            SnakeGame.toggleDpadBtn.textContent = '隐藏方向键';
        } else {
            SnakeGame.dpad.style.display = 'none';
            SnakeGame.toggleDpadBtn.textContent = '显示方向键';
        }
    });
};
