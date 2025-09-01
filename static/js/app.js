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
}
function hideResults() {
    document.getElementById('resultArea').style.opacity = '1';
    document.getElementById('moodCard').style.display = 'none';
    stopAudio();
}
function playAudio() {
    if (!window.currentTrackUrl) return;
    
    stopAudio();
    currentSound = new Howl({
        src: [window.currentTrackUrl],
        volume: 0.7,
        onloaderror: function() {
            console.log('Audio file not found, playing placeholder');
        }
    });
    currentSound.play();
}
function stopAudio() {
    if (currentSound) {
        currentSound.stop();
        currentSound = null;
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
