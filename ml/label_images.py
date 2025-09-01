#!/usr/bin/env python3
"""
Interactive dataset labeling tool
Helps you organize screenshots into mood categories
"""

import os
import shutil
from PIL import Image
import matplotlib.pyplot as plt

def interactive_label_images(source_folder, dataset_folder):
    """Interactively label images by showing them and asking for mood"""
    
    # Create mood directories
    moods = ['happy', 'calm', 'sad', 'energetic']
    for mood in moods:
        os.makedirs(os.path.join(dataset_folder, mood), exist_ok=True)
    
    # Get all image files
    image_files = []
    for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
        image_files.extend([f for f in os.listdir(source_folder) if f.lower().endswith(ext)])
    
    if not image_files:
        print(f"❌ No image files found in {source_folder}")
        return
    
    print(f"🏷️  Found {len(image_files)} images to label")
    print("📋 Instructions:")
    print("  1 = happy")
    print("  2 = calm") 
    print("  3 = sad")
    print("  4 = energetic")
    print("  s = skip")
    print("  q = quit")
    print("-" * 40)
    
    labeled_count = 0
    
    for i, filename in enumerate(image_files):
        source_path = os.path.join(source_folder, filename)
        
        # Display image
        try:
            img = Image.open(source_path)
            plt.figure(figsize=(6, 6))
            plt.imshow(img, cmap='gray' if img.mode == 'L' else None)
            plt.title(f"Image {i+1}/{len(image_files)}: {filename}")
            plt.axis('off')
            plt.show()
            
            # Get user input
            while True:
                choice = input(f"Label for '{filename}' (1-4, s, q): ").strip().lower()
                
                if choice == 'q':
                    print(f"✅ Labeled {labeled_count} images. Exiting.")
                    return
                elif choice == 's':
                    print("⏭️  Skipped")
                    break
                elif choice in ['1', '2', '3', '4']:
                    mood = moods[int(choice) - 1]
                    
                    # Generate new filename
                    base_name = os.path.splitext(filename)[0]
                    ext = os.path.splitext(filename)[1]
                    new_filename = f"{mood}_{labeled_count:03d}{ext}"
                    
                    # Copy to mood folder
                    dest_path = os.path.join(dataset_folder, mood, new_filename)
                    shutil.copy2(source_path, dest_path)
                    
                    print(f"✅ Labeled as '{mood}' → {dest_path}")
                    labeled_count += 1
                    break
                else:
                    print("Invalid choice. Use 1-4, s, or q")
            
            plt.close()
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue
    
    print(f"\n🎉 Labeling complete! Labeled {labeled_count} images")
    
    # Show summary
    print("\n📊 Dataset Summary:")
    for mood in moods:
        mood_path = os.path.join(dataset_folder, mood)
        count = len([f for f in os.listdir(mood_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        print(f"  {mood}: {count} images")

def batch_move_files(source_folder, dataset_folder):
    """Batch move files based on filename patterns"""
    
    # Create mood directories
    moods = ['happy', 'calm', 'sad', 'energetic']
    for mood in moods:
        os.makedirs(os.path.join(dataset_folder, mood), exist_ok=True)
    
    moved_files = {mood: 0 for mood in moods}
    
    for filename in os.listdir(source_folder):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
            
        source_path = os.path.join(source_folder, filename)
        filename_lower = filename.lower()
        
        # Try to detect mood from filename
        detected_mood = None
        for mood in moods:
            if mood in filename_lower:
                detected_mood = mood
                break
        
        if detected_mood:
            dest_path = os.path.join(dataset_folder, detected_mood, filename)
            shutil.move(source_path, dest_path)
            moved_files[detected_mood] += 1
            print(f"✅ Moved {filename} → {detected_mood}/")
    
    print(f"\n📊 Batch Move Summary:")
    for mood, count in moved_files.items():
        print(f"  {mood}: {count} files moved")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Label images for mood classification")
    parser.add_argument("--source", required=True, help="Source folder with images to label")
    parser.add_argument("--dataset", default="ml/dataset", help="Dataset folder to organize images")
    parser.add_argument("--interactive", action="store_true", help="Use interactive labeling")
    parser.add_argument("--batch", action="store_true", help="Use batch mode (detect from filenames)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source):
        print(f"❌ Source folder does not exist: {args.source}")
        exit(1)
    
    if args.interactive:
        print("🏷️  Starting interactive labeling...")
        interactive_label_images(args.source, args.dataset)
    elif args.batch:
        print("📦 Starting batch mode...")
        batch_move_files(args.source, args.dataset)
    else:
        print("❌ Please specify --interactive or --batch mode")
        print("\nExamples:")
        print("  python ml/label_images.py --source screenshots/ --dataset ml/dataset --interactive")
        print("  python ml/label_images.py --source screenshots/ --dataset ml/dataset --batch")
