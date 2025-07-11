#!/usr/bin/env python3
import sys
import os
import logging
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import butter, filtfilt

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_simple_separation(input_path, output_dir):
    """
    Create simple mock separation for testing - splits audio into frequency bands
    """
    try:
        logger.info(f"Loading audio file: {input_path}")
        
        # Load audio - limit to 30 seconds and lower sample rate for speed
        y, sr = librosa.load(input_path, sr=8000, mono=True, duration=30.0)
        logger.info(f"Loaded: {len(y)/sr:.1f}s at {sr}Hz")
        
        # Apply different filtering to create distinct tracks
        def lowpass_filter(data, cutoff, fs, order=4):
            nyquist = 0.5 * fs
            normal_cutoff = cutoff / nyquist
            b, a = butter(order, normal_cutoff, btype='low', analog=False)
            return filtfilt(b, a, data)
        
        def highpass_filter(data, cutoff, fs, order=4):
            nyquist = 0.5 * fs  
            normal_cutoff = cutoff / nyquist
            b, a = butter(order, normal_cutoff, btype='high', analog=False)
            return filtfilt(b, a, data)
        
        def bandpass_filter(data, low_cutoff, high_cutoff, fs, order=4):
            nyquist = 0.5 * fs
            low = low_cutoff / nyquist
            high = high_cutoff / nyquist
            b, a = butter(order, [low, high], btype='band', analog=False)
            return filtfilt(b, a, data)
        
        logger.info("Creating filtered tracks...")
        
        # Create different versions of the audio
        tracks = {}
        
        # Vocals: mid-frequency band + some reverb
        vocals = bandpass_filter(y, 150, 3000, sr)
        vocals = vocals * 0.8  # Slightly quieter
        tracks['vocals'] = vocals
        
        # Bass: low frequencies only
        bass = lowpass_filter(y, 200, sr)
        bass = bass * 1.2  # Boost bass
        tracks['bass'] = bass
        
        # Drums: emphasize percussive elements
        drums = highpass_filter(y, 60, sr)
        drums = bandpass_filter(drums, 60, 3500, sr)  # Stay within Nyquist limit
        # Add some compression effect
        drums = np.tanh(drums * 2) * 0.7
        tracks['drums'] = drums
        
        # Other: mid-high frequencies
        other = bandpass_filter(y, 800, 3500, sr)  # Stay within Nyquist limit
        other = other * 0.6
        tracks['other'] = other
        
        logger.info("Saving tracks...")
        
        # Save tracks
        for track_name, track_data in tracks.items():
            # Normalize
            if np.max(np.abs(track_data)) > 0:
                track_data = track_data / np.max(np.abs(track_data)) * 0.8
            
            # Convert to stereo
            stereo_data = np.column_stack([track_data, track_data])
            
            output_path = os.path.join(output_dir, f"{track_name}.wav")
            sf.write(output_path, stereo_data, sr)
            logger.info(f"Saved {track_name} track to {output_path}")
        
        logger.info("Simple separation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during separation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) != 3:
        logger.error("Usage: python simple-processor.py <input_file> <output_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Validate input file exists
    if not os.path.exists(input_path):
        logger.error(f"Input file does not exist: {input_path}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Perform separation
    success = create_simple_separation(input_path, output_dir)
    
    if success:
        logger.info("Simple audio separation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Simple audio separation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()