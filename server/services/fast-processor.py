#!/usr/bin/env python3
import sys
import os
import logging
import numpy as np
import librosa
import soundfile as sf
from scipy import signal

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fast_separation(input_path, output_dir):
    """
    Fast audio separation using frequency filtering and spectral subtraction
    """
    try:
        logger.info(f"Loading audio file: {input_path}")
        
        # Load audio with reduced duration for speed
        y, sr = librosa.load(input_path, sr=16000, mono=True, duration=45.0)
        logger.info(f"Loaded audio: {len(y)/sr:.1f}s at {sr}Hz")
        
        # Get STFT
        logger.info("Computing spectrogram...")
        D = librosa.stft(y, n_fft=1024, hop_length=256)
        magnitude, phase = np.abs(D), np.angle(D)
        
        # Frequency bins
        freqs = librosa.fft_frequencies(sr=sr, n_fft=1024)
        
        logger.info("Creating frequency masks...")
        
        # Create frequency-based masks
        vocals_mask = np.ones_like(magnitude)
        bass_mask = np.ones_like(magnitude) 
        drums_mask = np.ones_like(magnitude)
        other_mask = np.ones_like(magnitude)
        
        # Vocals: 80Hz - 1000Hz (human voice range)
        vocal_bins = np.where((freqs >= 80) & (freqs <= 1000))[0]
        vocals_mask[:] = 0.1  # Start with low values
        vocals_mask[vocal_bins, :] = 1.0
        
        # Bass: 20Hz - 200Hz 
        bass_bins = np.where((freqs >= 20) & (freqs <= 200))[0]
        bass_mask[:] = 0.1
        bass_mask[bass_bins, :] = 1.0
        
        # Drums: 60Hz - 8000Hz with emphasis on transients
        drum_bins = np.where((freqs >= 60) & (freqs <= 8000))[0]
        drums_mask[:] = 0.2
        drums_mask[drum_bins, :] = 0.8
        
        # Enhance drums with onset detection
        onset_strength = librosa.onset.onset_strength(y=y, sr=sr)
        onset_times = librosa.onset.onset_detect(onset_envelope=onset_strength, sr=sr)
        onset_frames = librosa.time_to_frames(onset_times, sr=sr, hop_length=256)
        
        # Boost drums around onset times
        for frame in onset_frames:
            if frame < drums_mask.shape[1]:
                start = max(0, frame-5)
                end = min(drums_mask.shape[1], frame+5)
                drums_mask[drum_bins, start:end] *= 1.5
        
        # Other: emphasis on mid-high frequencies
        other_bins = np.where((freqs >= 500) & (freqs <= 12000))[0]
        other_mask[:] = 0.3
        other_mask[other_bins, :] = 0.9
        
        logger.info("Generating separated tracks...")
        
        # Apply masks and convert back to time domain
        tracks = {}
        
        # Vocals
        vocals_stft = magnitude * vocals_mask * np.exp(1j * phase)
        vocals = librosa.istft(vocals_stft, hop_length=256)
        tracks['vocals'] = vocals
        
        # Bass
        bass_stft = magnitude * bass_mask * np.exp(1j * phase)
        bass = librosa.istft(bass_stft, hop_length=256)
        tracks['bass'] = bass
        
        # Drums  
        drums_stft = magnitude * drums_mask * np.exp(1j * phase)
        drums = librosa.istft(drums_stft, hop_length=256)
        tracks['drums'] = drums
        
        # Other
        other_stft = magnitude * other_mask * np.exp(1j * phase)
        other = librosa.istft(other_stft, hop_length=256)
        tracks['other'] = other
        
        logger.info("Saving tracks...")
        
        # Normalize and save
        for track_name, track_data in tracks.items():
            # Normalize
            if np.max(np.abs(track_data)) > 0:
                track_data = track_data / np.max(np.abs(track_data)) * 0.7
            
            # Convert to stereo
            stereo_data = np.column_stack([track_data, track_data])
            
            output_path = os.path.join(output_dir, f"{track_name}.wav")
            sf.write(output_path, stereo_data, sr)
            logger.info(f"Saved {track_name}: {len(track_data)/sr:.1f}s")
        
        logger.info("Fast separation completed!")
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) != 3:
        logger.error("Usage: python fast-processor.py <input_file> <output_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(input_path):
        logger.error(f"Input file does not exist: {input_path}")
        sys.exit(1)
    
    os.makedirs(output_dir, exist_ok=True)
    
    success = fast_separation(input_path, output_dir)
    
    if success:
        logger.info("SUCCESS: Fast audio separation completed!")
        sys.exit(0)
    else:
        logger.error("FAILED: Fast audio separation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()