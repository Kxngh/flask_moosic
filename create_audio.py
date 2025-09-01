#!/usr/bin/env python3

import wave
import math
import os

def create_sine_wave(frequency, duration, sample_rate=22050, amplitude=0.3):
    """Create a simple sine wave"""
    frames = int(duration * sample_rate)
    audio_data = []
    
    for i in range(frames):
        # Generate sine wave
        value = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
        # Convert to 16-bit integer
        audio_data.append(int(value * 32767))
    
    return audio_data

def create_melody(frequencies, note_duration=0.5, sample_rate=22050):
    """Create a melody from a list of frequencies"""
    melody = []
    
    for freq in frequencies:
        if freq > 0:
            note = create_sine_wave(freq, note_duration, sample_rate)
        else:
            # Rest (silence)
            note = [0] * int(note_duration * sample_rate)
        melody.extend(note)
    
    return melody

def save_wav_file(audio_data, filename, sample_rate=22050):
    """Save audio data to WAV file"""
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        # Convert to bytes
        audio_bytes = b''.join([int(sample).to_bytes(2, byteorder='little', signed=True) for sample in audio_data])
        wav_file.writeframes(audio_bytes)

def create_mood_audio_files():
    """Create audio files for each mood category"""
    audio_dir = "static/audio"
    os.makedirs(audio_dir, exist_ok=True)
    
    # Musical notes (frequencies in Hz)
    C4, D4, E4, F4, G4, A4, B4 = 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88
    C5, D5, E5, F5 = 523.25, 587.33, 659.25, 698.46
    
    print("🎵 Creating mood-based audio files...")
    
    # Happy melodies - Major scale, upbeat
    happy1 = create_melody([C4, E4, G4, C5, G4, E4, C4], 0.4)
    happy2 = create_melody([G4, A4, B4, C5, B4, A4, G4], 0.4)
    
    # Calm melodies - Soft, slower tempo  
    calm1 = create_melody([C4, F4, A4, C5, A4, F4], 0.8)
    calm2 = create_melody([F4, A4, C5, E5, C5, A4], 0.8)
    
    # Sad melodies - Minor intervals, slower
    sad1 = create_melody([A4, F4, D4, A4, F4, D4], 0.7)
    sad2 = create_melody([D4, F4, A4, D5, A4, F4], 0.7)
    
    # Energetic melodies - Fast, rhythmic
    energetic1 = create_melody([G4, G4, D5, D5, E5, D5, B4], 0.3)
    energetic2 = create_melody([C5, G4, C5, G4, D5, C5, G4], 0.3)
    
    # Save all audio files
    audio_files = {
        'happy1.wav': happy1,
        'happy2.wav': happy2,
        'calm1.wav': calm1,
        'calm2.wav': calm2,  
        'sad1.wav': sad1,
        'sad2.wav': sad2,
        'energetic1.wav': energetic1,
        'energetic2.wav': energetic2
    }
    
    for filename, audio_data in audio_files.items():
        filepath = os.path.join(audio_dir, filename)
        save_wav_file(audio_data, filepath)
        print(f"✅ Created: {filepath}")
        
        # Get file size for verification
        size = os.path.getsize(filepath)
        print(f"   Size: {size:,} bytes ({size/1024:.1f} KB)")
    
    print(f"\n🎶 Successfully created {len(audio_files)} audio files!")
    print("These are synthesized melodies that match each mood category.")

if __name__ == "__main__":
    create_mood_audio_files()
