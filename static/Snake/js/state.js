var Game = {
  state: 'idle',
  snake: [],
  prevSnake: [],
  dir: {x:1,y:0},
  nextDir: {x:1,y:0},
  food: null,
  score: 0,
  moveInterval: 130,
  lastMoveTime: 0,
  particles: [],
  bestScores: {},
  bgColor: '#0b0b0b'
};

function loadBestScores(){
  try{
    var raw = localStorage.getItem(BEST_SCORES_KEY);
    Game.bestScores = raw ? JSON.parse(raw) : {};
  }catch(e){
    Game.bestScores = {};
  }
}

function getBestScore(interval){
  return Game.bestScores[interval] || 0;
}

function saveBestScoreIfNeeded(){
  var key = Game.moveInterval;
  var current = Game.bestScores[key] || 0;
  if(Game.score > current){
    Game.bestScores[key] = Game.score;
    try{
      localStorage.setItem(BEST_SCORES_KEY, JSON.stringify(Game.bestScores));
    }catch(e){}
    return true;
  }
  return false;
}

function updateScoreDisplay(){
  currentScoreEl.textContent = Game.score;
  currentScoreEl.classList.remove('bump');
  void currentScoreEl.offsetWidth;
  currentScoreEl.classList.add('bump');
}

function updateBestDisplay(){
  bestScoreEl.textContent = getBestScore(Game.moveInterval);
}

function setSpeed(interval){
  Game.moveInterval = interval;
  modeButtons.forEach(function(btn){
    var speed = parseInt(btn.dataset.speed, 10);
    btn.classList.toggle('active', speed === interval);
  });
  updateBestDisplay();
}

function vibrate(ms){
  try{
    if(navigator.vibrate) navigator.vibrate(ms);
  }catch(e){}
}

function cloneSeg(seg){
  return {x:seg.x, y:seg.y};
}

function buildInitialSnake(){
  var startX = Math.floor(COLS / 4);
  var startY = Math.floor(ROWS / 2);
  return [
    {x:startX + 2, y:startY},
    {x:startX + 1, y:startY},
    {x:startX, y:startY}
  ];
}

function spawnFood(){
  var occupied = {};
  Game.snake.forEach(function(seg){
    occupied[seg.x + ',' + seg.y] = true;
  });
  var free = [];
  for(var x = 0; x < COLS; x++){
    for(var y = 0; y < ROWS; y++){
      if(!occupied[x + ',' + y]) free.push({x:x, y:y});
    }
  }
  if(free.length === 0){
    endGame();
    return;
  }
  Game.food = free[Math.floor(Math.random() * free.length)];
}

function spawnParticles(x, y){
  for(var i = 0; i < 8; i++){
    var angle = (Math.PI * 2 / 8) * i + Math.random() * 0.5;
    var speed = 1.4 + Math.random() * 2.6;
    Game.particles.push({
      x: x * Renderer.cellSize + Renderer.cellSize / 2,
      y: y * Renderer.cellSize + Renderer.cellSize / 2,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1,
      decay: 0.02 + Math.random() * 0.035,
      size: 2.2 + Math.random() * 2.2
    });
  }
}

function updateParticles(){
  for(var i = Game.particles.length - 1; i >= 0; i--){
    var p = Game.particles[i];
    p.x += p.vx;
    p.y += p.vy;
    p.life -= p.decay;
    if(p.life <= 0) Game.particles.splice(i, 1);
  }
}

function isOutOfBounds(pos){
  return pos.x < 0 || pos.x >= COLS || pos.y < 0 || pos.y >= ROWS;
}

function isSelfCollision(pos){
  return Game.snake.some(function(seg){
    return seg.x === pos.x && seg.y === pos.y;
  });
}

function setDirection(dx, dy){
  if(Game.state !== 'playing') return;
  if(dx === 0 && dy === 0) return;
  if(dx === -Game.dir.x && dy === -Game.dir.y && Game.snake.length > 1) return;
  Game.nextDir = {x:dx, y:dy};
}

function step(){
  if(Game.state !== 'playing') return;
  Game.prevSnake = Game.snake.map(cloneSeg);
  Game.dir = Game.nextDir;
  var head = Game.snake[0];
  var newHead = {x: head.x + Game.dir.x, y: head.y + Game.dir.y};
  if(isOutOfBounds(newHead) || isSelfCollision(newHead)){
    endGame();
    return;
  }
  Game.snake.unshift(newHead);
  if(Game.food && newHead.x === Game.food.x && newHead.y === Game.food.y){
    Game.score += 10;
    updateScoreDisplay();
    spawnParticles(Game.food.x, Game.food.y);
    spawnFood();
    vibrate(10);
  }else{
    Game.snake.pop();
  }
}

function endGame(){
  var isNewBest = saveBestScoreIfNeeded();
  if(Game.snake.length) spawnParticles(Game.snake[0].x, Game.snake[0].y);
  finalScoreEl.textContent = Game.score;
  newBestBadge.classList.toggle('visible', isNewBest);
  updateBestDisplay();
  vibrate(60);
  setGameState('gameover');
}

function startGame(){
  Game.snake = buildInitialSnake();
  Game.prevSnake = Game.snake.map(cloneSeg);
  Game.dir = {x:1, y:0};
  Game.nextDir = {x:1, y:0};
  Game.score = 0;
  Game.particles = [];
  updateScoreDisplay();
  spawnFood();
  Game.lastMoveTime = performance.now();
  setGameState('playing');
}

function setGameState(next){
  var prev = Game.state;
  Game.state = next;
  if(next === 'playing' && (prev === 'paused' || prev === 'idle')){
    Game.lastMoveTime = performance.now();
  }
  renderState(next);
}

function renderState(state){
  overlayIdle.classList.toggle('visible', state === 'idle');
  overlayPaused.classList.toggle('visible', state === 'paused');
  overlayGameOver.classList.toggle('visible', state === 'gameover');
  pauseBtn.disabled = state === 'idle' || state === 'gameover';
  pauseBtn.classList.toggle('is-resume', state === 'paused');
  pauseBtn.querySelector('.btn-label').textContent = state === 'paused' ? '继续' : '暂停';
  restartBtn.textContent = state === 'idle' ? '开始游戏' : '重新开始';
  modeButtons.forEach(function(btn){
    btn.classList.toggle('is-locked', state === 'playing');
  });
}
