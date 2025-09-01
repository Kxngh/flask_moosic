# TensorFlow CNN Model Setup

## Overview
This Flask application uses a Convolutional Neural Network (CNN) built with TensorFlow/Keras to classify hand-drawn sketches into mood categories: **happy**, **calm**, **sad**, and **energetic**.

## Model Architecture

### CNN Structure:
```
Input: 64x64 grayscale images
│
├── Conv2D(32, 3x3) + BatchNorm + ReLU
├── Conv2D(32, 3x3) + MaxPool2D + Dropout(0.25)
│
├── Conv2D(64, 3x3) + BatchNorm + ReLU  
├── Conv2D(64, 3x3) + MaxPool2D + Dropout(0.25)
│
├── Conv2D(128, 3x3) + BatchNorm + ReLU
├── Conv2D(128, 3x3) + MaxPool2D + Dropout(0.25)
│
├── Flatten
├── Dense(512) + BatchNorm + ReLU + Dropout(0.5)
├── Dense(256) + ReLU + Dropout(0.5)
└── Dense(4, softmax) → [happy, calm, sad, energetic]
```

## Quick Start

### 1. Setup Dataset (Option A: Synthetic for Testing)
```bash
# Create synthetic doodles for immediate testing
python ml/setup_dataset.py --output ml/dataset --synthetic --samples 50
```

### 2. Setup Dataset (Option B: Real Doodles - Recommended)
```bash
# Create folder structure
python ml/setup_dataset.py --output ml/dataset

# Add your doodles to:
ml/dataset/happy/     # Smiles, suns, hearts, flowers
ml/dataset/calm/      # Waves, trees, clouds, curves  
ml/dataset/sad/       # Tears, rain, frowns, wilted flowers
ml/dataset/energetic/ # Lightning, zigzags, explosions, exclamations
```

### 3. Train the Model
```bash
# Train with your dataset
python ml/train_model.py --dataset_path ml/dataset --epochs 50

# Quick training (for testing)
python ml/train_model.py --dataset_path ml/dataset --epochs 10 --batch_size 16
```

### 4. Run Flask App
```bash
python app.py
```

The app will automatically detect and use the trained TensorFlow model. If no model exists, it falls back to a dummy model.

## Model Files

- **`ml/sketch_mood_model.h5`** - Trained TensorFlow model
- **`ml/label_encoder.pkl`** - Label encoder for mood classes
- **`ml/dataset/`** - Training dataset organized by mood
- **`ml/sketch_cnn_model.py`** - CNN model implementation
- **`ml/train_model.py`** - Training script
- **`ml/setup_dataset.py`** - Dataset setup utility

## Model Status API

Check model status at: `GET /model-status`

Returns:
```json
{
  "using_tensorflow": true,
  "model_type": "TensorFlow CNN",
  "model_exists": true,
  "dataset_exists": true,
  "dataset_info": {
    "happy": 50,
    "calm": 50, 
    "sad": 50,
    "energetic": 50
  },
  "total_images": 200
}
```

## Data Augmentation

The training pipeline includes automatic data augmentation:
- Random rotation (±15°)
- Random zoom (0.9x - 1.1x)
- Horizontal flipping
- Gaussian noise addition

## Training Tips

### For Better Accuracy:
1. **Collect Real Doodles**: Hand-drawn sketches work much better than synthetic shapes
2. **Balanced Dataset**: Aim for 50+ images per mood category
3. **Diverse Styles**: Include different drawing styles and stroke weights
4. **Clear Categories**: Make sure doodles clearly represent their mood

### Recommended Dataset Size:
- **Minimum**: 25 images per mood (100 total)
- **Good**: 50 images per mood (200 total) 
- **Excellent**: 100+ images per mood (400+ total)

## Deployment Notes

- The model automatically handles production/development environments
- TensorFlow is included in `requirements.txt` for deployment
- Fallback dummy model ensures the app works even without trained model
- Model files are automatically created in the `ml/` directory

## Troubleshooting

### Model Not Loading?
1. Check if `ml/sketch_mood_model.h5` exists
2. Verify TensorFlow installation: `pip install tensorflow`
3. Check `/model-status` endpoint for details

### Poor Accuracy?
1. Add more real hand-drawn doodles
2. Ensure balanced dataset across all moods
3. Increase training epochs
4. Add more diverse drawing styles

### Training Fails?
1. Verify dataset structure matches expected format
2. Ensure images are valid PNG/JPG files
3. Check available memory (TensorFlow is memory-intensive)
4. Try reducing batch size: `--batch_size 16`
