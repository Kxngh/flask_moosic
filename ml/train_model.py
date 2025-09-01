#!/usr/bin/env python3
"""
Training script for the Sketch Mood CNN model
Usage: python train_model.py --dataset_path /path/to/dataset
"""

import os
import sys
import argparse
from sklearn.model_selection import train_test_split
import numpy as np

# Add the parent directory to sys.path to import from ml module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.sketch_cnn_model import SketchMoodCNN

def train_model(dataset_path, epochs=50, batch_size=32, test_size=0.2, augment=True):
    """Train the sketch mood classification model"""
    
    print("🚀 Starting model training...")
    print(f"Dataset path: {dataset_path}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")
    print(f"Test split: {test_size}")
    print(f"Data augmentation: {augment}")
    print("-" * 50)
    
    # Initialize model
    model = SketchMoodCNN()
    
    # Load dataset
    print("📂 Loading dataset...")
    X, y = model.load_dataset_from_folder(dataset_path)
    
    if X is None or len(X) == 0:
        print("❌ No data found! Please check your dataset structure.")
        print("Expected structure:")
        print("dataset/")
        print("├── happy/")
        print("│   ├── image1.png")
        print("│   └── image2.png")
        print("├── calm/")
        print("├── sad/")
        print("└── energetic/")
        return None
    
    print(f"✅ Loaded {len(X)} images")
    print("Class distribution:")
    unique, counts = np.unique(y, return_counts=True)
    for mood, count in zip(unique, counts):
        print(f"  {mood}: {count} images")
    
    # Data augmentation
    if augment and len(X) < 200:
        print("\n🔄 Applying data augmentation...")
        X, y = model.augment_data(X, y, augment_factor=max(1, 200 // len(X)))
        print(f"✅ Dataset size after augmentation: {len(X)} images")
        
        print("Updated class distribution:")
        unique, counts = np.unique(y, return_counts=True)
        for mood, count in zip(unique, counts):
            print(f"  {mood}: {count} images")
    
    # Split dataset
    print(f"\n📊 Splitting dataset (test size: {test_size})...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train)} images")
    print(f"Test set: {len(X_test)} images")
    
    # Train model
    print(f"\n🤖 Training model for {epochs} epochs...")
    history = model.train_model(
        X_train, y_train, 
        X_test, y_test,
        epochs=epochs, 
        batch_size=batch_size
    )
    
    # Evaluate model
    print("\n📈 Evaluating model...")
    test_loss, test_accuracy = model.model.evaluate(X_test, np.eye(4)[model.label_encoder.transform(y_test)], verbose=0)
    print(f"Test Accuracy: {test_accuracy:.4f}")
    print(f"Test Loss: {test_loss:.4f}")
    
    print("\n✅ Training completed successfully!")
    print(f"Model saved to: {model.model_path}")
    print(f"Label encoder saved to: {model.label_encoder_path}")
    
    return model, history

def create_sample_dataset(output_path):
    """Create a sample dataset structure with placeholder instructions"""
    
    moods = ['happy', 'calm', 'sad', 'energetic']
    
    for mood in moods:
        mood_dir = os.path.join(output_path, mood)
        os.makedirs(mood_dir, exist_ok=True)
        
        # Create instruction file
        instruction_file = os.path.join(mood_dir, 'README.txt')
        
        instructions = {
            'happy': "Add drawings of: smiling faces, suns, flowers, hearts, rainbows, stars, thumbs up",
            'calm': "Add drawings of: waves, clouds, trees, mountains, meditation poses, gentle curves",
            'sad': "Add drawings of: tears, rain, wilted flowers, downward arrows, broken hearts",
            'energetic': "Add drawings of: lightning bolts, zigzags, explosions, exclamation marks, dynamic lines"
        }
        
        with open(instruction_file, 'w') as f:
            f.write(f"MOOD: {mood.upper()}\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Place your {mood} doodle images in this folder.\n\n")
            f.write("Suggested drawings:\n")
            f.write(instructions[mood] + "\n\n")
            f.write("Supported formats: .png, .jpg, .jpeg\n")
            f.write("Recommended size: Any size (will be resized to 64x64)\n")
            f.write("Background: Any (preferably white/light)\n")
    
    print(f"📁 Sample dataset structure created at: {output_path}")
    print("\nNext steps:")
    print("1. Add your doodle images to the respective mood folders")
    print("2. Run: python train_model.py --dataset_path " + output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Sketch Mood Classification Model")
    parser.add_argument("--dataset_path", type=str, required=True, help="Path to dataset folder")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for training")
    parser.add_argument("--test_size", type=float, default=0.2, help="Test set proportion")
    parser.add_argument("--no_augment", action="store_true", help="Disable data augmentation")
    parser.add_argument("--create_sample", action="store_true", help="Create sample dataset structure")
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_dataset(args.dataset_path)
    else:
        if not os.path.exists(args.dataset_path):
            print(f"❌ Dataset path does not exist: {args.dataset_path}")
            print("Use --create_sample to create the dataset structure first")
            sys.exit(1)
        
        train_model(
            args.dataset_path,
            epochs=args.epochs,
            batch_size=args.batch_size,
            test_size=args.test_size,
            augment=not args.no_augment
        )
