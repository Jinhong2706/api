var animationId = null;
function frame(ts){
  if(Game.state === 'playing'){
    if(ts - Game.lastMoveTime >= Game.moveInterval){
      step();
      Game.lastMoveTime = ts;
    }
  }
  if(Game.state === 'playing' || Game.state === 'gameover'){
    if(Game.particles.length) updateParticles();
  }
  draw(ts);
  animationId = requestAnimationFrame(frame);
}

function init(){
  loadBestScores();
  setSpeed(130);
  initDpadVisibility();
  setupHint();
  setupResize();
  setupModeButtons();
  setupSwatches();
  setupButtons();
  setupDpad();
  setupPointerControls();
  setupKeyboard();
  setGameState('idle');
  resizeCanvas();
  animationId = requestAnimationFrame(frame);
}

init();
