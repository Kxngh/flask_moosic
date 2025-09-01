import os
from flask import Flask, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import base64
import io
import random
from PIL import Image, ImageOps, ImageStat

app = Flask(__name__)

# Database configuration - use PostgreSQL in production, SQLite in development
if os.environ.get('DATABASE_URL'):
    # Production database (PostgreSQL on Render)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    # Development database (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mood_app.db'

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    mood_pred = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    track_path = db.Column(db.String(200))
    image_path = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    relabel = db.Column(db.String(50))
    
    def as_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'mood_pred': self.mood_pred,
            'confidence': self.confidence,
            'track_path': self.track_path,
            'image_path': self.image_path,
            'rating': self.rating,
            'relabel': self.relabel
        }

# Dummy Model Class
class DummyMoodModel:
    def __init__(self):
        pass

    def predict_from_pil(self, pil_img):
        """Accepts a PIL grayscale image (64x64). Returns (mood, confidence)"""
        # heuristic: mean brightness
        stat = ImageStat.Stat(pil_img)
        mean = stat.mean[0]
        # mean near white -> calm/happy, near black -> energetic/sad randomly
        if mean > 220:
            mood = random.choice(['calm','happy'])
            conf = 0.6 + (mean - 220)/35 * 0.4
        elif mean > 120:
            mood = random.choice(['happy','energetic'])
            conf = 0.5 + (mean - 120)/100 * 0.5
        else:
            mood = random.choice(['sad','energetic'])
            conf = 0.55
        return mood, min(max(conf, 0.0), 0.99)

# Initialize model and audio mappings
MODEL = DummyMoodModel()
MOOD_AUDIO = {
    'happy': ['static/audio/happy1.mp3', 'static/audio/happy2.mp3'],
    'calm': ['static/audio/calm1.mp3', 'static/audio/calm2.mp3'],
    'sad': ['static/audio/sad1.mp3', 'static/audio/sad2.mp3'],
    'energetic': ['static/audio/energetic1.mp3', 'static/audio/energetic2.mp3']
}

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('history.html')

@app.route('/history')
def history():
    entries = History.query.order_by(History.timestamp.desc()).all()
    return render_template('index.html', entries=entries)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json.get('image')
    if not data:
        return jsonify({'error': 'no image received'}), 400

    # data is expected like: data:image/png;base64,AAAA...
    header, b64 = data.split(',', 1) if ',' in data else (None, data)
    image_bytes = base64.b64decode(b64)

    # save original user submission
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'sketch_{timestamp}.png')
    with open(image_path, 'wb') as f:
        f.write(image_bytes)

    # Basic preprocessing for dummy model: resize + convert to gray
    img = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
    # merge alpha onto white background
    background = Image.new('RGBA', img.size, (255, 255, 255, 255))
    image_merged = Image.alpha_composite(background, img).convert('RGB')
    image_resized = ImageOps.fit(image_merged, (64, 64)).convert('L')

    # pass PIL image to model (dummy accepts PIL)
    mood, confidence = MODEL.predict_from_pil(image_resized)

    track = random.choice(MOOD_AUDIO.get(mood, []))

    # Log to DB
    h = History(mood_pred=mood, confidence=float(confidence), track_path=track, image_path=image_path)
    db.session.add(h)
    db.session.commit()

    return jsonify({
        'mood': mood,
        'confidence': float(confidence),
        'track_url': '/' + track,
        'history_id': h.id
    })



@app.route('/rate', methods=['POST'])
def rate():
    payload = request.json
    hid = payload.get('history_id')
    rating = payload.get('rating')
    relabel = payload.get('relabel')
    entry = History.query.get(hid)
    if not entry:
        return jsonify({'error': 'not found'}), 404
    if rating is not None:
        try:
            entry.rating = int(rating)
        except Exception:
            pass
    if relabel:
        entry.relabel = relabel
    db.session.commit()
    return jsonify({'ok': True, 'entry': entry.as_dict()})

@app.route('/export.csv')
def export_csv():
    import csv
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','timestamp','mood_pred','confidence','track_path','image_path','rating','relabel'])
    for e in History.query.order_by(History.timestamp.asc()).all():
        cw.writerow([e.id, e.timestamp.isoformat(), e.mood_pred, e.confidence, e.track_path, e.image_path, e.rating, e.relabel])
    return send_file(io.BytesIO(si.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='history.csv')

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    # Disable debug in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)