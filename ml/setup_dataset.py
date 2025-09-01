#!/usr/bin/env python3
"""
Quick dataset setup script - creates dataset structure and can generate simple synthetic doodles for testing
"""

import os
import numpy as np
from PIL import Image, ImageDraw
import random

def create_dataset_structure(output_path):
    """Create the dataset folder structure"""
    moods = ['happy', 'calm', 'sad', 'energetic']
    
    for mood in moods:
        mood_dir = os.path.join(output_path, mood)
        os.makedirs(mood_dir, exist_ok=True)
        print(f"Created directory: {mood_dir}")
    
    print(f"\n✅ Dataset structure created at: {output_path}")
    return output_path

def generate_simple_synthetic_doodles(dataset_path, samples_per_mood=50):
    """Generate simple synthetic doodles for initial testing (NOT for production)"""
    
    print("🎨 Generating synthetic doodles for testing...")
    print("⚠️  Note: These are simple shapes for testing only. Replace with real doodles!")
    
    def draw_happy_doodle():
        img = Image.new('RGB', (64, 64), 'white')
        draw = ImageDraw.Draw(img)
        # Smiley face
        draw.ellipse([10, 10, 54, 54], outline='black', width=2)
        draw.ellipse([20, 20, 25, 25], fill='black')  # Left eye
        draw.ellipse([39, 20, 44, 25], fill='black')  # Right eye
        draw.arc([20, 25, 44, 45], 0, 180, fill='black', width=2)  # Smile
        return img
    
    def draw_calm_doodle():
        img = Image.new('RGB', (64, 64), 'white')
        draw = ImageDraw.Draw(img)
        # Gentle waves
        for y in range(20, 50, 8):
            for x in range(0, 64, 4):
                draw.ellipse([x, y + random.randint(-2, 2), x+2, y+2], fill='black')
        return img
    
    def draw_sad_doodle():
        img = Image.new('RGB', (64, 64), 'white')
        draw = ImageDraw.Draw(img)
        # Sad face
        draw.ellipse([10, 10, 54, 54], outline='black', width=2)
        draw.ellipse([20, 20, 25, 25], fill='black')  # Left eye
        draw.ellipse([39, 20, 44, 25], fill='black')  # Right eye
        draw.arc([20, 35, 44, 55], 180, 360, fill='black', width=2)  # Frown
        # Teardrops
        draw.ellipse([18, 30, 22, 40], fill='blue')
        return img
    
    def draw_energetic_doodle():
        img = Image.new('RGB', (64, 64), 'white')
        draw = ImageDraw.Draw(img)
        # Lightning bolt
        points = [(25, 5), (35, 5), (20, 35), (30, 35), (15, 60), (40, 25), (30, 25), (45, 5)]
        draw.polygon(points, fill='black')
        return img
    
    mood_generators = {
        'happy': draw_happy_doodle,
        'calm': draw_calm_doodle,
        'sad': draw_sad_doodle,
        'energetic': draw_energetic_doodle
    }
    
    for mood, generator in mood_generators.items():
        mood_dir = os.path.join(dataset_path, mood)
        print(f"Generating {samples_per_mood} {mood} doodles...")
        
        for i in range(samples_per_mood):
            # Generate base doodle
            img = generator()
            
            # Add some variation
            img_array = np.array(img)
            
            # Random rotation
            angle = random.uniform(-10, 10)
            img = img.rotate(angle, fillcolor='white')
            
            # Random noise
            img_array = np.array(img)
            noise = np.random.normal(0, 5, img_array.shape)
            img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(img_array)
            
            # Save
            filename = f"synthetic_{mood}_{i:03d}.png"
            filepath = os.path.join(mood_dir, filename)
            img.save(filepath)
        
        print(f"  ✅ Saved {samples_per_mood} images to {mood_dir}")
    
    print(f"\n✅ Generated {samples_per_mood * 4} synthetic doodles total")
    print("⚠️  Remember to replace these with real hand-drawn doodles for better accuracy!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup dataset for sketch mood classification")
    parser.add_argument("--output", type=str, default="ml/dataset", help="Output directory for dataset")
    parser.add_argument("--synthetic", action="store_true", help="Generate synthetic doodles for testing")
    parser.add_argument("--samples", type=int, default=50, help="Number of synthetic samples per mood")
    
    args = parser.parse_args()
    
    # Create dataset structure
    dataset_path = create_dataset_structure(args.output)
    
    if args.synthetic:
        generate_simple_synthetic_doodles(dataset_path, args.samples)
        
        print("\n" + "="*50)
        print("🚀 NEXT STEPS:")
        print("="*50)
        print(f"1. Review generated doodles in: {dataset_path}")
        print("2. Replace with real hand-drawn doodles for better accuracy")
        print("3. Train the model:")
        print(f"   python ml/train_model.py --dataset_path {dataset_path}")
        print("4. The trained model will be saved and automatically used in the Flask app")
    else:
        print("\n" + "="*50)
        print("📁 DATASET STRUCTURE READY")
        print("="*50)
        print(f"Add your doodle images to: {dataset_path}")
        print("Folder structure:")
        for mood in ['happy', 'calm', 'sad', 'energetic']:
            print(f"  {dataset_path}/{mood}/ - Add {mood} doodles here")
        print("\nThen run:")
        print(f"python ml/train_model.py --dataset_path {dataset_path}")
