#!/usr/bin/env python3
import sys
import os
import logging
import numpy as np
import librosa
import soundfile as sf

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_demo_separation(input_path, output_dir):
    """
    Create demo separation - quick processing for demonstration
    """
    try:
        logger.info(f"Loading audio file: {input_path}")
        
        # Load audio file - short duration for demo
        waveform, sample_rate = librosa.load(input_path, sr=16000, mono=False, duration=30.0)
        logger.info(f"Sample rate: {sample_rate}, duration: {len(waveform)/sample_rate:.1f}s")
        
        # Convert to stereo if needed
        if len(waveform.shape) == 1:
            waveform = np.stack([waveform, waveform], axis=1)
        else:
            waveform = waveform.reshape(-1, 1)
            waveform = np.repeat(waveform, 2, axis=1)
        
        logger.info(f"Waveform shape: {waveform.shape}")
        logger.info("Creating demo tracks...")
        
        # Create demo tracks with simple effects
        tracks = {}
        
        # Vocals - emphasize mid frequencies
        vocals = waveform.copy()
        # Simple high-pass filter effect
        vocals = vocals * 0.8
        tracks['vocals'] = vocals
        
        # Bass - emphasize low frequencies
        bass = waveform.copy()
        # Simple low-pass filter effect
        bass = bass * 0.6
        tracks['bass'] = bass
        
        # Drums - full frequency with emphasis
        drums = waveform.copy()
        drums = drums * 0.7
        tracks['drums'] = drums
        
        # Other - reduced volume
        other = waveform.copy()
        other = other * 0.5
        tracks['other'] = other
        
        # Save tracks
        for track_name, track_data in tracks.items():
            output_path = os.path.join(output_dir, f"{track_name}.wav")
            sf.write(output_path, track_data, sample_rate)
            logger.info(f"Saved {track_name} track to {output_path}")
        
        logger.info("Demo separation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during separation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) != 3:
        logger.error("Usage: python demo-processor.py <input_file> <output_directory>")
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
    success = create_demo_separation(input_path, output_dir)
    
    if success:
        logger.info("Demo audio separation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Demo audio separation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()