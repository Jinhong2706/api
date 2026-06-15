var SnakeGame = SnakeGame || {};

SnakeGame.drawRoundedRect = function(x, y, w, h, radius) {
    var ctx = SnakeGame.ctx;
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
};

SnakeGame.draw = function() {
    var ctx = SnakeGame.ctx;
    var SIZE = SnakeGame.SIZE;
    var GRID = SnakeGame.GRID;
    var COLS = SnakeGame.COLS;
    var ROWS = SnakeGame.ROWS;

    ctx.fillStyle = SnakeGame.bgColor;
    ctx.fillRect(0, 0, SIZE, SIZE);

    ctx.strokeStyle = 'rgba(255,255,255,0.04)';
    ctx.lineWidth = 0.5;
    for (var i = 0; i <= COLS; i++) {
        ctx.beginPath();
        ctx.moveTo(i * GRID, 0);
        ctx.lineTo(i * GRID, SIZE);
        ctx.stroke();
    }
    for (var i = 0; i <= ROWS; i++) {
        ctx.beginPath();
        ctx.moveTo(0, i * GRID);
        ctx.lineTo(SIZE, i * GRID);
        ctx.stroke();
    }

    if (SnakeGame.gameState === 'playing' || SnakeGame.gameState === 'paused' || SnakeGame.gameState === 'gameover') {
        if (SnakeGame.food) {
            var fx = SnakeGame.food.x * GRID, fy = SnakeGame.food.y * GRID;
            ctx.fillStyle = '#ff4d4d';
            ctx.shadowColor = '#ff4d4d';
            ctx.shadowBlur = 12;
            ctx.fillRect(fx, fy, GRID, GRID);
            ctx.fillStyle = 'rgba(255,180,180,0.7)';
            ctx.fillRect(fx + 2, fy + 2, GRID - 4, GRID - 4);
            ctx.shadowBlur = 0;
            ctx.shadowColor = 'transparent';
        }

        SnakeGame.snake.forEach(function(seg, idx) {
            var sx = seg.x * GRID, sy = seg.y * GRID;
            var isHead = idx === 0;
            ctx.fillStyle = isHead ? '#4caf50' : '#2e7d32';
            if (isHead) {
                ctx.shadowColor = '#4caf50';
                ctx.shadowBlur = 10;
            }
            ctx.fillRect(sx, sy, GRID, GRID);
            ctx.strokeStyle = isHead ? '#81c784' : '#1b5e20';
            ctx.lineWidth = 1.2;
            ctx.strokeRect(sx + 0.5, sy + 0.5, GRID - 1, GRID - 1);
            ctx.shadowBlur = 0;
            ctx.shadowColor = 'transparent';
        });

        SnakeGame.particles.forEach(function(p) {
            ctx.globalAlpha = p.life;
            ctx.fillStyle = '#ffcc80';
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.globalAlpha = 1;
    }

    if (SnakeGame.gameState === 'idle') {
        ctx.fillStyle = 'rgba(0,0,0,0.3)';
        SnakeGame.drawRoundedRect(SnakeGame.startBtnX + 3, SnakeGame.startBtnY + 3, SnakeGame.startBtnW, SnakeGame.startBtnH, SnakeGame.startBtnRadius);
        ctx.fill();

        var btnGrad = ctx.createLinearGradient(SnakeGame.startBtnX, SnakeGame.startBtnY, SnakeGame.startBtnX, SnakeGame.startBtnY + SnakeGame.startBtnH);
        btnGrad.addColorStop(0, '#5cbf62');
        btnGrad.addColorStop(1, '#388e3c');
        ctx.fillStyle = btnGrad;
        ctx.shadowColor = 'rgba(76,175,80,0.7)';
        ctx.shadowBlur = 20;
        SnakeGame.drawRoundedRect(SnakeGame.startBtnX, SnakeGame.startBtnY, SnakeGame.startBtnW, SnakeGame.startBtnH, SnakeGame.startBtnRadius);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';

        ctx.strokeStyle = 'rgba(255,255,255,0.3)';
        ctx.lineWidth = 2;
        SnakeGame.drawRoundedRect(SnakeGame.startBtnX, SnakeGame.startBtnY, SnakeGame.startBtnW, SnakeGame.startBtnH, SnakeGame.startBtnRadius);
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 22px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.shadowColor = 'rgba(0,0,0,0.4)';
        ctx.shadowBlur = 4;
        ctx.fillText('开始游戏', SIZE / 2, SnakeGame.startBtnY + SnakeGame.startBtnH / 2);
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';
        ctx.textAlign = 'start';
        ctx.textBaseline = 'alphabetic';
    }

    if (SnakeGame.gameState === 'paused') {
        ctx.fillStyle = 'rgba(0,0,0,0.55)';
        ctx.fillRect(0, 0, SIZE, SIZE);

        var bar1X = SnakeGame.pauseIconCX - SnakeGame.pauseBarGap / 2 - SnakeGame.pauseBarW;
        var bar2X = SnakeGame.pauseIconCX + SnakeGame.pauseBarGap / 2;
        var barY = SnakeGame.pauseIconCY - SnakeGame.pauseBarH / 2;

        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = 'rgba(255,255,255,0.6)';
        ctx.shadowBlur = 14;
        SnakeGame.drawRoundedRect(bar1X, barY, SnakeGame.pauseBarW, SnakeGame.pauseBarH, SnakeGame.pauseBarRadius);
        ctx.fill();
        SnakeGame.drawRoundedRect(bar2X, barY, SnakeGame.pauseBarW, SnakeGame.pauseBarH, SnakeGame.pauseBarRadius);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 20px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('已暂停', SIZE / 2, SnakeGame.pauseIconCY + SnakeGame.pauseBarH / 2 + 28);
        ctx.fillStyle = '#ccc';
        ctx.font = '14px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillText('点击屏幕或按空格键继续', SIZE / 2, SnakeGame.pauseIconCY + SnakeGame.pauseBarH / 2 + 52);
        ctx.textAlign = 'start';
    }

    if (SnakeGame.gameState === 'confirming') {
        ctx.fillStyle = 'rgba(0,0,0,0.7)';
        ctx.fillRect(0, 0, SIZE, SIZE);

        ctx.fillStyle = '#1e1e1e';
        ctx.strokeStyle = '#555';
        ctx.lineWidth = 2;
        ctx.shadowColor = 'rgba(0,0,0,0.8)';
        ctx.shadowBlur = 30;
        SnakeGame.drawRoundedRect(SnakeGame.confirmDialogX, SnakeGame.confirmDialogY, SnakeGame.confirmDialogW, SnakeGame.confirmDialogH, SnakeGame.confirmDialogR);
        ctx.fill();
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 20px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('请确任切换速度', SIZE / 2, SnakeGame.confirmDialogY + SnakeGame.confirmDialogH * 0.28);

        var speedNames = { 180: '慢速', 130: '正常', 90: '快速', 60: '极速' };
        var speedName = speedNames[SnakeGame.pendingSpeed] || '正常';
        var speedColor;
        if (SnakeGame.pendingSpeed === 180) speedColor = '#81c784';
        else if (SnakeGame.pendingSpeed === 130) speedColor = '#4caf50';
        else if (SnakeGame.pendingSpeed === 90) speedColor = '#ff9800';
        else speedColor = '#f44336';

        ctx.fillStyle = speedColor;
        ctx.font = 'bold 22px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillText(speedName, SIZE / 2, SnakeGame.confirmDialogY + SnakeGame.confirmDialogH * 0.48);

        var gradConfirm = ctx.createLinearGradient(SnakeGame.confirmBtnX, SnakeGame.confirmBtnY, SnakeGame.confirmBtnX, SnakeGame.confirmBtnY + SnakeGame.confirmBtnH);
        gradConfirm.addColorStop(0, '#5cbf62');
        gradConfirm.addColorStop(1, '#388e3c');
        ctx.fillStyle = gradConfirm;
        ctx.shadowColor = 'rgba(76,175,80,0.5)';
        ctx.shadowBlur = 10;
        SnakeGame.drawRoundedRect(SnakeGame.confirmBtnX, SnakeGame.confirmBtnY, SnakeGame.confirmBtnW, SnakeGame.confirmBtnH, SnakeGame.confirmBtnR);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 15px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillText('确认', SnakeGame.confirmBtnX + SnakeGame.confirmBtnW / 2, SnakeGame.confirmBtnY + SnakeGame.confirmBtnH / 2);

        var gradCancel = ctx.createLinearGradient(SnakeGame.cancelBtnX, SnakeGame.confirmBtnY, SnakeGame.cancelBtnX, SnakeGame.confirmBtnY + SnakeGame.confirmBtnH);
        gradCancel.addColorStop(0, '#555');
        gradCancel.addColorStop(1, '#333');
        ctx.fillStyle = gradCancel;
        ctx.shadowColor = 'rgba(0,0,0,0.5)';
        ctx.shadowBlur = 8;
        SnakeGame.drawRoundedRect(SnakeGame.cancelBtnX, SnakeGame.confirmBtnY, SnakeGame.confirmBtnW, SnakeGame.confirmBtnH, SnakeGame.confirmBtnR);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';
        ctx.fillStyle = '#ccc';
        ctx.font = 'bold 15px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillText('取消', SnakeGame.cancelBtnX + SnakeGame.confirmBtnW / 2, SnakeGame.confirmBtnY + SnakeGame.confirmBtnH / 2);

        ctx.textAlign = 'start';
        ctx.textBaseline = 'alphabetic';
    }

    if (SnakeGame.gameState === 'notify') {
        ctx.fillStyle = 'rgba(0,0,0,0.7)';
        ctx.fillRect(0, 0, SIZE, SIZE);

        ctx.fillStyle = '#1e1e1e';
        ctx.strokeStyle = '#555';
        ctx.lineWidth = 2;
        ctx.shadowColor = 'rgba(0,0,0,0.8)';
        ctx.shadowBlur = 30;
        SnakeGame.drawRoundedRect(SnakeGame.notifyDialogX, SnakeGame.notifyDialogY, SnakeGame.notifyDialogW, SnakeGame.notifyDialogH, SnakeGame.notifyDialogR);
        ctx.fill();
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';

        ctx.fillStyle = '#ff9800';
        ctx.font = 'bold 20px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('提示', SIZE / 2, SnakeGame.notifyDialogY + SnakeGame.notifyDialogH * 0.22);

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 17px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillText('游戏中无法切换速度', SIZE / 2, SnakeGame.notifyDialogY + SnakeGame.notifyDialogH * 0.42);

        ctx.fillStyle = '#aaa';
        ctx.font = '13px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillText('请游戏结束后再试', SIZE / 2, SnakeGame.notifyDialogY + SnakeGame.notifyDialogH * 0.56);

        var gradBtn = ctx.createLinearGradient(SnakeGame.notifyBtnX, SnakeGame.notifyBtnY, SnakeGame.notifyBtnX, SnakeGame.notifyBtnY + SnakeGame.notifyBtnH);
        gradBtn.addColorStop(0, '#5cbf62');
        gradBtn.addColorStop(1, '#388e3c');
        ctx.fillStyle = gradBtn;
        ctx.shadowColor = 'rgba(76,175,80,0.5)';
        ctx.shadowBlur = 10;
        SnakeGame.drawRoundedRect(SnakeGame.notifyBtnX, SnakeGame.notifyBtnY, SnakeGame.notifyBtnW, SnakeGame.notifyBtnH, SnakeGame.notifyBtnR);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 15px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillText('继续', SnakeGame.notifyBtnX + SnakeGame.notifyBtnW / 2, SnakeGame.notifyBtnY + SnakeGame.notifyBtnH / 2);

        ctx.textAlign = 'start';
        ctx.textBaseline = 'alphabetic';
    }

    if (SnakeGame.gameState === 'gameover') {
        ctx.fillStyle = 'rgba(0,0,0,0.7)';
        ctx.fillRect(0, 0, SIZE, SIZE);
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 30px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.textAlign = 'center';
        ctx.shadowColor = '#000';
        ctx.shadowBlur = 10;
        ctx.fillText('游戏结束', SIZE / 2, SIZE / 2 - 15);
        ctx.shadowBlur = 0;
        ctx.fillStyle = '#ffc107';
        ctx.font = '18px "PingFang SC"';
        ctx.fillText('得分 ' + SnakeGame.score, SIZE / 2, SIZE / 2 + 30);
        ctx.fillStyle = '#ccc';
        ctx.font = '13px "PingFang SC"';
        ctx.fillText('按空格键或点击按钮重新开始', SIZE / 2, SIZE / 2 + 58);
        ctx.textAlign = 'start';
    }
};
