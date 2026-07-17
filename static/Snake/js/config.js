var COLS = 20;
var ROWS = 20;
var MIN_CANVAS_SIZE = 200;
var MAX_CANVAS_SIZE = 640;
var BEST_SCORES_KEY = 'snakeBestScores';

var stageEl = document.getElementById('stage');
var canvasFrameEl = document.getElementById('canvasFrame');
var canvasEl = document.getElementById('gameCanvas');
var ctx = canvasEl.getContext('2d');
var currentScoreEl = document.getElementById('currentScore');
var bestScoreEl = document.getElementById('bestScore');
var overlayIdle = document.getElementById('overlayIdle');
var overlayPaused = document.getElementById('overlayPaused');
var overlayGameOver = document.getElementById('overlayGameOver');
var finalScoreEl = document.getElementById('finalScore');
var newBestBadge = document.getElementById('newBestBadge');
var toastEl = document.getElementById('toast');
var dpadEl = document.getElementById('dpad');
var dpadButtons = dpadEl.querySelectorAll('.dpad-btn');
var modeButtons = document.querySelectorAll('.mode-btn');
var swatchEls = document.querySelectorAll('.swatch');
var startBtn = document.getElementById('startBtn');
var restartFromOverBtn = document.getElementById('restartFromOverBtn');
var restartBtn = document.getElementById('restartBtn');
var pauseBtn = document.getElementById('pauseBtn');
var toggleDpadBtn = document.getElementById('toggleDpadBtn');
var hintEl = document.getElementById('hint');

var isTouchDevice = (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) || navigator.maxTouchPoints > 0;

function clamp(value, min, max){
  return Math.max(min, Math.min(max, value));
}
