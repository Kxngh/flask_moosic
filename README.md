# Flask Moosic - Mood-Based Music from Doodles

A Flask web application that analyzes user drawings/doodles to predict mood and recommend music tracks accordingly.

## Features

- **Drawing Interface**: Interactive canvas for users to create doodles
- **Mood Detection**: AI-powered mood analysis from drawings using image processing
- **Music Recommendation**: Curated audio tracks based on detected mood (happy, calm, sad, energetic)
- **History Tracking**: Save and review previous doodles with their mood predictions
- **User Feedback**: Rating system and mood relabeling for model improvement
- **Data Export**: Export history data as CSV

## Mood Categories

- **Happy**: Upbeat, joyful music
- **Calm**: Relaxing, peaceful tracks
- **Sad**: Melancholic, reflective music
- **Energetic**: High-energy, motivational tracks

## Technology Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite (development), PostgreSQL (production)
- **Image Processing**: PIL (Pillow)
- **Frontend**: HTML5 Canvas, JavaScript
- **Deployment**: Ready for Render.com

## Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python app.py`
6. Open `http://localhost:5000` in your browser

## Deployment on Render

This application is configured for deployment on Render.com:

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
4. Add a PostgreSQL database add-on
5. The application will automatically use PostgreSQL in production

## Project Structure

```
flask_moosic/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Process file for deployment
├── runtime.txt           # Python version specification
├── static/               # Static assets
│   ├── audio/           # Music files organized by mood
│   └── js/              # Frontend JavaScript
├── templates/           # HTML templates
├── uploads/             # User-generated doodle images
└── instance/           # Database files (development)
```

## API Endpoints

- `GET /` - Main application interface
- `GET /history` - View prediction history
- `POST /predict` - Submit doodle for mood prediction
- `POST /rate` - Rate and relabel predictions
- `GET /export.csv` - Export history data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE). 
