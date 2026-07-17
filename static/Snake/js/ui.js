function handlePrimaryAction(){
  if(Game.state === 'idle') startGame();
  else if(Game.state === 'playing') setGameState('paused');
  else if(Game.state === 'paused') setGameState('playing');
  else if(Game.state === 'gameover') startGame();
}

var toastTimer = null;
function showToast(message){
  toastEl.textContent = message;
  toastEl.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function(){
    toastEl.classList.remove('visible');
  }, 1800);
}

function setupModeButtons(){
  modeButtons.forEach(function(btn){
    btn.addEventListener('click', function(){
      if(Game.state === 'playing'){
        showToast('游戏进行中无法切换速度');
        return;
      }
      var speed = parseInt(btn.dataset.speed, 10);
      setSpeed(speed);
    });
  });
}

function setupSwatches(){
  swatchEls.forEach(function(swatch){
    swatch.addEventListener('click', function(){
      Game.bgColor = swatch.dataset.color;
      swatchEls.forEach(function(s){
        s.classList.toggle('active', s === swatch);
      });
    });
  });
}

function setupButtons(){
  startBtn.addEventListener('click', startGame);
  restartFromOverBtn.addEventListener('click', startGame);
  restartBtn.addEventListener('click', startGame);
  pauseBtn.addEventListener('click', function(){
    if(Game.state === 'playing') setGameState('paused');
    else if(Game.state === 'paused') setGameState('playing');
  });
  toggleDpadBtn.addEventListener('click', function(){
    var showing = dpadEl.classList.toggle('visible');
    toggleDpadBtn.textContent = showing ? '隐藏方向键' : '显示方向键';
    resizeCanvas();
  });
}

function setupHint(){
  hintEl.textContent = isTouchDevice
    ? '滑动屏幕或使用方向键控制 · 点击画布暂停/继续'
    : '方向键 / WASD 移动 · 空格键开始/暂停/继续 · 点击画布暂停';
}

function initDpadVisibility(){
  if(isTouchDevice){
    dpadEl.classList.add('visible');
    toggleDpadBtn.textContent = '隐藏方向键';
  }else{
    toggleDpadBtn.textContent = '显示方向键';
  }
}
