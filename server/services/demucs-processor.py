#!/usr/bin/env python3
import sys
import os
import logging
import tempfile
import shutil
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demucs_separation(input_path, output_dir):
    """
    Use Demucs for high-quality audio separation
    """
    try:
        import torch
        import demucs.api
        
        logger.info(f"Loading audio file: {input_path}")
        
        # Load the model (htdemucs is the best quality model)
        separator = demucs.api.Separator(model="htdemucs", device="cpu")
        logger.info("Demucs model loaded successfully")
        
        # Separate the audio
        logger.info("Starting audio separation with Demucs...")
        origin, res = separator.separate_audio_file(input_path)
        
        logger.info("Separation completed, saving tracks...")
        
        # Save the separated tracks
        track_names = ['drums', 'bass', 'other', 'vocals']
        
        for i, track_name in enumerate(track_names):
            if i < len(res):
                track_data = res[i]
                output_path = os.path.join(output_dir, f"{track_name}.wav")
                
                # Save using torchaudio
                import torchaudio
                torchaudio.save(output_path, track_data, separator.samplerate)
                logger.info(f"Saved {track_name} track to {output_path}")
        
        logger.info("Demucs separation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error with Demucs separation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def lightweight_demucs(input_path, output_dir):
    """
    Use lightweight Demucs model for faster processing
    """
    try:
        import subprocess
        import tempfile
        
        logger.info(f"Processing with lightweight Demucs: {input_path}")
        
        # Use command line interface with lightweight model
        cmd = [
            "python", "-m", "demucs.separate",
            "--model", "mdx_extra_q",  # Faster model
            "--device", "cpu",
            "--mp3",  # Use MP3 for speed
            "--mp3-bitrate", "192",
            "-o", output_dir,
            input_path
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            logger.info("Demucs processing completed successfully")
            
            # Find the output directory (Demucs creates subdirectories)
            base_name = Path(input_path).stem
            demucs_output = Path(output_dir) / "mdx_extra_q" / base_name
            
            if demucs_output.exists():
                # Move files to the expected location
                for track_file in demucs_output.glob("*.mp3"):
                    track_name = track_file.stem
                    dest_path = Path(output_dir) / f"{track_name}.wav"
                    
                    # Convert MP3 to WAV
                    import librosa
                    import soundfile as sf
                    y, sr = librosa.load(str(track_file))
                    sf.write(str(dest_path), y, sr)
                    logger.info(f"Converted and saved {track_name}")
                
                # Clean up Demucs output directory
                shutil.rmtree(Path(output_dir) / "mdx_extra_q", ignore_errors=True)
                return True
            else:
                logger.error(f"Expected output directory not found: {demucs_output}")
                return False
        else:
            logger.error(f"Demucs failed with error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Demucs processing timed out after 120 seconds")
        return False
    except Exception as e:
        logger.error(f"Error with lightweight Demucs: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) != 3:
        logger.error("Usage: python demucs-processor.py <input_file> <output_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Validate input file exists
    if not os.path.exists(input_path):
        logger.error(f"Input file does not exist: {input_path}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Try lightweight Demucs first
    logger.info("Attempting lightweight Demucs separation...")
    success = lightweight_demucs(input_path, output_dir)
    
    if not success:
        logger.info("Lightweight method failed, trying API method...")
        success = demucs_separation(input_path, output_dir)
    
    if success:
        logger.info("Demucs audio separation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Demucs audio separation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()