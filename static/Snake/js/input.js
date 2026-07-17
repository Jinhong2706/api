function setupDpad(){
  dpadButtons.forEach(function(btn){
    btn.addEventListener('pointerdown', function(e){
      e.preventDefault();
      var dir = btn.dataset.dir;
      if(dir === 'up') setDirection(0, -1);
      else if(dir === 'down') setDirection(0, 1);
      else if(dir === 'left') setDirection(-1, 0);
      else if(dir === 'right') setDirection(1, 0);
    });
  });
}

function setupPointerControls(){
  var pointerStart = null;
  canvasFrameEl.addEventListener('pointerdown', function(e){
    pointerStart = {x:e.clientX, y:e.clientY, time:Date.now(), id:e.pointerId};
  });
  canvasFrameEl.addEventListener('pointerup', function(e){
    if(e.target.closest('button')){
      pointerStart = null;
      return;
    }
    if(!pointerStart || pointerStart.id !== e.pointerId) return;
    var dx = e.clientX - pointerStart.x;
    var dy = e.clientY - pointerStart.y;
    var dist = Math.max(Math.abs(dx), Math.abs(dy));
    pointerStart = null;
    if(dist < 12){
      handlePrimaryAction();
      return;
    }
    if(Game.state === 'playing'){
      if(Math.abs(dx) > Math.abs(dy)) setDirection(dx > 0 ? 1 : -1, 0);
      else setDirection(0, dy > 0 ? 1 : -1);
    }
  });
}

function setupKeyboard(){
  var navKeys = ['arrowup','arrowdown','arrowleft','arrowright','w','a','s','d',' '];
  document.addEventListener('keydown', function(e){
    var lower = e.key.toLowerCase();
    if(navKeys.indexOf(lower) !== -1) e.preventDefault();
    if(lower === ' '){
      handlePrimaryAction();
      return;
    }
    if(Game.state !== 'playing') return;
    if(lower === 'arrowup' || lower === 'w') setDirection(0, -1);
    else if(lower === 'arrowdown' || lower === 's') setDirection(0, 1);
    else if(lower === 'arrowleft' || lower === 'a') setDirection(-1, 0);
    else if(lower === 'arrowright' || lower === 'd') setDirection(1, 0);
  });
}
