let canvas = document.getElementById('sketch');
let ctx = canvas.getContext('2d');
let isDrawing = false;
let currentTool = 'pen';
let currentSound = null;
let currentColor = '#000000';
if (!canvas || !ctx) {
    console.error('Canvas not found or context not available');
}
if (ctx) {
    ctx.strokeStyle = currentColor;
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
}
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;
    console.log('Initializing dark mode...', darkModeToggle ? 'Toggle found' : 'Toggle NOT found');
    if (darkModeToggle) {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            html.classList.add('dark');
            console.log('Applied saved dark theme');
        }
        darkModeToggle.onclick = function() {
            console.log('Dark mode toggle clicked!');
            html.classList.toggle('dark');
            const isDark = html.classList.contains('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            console.log('Dark mode toggled to:', isDark ? 'dark' : 'light');
            updateCanvasForDarkMode();
        };
        console.log('Dark mode toggle initialized successfully');
    } else {
        console.error('Dark mode toggle button not found!');
    }
}
function updateCanvasForDarkMode() {
    if (!ctx) return;
    if (currentTool === 'pen') {
        const html = document.documentElement;
        if (html.classList.contains('dark') && currentColor === '#000000') {
            currentColor = '#ffffff';
            ctx.strokeStyle = currentColor;
            updateColorButtons();
        } else if (!html.classList.contains('dark') && currentColor === '#ffffff') {
            currentColor = '#000000';
            ctx.strokeStyle = currentColor;
            updateColorButtons();
        }
    }
}
function initializeApp() {
    console.log('Initializing app...');
    
    canvas = document.getElementById('sketch');
    if (canvas) {
        ctx = canvas.getContext('2d');
        if (ctx) {
            ctx.strokeStyle = currentColor;
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
        }
    }
    
    initDarkMode();
    
    const clearBtn = document.getElementById('clear');
    const eraserBtn = document.getElementById('eraser');
    const penBtn = document.getElementById('pen');
    const submitBtn = document.getElementById('submit');
    const playBtn = document.getElementById('playBtn');
    const stopBtn = document.getElementById('stopBtn');
    const submitRatingBtn = document.getElementById('submitRating');
    
    if (clearBtn) {
        clearBtn.onclick = clearCanvas;
        console.log('Clear button initialized');
    }
    if (eraserBtn) {
        eraserBtn.onclick = () => {
            console.log('Eraser clicked');
            setTool('eraser');
        };
        console.log('Eraser button initialized');
    }
    if (penBtn) {
        penBtn.onclick = () => {
            console.log('Pen clicked');
            setTool('pen');
        };
        console.log('Pen button initialized');
    }
    if (submitBtn) submitBtn.onclick = predictMood;
    if (playBtn) playBtn.onclick = playAudio;
    if (stopBtn) stopBtn.onclick = stopAudio;
    if (submitRatingBtn) submitRatingBtn.onclick = submitRating;
    const colorButtons = document.querySelectorAll('.color-btn');
    const brushSizeSlider = document.getElementById('brushSize');
    const brushSizeDisplay = document.getElementById('brushSizeDisplay');
    colorButtons.forEach(button => {
        button.onclick = function() {
            const color = this.dataset.color;
            setColor(color);
        };
    });
    if (brushSizeSlider) {
        brushSizeSlider.oninput = function() {
            const size = parseInt(this.value);
            setBrushSize(size);
        };
    }
    if (canvas) {
        canvas.onmousedown = startDrawing;
        canvas.onmousemove = draw;
        canvas.onmouseup = stopDrawing;
        canvas.onmouseout = stopDrawing;
        canvas.ontouchstart = handleTouch;
        canvas.ontouchmove = handleTouch;
        canvas.ontouchend = stopDrawing;
    }
    updateToolButtons();
    updateColorButtons();
    setBrushSize(3);
    initAudioControls();
}
function setColor(color) {
    currentColor = color;
    if (currentTool === 'pen') {
        ctx.strokeStyle = currentColor;
    }
    updateColorButtons();
}
function setBrushSize(size) {
    ctx.lineWidth = size;
    const display = document.getElementById('brushSizeDisplay');
    if (display) display.textContent = size + 'px';
    if (currentTool === 'eraser') {
        ctx.lineWidth = size * 2; // Eraser is bigger
    }
}
function updateColorButtons() {
    const colorButtons = document.querySelectorAll('.color-btn');
    colorButtons.forEach(button => {
        if (button.dataset.color === currentColor) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
function setTool(tool) {
    currentTool = tool;
    const brushSizeSlider = document.getElementById('brushSize');
    const brushSize = brushSizeSlider ? parseInt(brushSizeSlider.value) : 3;
    
    if (tool === 'eraser') {
        ctx.globalCompositeOperation = 'destination-out';
        ctx.lineWidth = brushSize * 2; // Eraser is bigger
    } else {
        ctx.globalCompositeOperation = 'source-over';
        ctx.lineWidth = brushSize;
        ctx.strokeStyle = currentColor;
    }
    updateToolButtons();
}
function updateToolButtons() {
    const eraserBtn = document.getElementById('eraser');
    const penBtn = document.getElementById('pen');
    
    if (currentTool === 'eraser') {
        eraserBtn.className = 'px-4 py-2 rounded-lg bg-gray-500 hover:bg-gray-600 text-white font-medium transition-all duration-200 hover:scale-105 shadow-lg';
        penBtn.className = 'px-4 py-2 rounded-lg bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-800 dark:text-white font-medium transition-all duration-200 hover:scale-105 shadow-lg';
    } else {
        eraserBtn.className = 'px-4 py-2 rounded-lg bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-800 dark:text-white font-medium transition-all duration-200 hover:scale-105 shadow-lg';
        penBtn.className = 'px-4 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-medium transition-all duration-200 hover:scale-105 shadow-lg';
    }
}
function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    hideResults();
}
function startDrawing(e) {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    ctx.beginPath();
    ctx.moveTo((e.clientX - rect.left) * scaleX, (e.clientY - rect.top) * scaleY);
}
function draw(e) {
    if (!isDrawing) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    ctx.lineTo((e.clientX - rect.left) * scaleX, (e.clientY - rect.top) * scaleY);
    ctx.stroke();
}
function stopDrawing() {
    isDrawing = false;
}
function handleTouch(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    
    const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 
                                     e.type === 'touchmove' ? 'mousemove' : 'mouseup', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}
function predictMood() {
    const dataURL = canvas.toDataURL('image/png');
    
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: dataURL })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        showResults(data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to predict mood');
    });
}
function showResults(data) {
    document.getElementById('resultArea').style.opacity = '0.4';
    document.getElementById('moodCard').style.display = 'block';
    
    document.getElementById('moodText').textContent = data.mood.charAt(0).toUpperCase() + data.mood.slice(1);
    
    const emojis = {
        happy: '😊',
        calm: '😌',
        sad: '😢',
        energetic: '⚡'
    };
    document.getElementById('emoji').textContent = emojis[data.mood] || '🙂';
    
    window.currentTrackUrl = data.track_url;
    window.currentHistoryId = data.history_id;
    updateTrackInfo();
}
function hideResults() {
    document.getElementById('resultArea').style.opacity = '1';
    document.getElementById('moodCard').style.display = 'none';
    stopAudio();
}
function playAudio() {
    if (!window.currentTrackUrl) return;
    
    stopAudio();
    
    const volumeSlider = document.getElementById('volumeSlider');
    const volume = volumeSlider ? parseInt(volumeSlider.value) / 100 : 0.7;
    
    currentSound = new Howl({
        src: [window.currentTrackUrl],
        volume: volume,
        onload: function() {
            updateTrackInfo();
            updateProgress();
        },
        onplay: function() {
            showPauseButton();
            updateProgress();
        },
        onpause: function() {
            showPlayButton();
        },
        onend: function() {
            showPlayButton();
            resetProgress();
        },
        onloaderror: function() {
            console.log('Audio file not found');
            updateTrackInfo('Audio file not available');
        }
    });
    
    currentSound.play();
}

function pauseAudio() {
    if (currentSound && currentSound.playing()) {
        currentSound.pause();
    }
}

function stopAudio() {
    if (currentSound) {
        currentSound.stop();
        currentSound = null;
        showPlayButton();
        resetProgress();
    }
}

function showPlayButton() {
    const playBtn = document.getElementById('playBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    if (playBtn && pauseBtn) {
        playBtn.style.display = 'block';
        pauseBtn.style.display = 'none';
    }
}

function showPauseButton() {
    const playBtn = document.getElementById('playBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    if (playBtn && pauseBtn) {
        playBtn.style.display = 'none';
        pauseBtn.style.display = 'block';
    }
}

function updateTrackInfo(message = null) {
    const trackName = document.getElementById('trackName');
    if (!trackName) return;
    
    if (message) {
        trackName.textContent = message;
        return;
    }
    
    if (window.currentTrackUrl) {
        const filename = window.currentTrackUrl.split('/').pop();
        const moodType = filename.replace('.wav', '').replace(/[12]$/, '');
        const trackNumber = filename.match(/[12]$/) ? filename.match(/[12]$/)[0] : '1';
        trackName.textContent = `${moodType.charAt(0).toUpperCase() + moodType.slice(1)} Melody ${trackNumber}`;
    }
}

function updateProgress() {
    if (!currentSound) return;
    
    const progressFill = document.getElementById('progressFill');
    const currentTimeEl = document.getElementById('currentTime');
    const totalTimeEl = document.getElementById('totalTime');
    
    if (!progressFill || !currentTimeEl || !totalTimeEl) return;
    
    const seek = currentSound.seek() || 0;
    const duration = currentSound.duration() || 0;
    
    if (duration > 0) {
        const progress = (seek / duration) * 100;
        progressFill.style.width = progress + '%';
        
        currentTimeEl.textContent = formatTime(seek);
        totalTimeEl.textContent = formatTime(duration);
    }
    
    if (currentSound.playing()) {
        requestAnimationFrame(updateProgress);
    }
}

function resetProgress() {
    const progressFill = document.getElementById('progressFill');
    const currentTimeEl = document.getElementById('currentTime');
    const totalTimeEl = document.getElementById('totalTime');
    
    if (progressFill) progressFill.style.width = '0%';
    if (currentTimeEl) currentTimeEl.textContent = '0:00';
    if (totalTimeEl) totalTimeEl.textContent = '0:00';
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return mins + ':' + (secs < 10 ? '0' : '') + secs;
}

function initAudioControls() {
    const playBtn = document.getElementById('playBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const stopBtn = document.getElementById('stopBtn');
    const volumeSlider = document.getElementById('volumeSlider');
    const volumeDisplay = document.getElementById('volumeDisplay');
    const progressBar = document.getElementById('progressBar');
    
    if (playBtn) {
        playBtn.addEventListener('click', playAudio);
    }
    
    if (pauseBtn) {
        pauseBtn.addEventListener('click', pauseAudio);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopAudio);
    }
    
    if (volumeSlider && volumeDisplay) {
        volumeSlider.addEventListener('input', function() {
            const volume = parseInt(this.value) / 100;
            volumeDisplay.textContent = this.value + '%';
            
            if (currentSound) {
                currentSound.volume(volume);
            }
        });
    }
    
    if (progressBar) {
        progressBar.addEventListener('click', function(e) {
            if (!currentSound) return;
            
            const rect = this.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const width = rect.width;
            const percentage = clickX / width;
            const duration = currentSound.duration();
            
            if (duration > 0) {
                const seekTime = duration * percentage;
                currentSound.seek(seekTime);
            }
        });
    }
}
function submitRating() {
    const rating = document.getElementById('rating').value;
    if (!rating || !window.currentHistoryId) return;
    
    fetch('/rate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            history_id: window.currentHistoryId,
            rating: parseInt(rating)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            alert('Rating submitted!');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
updateToolButtons();
updateColorButtons();
setBrushSize(3); // Set initial brush size
