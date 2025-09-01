import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import cv2
from PIL import Image, ImageOps, ImageStat
import os
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import io
import base64

class SketchMoodCNN:
    def __init__(self, model_path='ml/sketch_mood_model.h5', label_encoder_path='ml/label_encoder.pkl'):
        self.model_path = model_path
        self.label_encoder_path = label_encoder_path
        self.model = None
        self.label_encoder = None
        self.input_shape = (64, 64, 1)
        self.mood_classes = ['happy', 'calm', 'sad', 'energetic']
        
        self._load_or_create_model()
    
    def _create_model(self):
        model = keras.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape),
            layers.BatchNormalization(),
            layers.Conv2D(32, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(len(self.mood_classes), activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.label_encoder_path):
                print("Loading existing model...")
                self.model = keras.models.load_model(self.model_path)
                with open(self.label_encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                print("Model loaded successfully!")
            else:
                print("Creating new model...")
                self.model = self._create_model()
                self.label_encoder = LabelEncoder()
                self.label_encoder.fit(self.mood_classes)
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Creating new model...")
            self.model = self._create_model()
            self.label_encoder = LabelEncoder()
            self.label_encoder.fit(self.mood_classes)
    
    def preprocess_image(self, image):
        """Preprocess image for model prediction"""
        if isinstance(image, str):

            header, b64 = image.split(',', 1) if ',' in image else (None, image)
            image_bytes = base64.b64decode(b64)
            image = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
        
        if isinstance(image, Image.Image):
            if image.mode == 'RGBA':
                background = Image.new('RGBA', image.size, (255, 255, 255, 255))
                image = Image.alpha_composite(background, image).convert('RGB')
            
            image = ImageOps.fit(image, (64, 64)).convert('L')
            image_array = np.array(image)
        else:
            image_array = image
        
        image_array = image_array.astype('float32') / 255.0
        
        image_array = np.expand_dims(image_array, axis=-1)
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    def predict_from_pil(self, pil_img):
        try:
            processed_image = self.preprocess_image(pil_img)
            
            predictions = self.model.predict(processed_image, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            
            mood = self.mood_classes[predicted_class_idx]
            
            return mood, confidence
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._dummy_prediction(pil_img)
    
    def _dummy_prediction(self, pil_img):
        """Fallback dummy prediction if model fails"""
        import random
        stat = ImageStat.Stat(pil_img)
        mean = stat.mean[0] if hasattr(stat.mean, '__getitem__') else stat.mean
        
        if mean > 220:
            mood = random.choice(['calm', 'happy'])
            conf = 0.6 + (mean - 220) / 35 * 0.4
        elif mean > 120:
            mood = random.choice(['happy', 'energetic'])
            conf = 0.5 + (mean - 120) / 100 * 0.5
        else:
            mood = random.choice(['sad', 'energetic'])
            conf = 0.55
        
        return mood, min(max(conf, 0.0), 0.99)
    
    def train_model(self, X_train, y_train, X_val=None, y_val=None, epochs=50, batch_size=32):
        print(f"Training model with {len(X_train)} samples...")
        
        y_train_encoded = keras.utils.to_categorical(
            self.label_encoder.transform(y_train), 
            num_classes=len(self.mood_classes)
        )
        
        if X_val is not None and y_val is not None:
            y_val_encoded = keras.utils.to_categorical(
                self.label_encoder.transform(y_val),
                num_classes=len(self.mood_classes)
            )
            validation_data = (X_val, y_val_encoded)
        else:
            validation_data = None
        
        callbacks = [
            keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.5),
            keras.callbacks.ModelCheckpoint(self.model_path, save_best_only=True)
        ]
        
        history = self.model.fit(
            X_train, y_train_encoded,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=1
        )
        

        os.makedirs(os.path.dirname(self.label_encoder_path), exist_ok=True)
        with open(self.label_encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        
        print("Model training completed and saved!")
        return history
    
    def load_dataset_from_folder(self, dataset_path):
        """Load dataset from organized folder structure"""
        images = []
        labels = []
        
        for mood in self.mood_classes:
            mood_path = os.path.join(dataset_path, mood)
            if os.path.exists(mood_path):
                for filename in os.listdir(mood_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(mood_path, filename)
                        try:

                            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                            img = cv2.resize(img, (64, 64))
                            img = img.astype('float32') / 255.0
                            img = np.expand_dims(img, axis=-1)
                            
                            images.append(img)
                            labels.append(mood)
                        except Exception as e:
                            print(f"Error loading {img_path}: {e}")
        
        if len(images) == 0:
            print("No images found in dataset!")
            return None, None
        
        return np.array(images), np.array(labels)
    
    def augment_data(self, images, labels, augment_factor=3):
        """Apply data augmentation to increase dataset size"""
        augmented_images = []
        augmented_labels = []
        

        augmented_images.extend(images)
        augmented_labels.extend(labels)
        

        for i in range(len(images)):
            img = images[i]
            label = labels[i]
            
            for _ in range(augment_factor):

                angle = np.random.uniform(-15, 15)
                h, w = img.shape[:2]
                center = (w // 2, h // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(img[:,:,0], rotation_matrix, (w, h))
                rotated = np.expand_dims(rotated, axis=-1)
                

                zoom_factor = np.random.uniform(0.9, 1.1)
                h, w = rotated.shape[:2]
                new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
                resized = cv2.resize(rotated[:,:,0], (new_w, new_h))
                

                if new_h > h or new_w > w:

                    start_y = (new_h - h) // 2
                    start_x = (new_w - w) // 2
                    cropped = resized[start_y:start_y+h, start_x:start_x+w]
                else:

                    pad_y = (h - new_h) // 2
                    pad_x = (w - new_w) // 2
                    cropped = np.pad(resized, ((pad_y, h-new_h-pad_y), (pad_x, w-new_w-pad_x)), 'constant')
                
                cropped = np.expand_dims(cropped, axis=-1)
                

                if np.random.random() > 0.5:
                    cropped = np.fliplr(cropped)
                

                noise = np.random.normal(0, 0.02, cropped.shape)
                noisy = np.clip(cropped + noise, 0, 1)
                
                augmented_images.append(noisy)
                augmented_labels.append(label)
        
        return np.array(augmented_images), np.array(augmented_labels)


sketch_model = None

def get_model():
    """Get or create the global model instance"""
    global sketch_model
    if sketch_model is None:
        sketch_model = SketchMoodCNN()
    return sketch_model
