var Renderer = {
  boardSize: 400,
  cellSize: 20
};

function drawRoundedRect(x, y, w, h, radius){
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + w - radius, y);
  ctx.arcTo(x + w, y, x + w, y + radius, radius);
  ctx.lineTo(x + w, y + h - radius);
  ctx.arcTo(x + w, y + h, x + w - radius, y + h, radius);
  ctx.lineTo(x + radius, y + h);
  ctx.arcTo(x, y + h, x, y + h - radius, radius);
  ctx.lineTo(x, y + radius);
  ctx.arcTo(x, y, x + radius, y, radius);
  ctx.closePath();
}

function getInterpolatedSnake(t){
  var prev = Game.prevSnake;
  var curr = Game.snake;
  if(t >= 1 || prev.length === 0) return curr;
  var result = new Array(curr.length);
  for(var i = 0; i < curr.length; i++){
    var from = i < prev.length ? prev[i] : prev[prev.length - 1];
    var to = curr[i];
    result[i] = {x: from.x + (to.x - from.x) * t, y: from.y + (to.y - from.y) * t};
  }
  return result;
}

function draw(ts){
  var size = Renderer.boardSize;
  var grid = Renderer.cellSize;

  ctx.fillStyle = Game.bgColor;
  ctx.fillRect(0, 0, size, size);

  ctx.strokeStyle = 'rgba(255,255,255,0.045)';
  ctx.lineWidth = 1;
  for(var gx = 0; gx <= COLS; gx++){
    ctx.beginPath();
    ctx.moveTo(gx * grid, 0);
    ctx.lineTo(gx * grid, size);
    ctx.stroke();
  }
  for(var gy = 0; gy <= ROWS; gy++){
    ctx.beginPath();
    ctx.moveTo(0, gy * grid);
    ctx.lineTo(size, gy * grid);
    ctx.stroke();
  }

  if(Game.state === 'playing' || Game.state === 'paused' || Game.state === 'gameover'){
    if(Game.food){
      var pulse = 0.65 + 0.35 * Math.sin(ts / 240);
      var fx = Game.food.x * grid;
      var fy = Game.food.y * grid;
      var pad = grid * 0.16;
      ctx.save();
      ctx.shadowColor = 'rgba(255,122,89,' + (0.35 + 0.35 * pulse) + ')';
      ctx.shadowBlur = 10 + 8 * pulse;
      ctx.fillStyle = '#ff7a59';
      drawRoundedRect(fx + pad, fy + pad, grid - pad * 2, grid - pad * 2, (grid - pad * 2) / 3.2);
      ctx.fill();
      ctx.restore();
      ctx.fillStyle = 'rgba(255,214,199,0.75)';
      var innerPad = grid * 0.34;
      ctx.beginPath();
      ctx.arc(fx + innerPad + (grid - innerPad * 2) / 2, fy + innerPad, (grid - innerPad * 2) / 2.6, 0, Math.PI * 2);
      ctx.fill();
    }

    var t = Game.state === 'playing' ? clamp((ts - Game.lastMoveTime) / Game.moveInterval, 0, 1) : 1;
    var renderSnake = getInterpolatedSnake(t);
    var total = renderSnake.length;
    renderSnake.forEach(function(seg, idx){
      var sx = seg.x * grid;
      var sy = seg.y * grid;
      var isHead = idx === 0;
      var ratio = total > 1 ? idx / (total - 1) : 0;
      var color = mixColor('#5fe89a', '#155c3b', ratio);
      ctx.save();
      if(isHead){
        ctx.shadowColor = 'rgba(95,232,154,0.65)';
        ctx.shadowBlur = 12;
      }
      ctx.fillStyle = color;
      var segPad = grid * 0.05;
      drawRoundedRect(sx + segPad, sy + segPad, grid - segPad * 2, grid - segPad * 2, grid * 0.28);
      ctx.fill();
      ctx.restore();
      if(isHead){
        drawEyes(sx, sy, grid);
      }
    });

    Game.particles.forEach(function(p){
      ctx.globalAlpha = clamp(p.life, 0, 1);
      ctx.fillStyle = '#ffcb80';
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.globalAlpha = 1;
  }
}

function drawEyes(sx, sy, grid){
  var dir = Game.dir;
  var cx = sx + grid / 2;
  var cy = sy + grid / 2;
  var offset = grid * 0.18;
  var perpX = -dir.y;
  var perpY = dir.x;
  var forwardX = dir.x * grid * 0.14;
  var forwardY = dir.y * grid * 0.14;
  var eye1x = cx + forwardX + perpX * offset;
  var eye1y = cy + forwardY + perpY * offset;
  var eye2x = cx + forwardX - perpX * offset;
  var eye2y = cy + forwardY - perpY * offset;
  ctx.fillStyle = '#04140c';
  ctx.beginPath();
  ctx.arc(eye1x, eye1y, grid * 0.09, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(eye2x, eye2y, grid * 0.09, 0, Math.PI * 2);
  ctx.fill();
}

function mixColor(hexA, hexB, ratio){
  var a = hexToRgb(hexA);
  var b = hexToRgb(hexB);
  var r = Math.round(a.r + (b.r - a.r) * ratio);
  var g = Math.round(a.g + (b.g - a.g) * ratio);
  var bl = Math.round(a.b + (b.b - a.b) * ratio);
  return 'rgb(' + r + ',' + g + ',' + bl + ')';
}

function hexToRgb(hex){
  var v = hex.replace('#', '');
  return {
    r: parseInt(v.substring(0,2), 16),
    g: parseInt(v.substring(2,4), 16),
    b: parseInt(v.substring(4,6), 16)
  };
}

function measureAvailableSize(){
  var stageRect = stageEl.getBoundingClientRect();
  var dpadVisible = dpadEl.classList.contains('visible');
  var dpadHeight = dpadVisible ? dpadEl.getBoundingClientRect().height : 0;
  var gap = dpadVisible ? 14 : 0;
  return {
    availableWidth: stageRect.width,
    availableHeight: stageRect.height - dpadHeight - gap
  };
}

function resizeCanvas(){
  var available = measureAvailableSize();
  var size = clamp(Math.floor(Math.min(available.availableWidth, available.availableHeight)), MIN_CANVAS_SIZE, MAX_CANVAS_SIZE);
  var dpr = Math.min(window.devicePixelRatio || 1, 3);

  canvasFrameEl.style.width = size + 'px';
  canvasFrameEl.style.height = size + 'px';
  canvasEl.style.width = size + 'px';
  canvasEl.style.height = size + 'px';
  canvasEl.width = Math.round(size * dpr);
  canvasEl.height = Math.round(size * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  Renderer.boardSize = size;
  Renderer.cellSize = size / COLS;
  draw(performance.now());
}

function setupResize(){
  var scheduled = false;
  var observer = new ResizeObserver(function(){
    if(scheduled) return;
    scheduled = true;
    requestAnimationFrame(function(){
      scheduled = false;
      resizeCanvas();
    });
  });
  observer.observe(stageEl);
  window.addEventListener('orientationchange', function(){
    setTimeout(resizeCanvas, 200);
  });
}
