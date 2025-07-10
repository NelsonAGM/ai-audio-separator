#!/usr/bin/env python3
import sys
import os
import logging
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
        # Initialize Spleeter with 4stems model (vocals, drums, bass, other)
        separator = Separator('spleeter:4stems-wq-16kHz')
        
        logger.info(f"Loading audio file: {input_path}")
        
        # Load audio file
        waveform, sample_rate = librosa.load(input_path, sr=16000, mono=False)
        
        # Ensure stereo
        if len(waveform.shape) == 1:
            waveform = waveform.reshape(1, -1)
        if waveform.shape[0] == 1:
            waveform = np.repeat(waveform, 2, axis=0)
        
        # Spleeter expects (samples, channels) format
        waveform = waveform.T
        
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
                
                # Save as WAV file
                sf.write(output_path, track_data, sample_rate)
                logger.info(f"Saved {track_name} track to {output_path}")
        
        logger.info("All tracks saved successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during separation: {str(e)}")
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
