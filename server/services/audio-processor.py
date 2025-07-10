#!/usr/bin/env python3
import sys
import os
import logging
import numpy as np
from spleeter.separator import Separator
import librosa
import soundfile as sf

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def separate_audio(input_path, output_dir):
    """
    Separate audio using Spleeter into 4 stems: vocals, drums, bass, other
    """
    try:
        logger.info(f"Loading audio file: {input_path}")
        
        # Load audio file with optimized settings for long files
        waveform, sample_rate = librosa.load(input_path, sr=22050, mono=False)
        logger.info(f"Sample rate: {sample_rate}")
        
        # Limit audio length to 5 minutes for processing (300 seconds)
        max_length = 300 * sample_rate
        if waveform.shape[-1] > max_length:
            logger.info(f"Trimming audio from {waveform.shape[-1]/sample_rate:.1f}s to {max_length/sample_rate:.1f}s")
            waveform = waveform[..., :max_length]
        
        # Convert to stereo if needed
        if len(waveform.shape) == 1:
            # Mono to stereo
            waveform = np.stack([waveform, waveform])
        elif waveform.shape[0] == 1:
            # Single channel to stereo
            waveform = np.repeat(waveform, 2, axis=0)
        
        # Transpose to (samples, channels) format for Spleeter
        waveform = waveform.T
        
        logger.info(f"Waveform shape: {waveform.shape}")
        logger.info("Initializing Spleeter separator...")
        
        # Initialize Spleeter with 4stems model - use faster model for quicker processing
        separator = Separator('spleeter:4stems-wq-16kHz')
        
        logger.info("Starting separation...")
        
        # Perform separation
        prediction = separator.separate(waveform)
        
        logger.info("Separation complete. Saving tracks...")
        
        # Save each track
        track_names = ['vocals', 'drums', 'bass', 'other']
        
        for track_name in track_names:
            if track_name in prediction:
                track_data = prediction[track_name]
                output_path = os.path.join(output_dir, f"{track_name}.wav")
                
                # Save as WAV file with original sample rate
                sf.write(output_path, track_data, sample_rate)
                logger.info(f"Saved {track_name} track to {output_path}")
        
        logger.info("All tracks saved successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during separation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) != 3:
        logger.error("Usage: python audio-processor.py <input_file> <output_directory>")
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
    success = separate_audio(input_path, output_dir)
    
    if success:
        logger.info("Audio separation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Audio separation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
