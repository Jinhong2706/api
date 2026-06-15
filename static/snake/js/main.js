var SnakeGame = SnakeGame || {};

var animationId = null;

function loop(ts) {
    if (SnakeGame.gameState === 'playing') {
        if (ts - SnakeGame.lastMoveTime >= SnakeGame.moveInterval) {
            SnakeGame.update();
            SnakeGame.lastMoveTime = ts;
        }
        SnakeGame.updateParticles();
    }

    if (SnakeGame.gameState === 'gameover' && SnakeGame.particles.length > 0) {
        SnakeGame.updateParticles();
    }

    SnakeGame.draw();
    animationId = requestAnimationFrame(loop);
}

function startLoop() {
    if (animationId) cancelAnimationFrame(animationId);
    SnakeGame.lastMoveTime = performance.now();
    animationId = requestAnimationFrame(loop);
}

SnakeGame.setupInput();
SnakeGame.setupUI();

SnakeGame.loadBest();
SnakeGame.bgColor = '#000000';
SnakeGame.canvas.style.backgroundColor = '#000000';
SnakeGame.colorSwatches.forEach(function(s) {
    s.classList.remove('active');
    if (s.dataset.color === '#000000') s.classList.add('active');
});
SnakeGame.setSpeedMode(130);
SnakeGame.setGameState('idle');

setTimeout(function() {
    startLoop();
}, 0);
