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

def create_simple_separation(input_path, output_dir):
    """
    Create simple mock separation for testing - splits audio into frequency bands
    """
    try:
        logger.info(f"Loading audio file: {input_path}")
        
        # Load audio file with reduced quality for faster processing
        waveform, sample_rate = librosa.load(input_path, sr=16000, mono=False)
        logger.info(f"Sample rate: {sample_rate}")
        
        # Limit to 2 minutes for testing
        max_length = 120 * sample_rate
        if waveform.shape[-1] > max_length:
            logger.info(f"Trimming audio from {waveform.shape[-1]/sample_rate:.1f}s to {max_length/sample_rate:.1f}s")
            waveform = waveform[..., :max_length]
        
        # Convert to stereo if needed
        if len(waveform.shape) == 1:
            waveform = np.stack([waveform, waveform])
        elif waveform.shape[0] == 1:
            waveform = np.repeat(waveform, 2, axis=0)
        
        # Transpose to (samples, channels) format
        waveform = waveform.T
        
        logger.info(f"Waveform shape: {waveform.shape}")
        logger.info("Creating frequency-based separation...")
        
        # Simple frequency-based separation
        # Convert to frequency domain
        n_fft = 2048
        hop_length = 512
        
        # Get STFT
        stft = librosa.stft(waveform[:, 0], n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Create frequency masks for different "instruments"
        freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
        
        # Vocals (mid frequencies 300-3000 Hz)
        vocals_mask = np.logical_and(freqs >= 300, freqs <= 3000)
        vocals_stft = stft.copy()
        vocals_stft[~vocals_mask] *= 0.1  # Reduce other frequencies
        
        # Bass (low frequencies 20-250 Hz) 
        bass_mask = np.logical_and(freqs >= 20, freqs <= 250)
        bass_stft = stft.copy()
        bass_stft[~bass_mask] *= 0.1
        
        # Drums (wide range with emphasis on percussive frequencies)
        drums_stft = stft.copy()
        drums_stft[freqs < 60] *= 0.3  # Reduce very low
        drums_stft[freqs > 8000] *= 0.5  # Reduce very high
        
        # Other (everything else)
        other_stft = stft.copy()
        other_stft[vocals_mask] *= 0.3
        other_stft[bass_mask] *= 0.3
        
        logger.info("Converting back to time domain...")
        
        # Convert back to time domain
        tracks = {
            'vocals': librosa.istft(vocals_stft, hop_length=hop_length),
            'bass': librosa.istft(bass_stft, hop_length=hop_length),
            'drums': librosa.istft(drums_stft, hop_length=hop_length),
            'other': librosa.istft(other_stft, hop_length=hop_length)
        }
        
        # Convert to stereo for all tracks
        for track_name, track_data in tracks.items():
            if len(track_data.shape) == 1:
                track_data = np.stack([track_data, track_data], axis=1)
            else:
                track_data = track_data.reshape(-1, 1)
                track_data = np.repeat(track_data, 2, axis=1)
            
            output_path = os.path.join(output_dir, f"{track_name}.wav")
            sf.write(output_path, track_data, sample_rate)
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
        logger.info("Audio separation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Audio separation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()