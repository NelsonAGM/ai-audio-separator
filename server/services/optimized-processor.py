#!/usr/bin/env python3
import sys
import os
import logging
import numpy as np
import librosa
import soundfile as sf

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def optimized_separation(input_path, output_dir):
    """
    Optimized audio separation using librosa and spectral techniques
    """
    try:
        logger.info(f"Loading audio file: {input_path}")
        
        # Load audio file with optimized settings
        y, sr = librosa.load(input_path, sr=22050, mono=False, duration=60.0)  # Limit to 1 minute
        logger.info(f"Sample rate: {sr}, shape: {y.shape}")
        
        # Convert to mono for processing, then duplicate for stereo output
        if len(y.shape) > 1:
            y_mono = librosa.to_mono(y)
        else:
            y_mono = y
            
        logger.info("Performing harmonic-percussive separation...")
        
        # Harmonic-percussive separation
        y_harmonic, y_percussive = librosa.effects.hpss(y_mono, margin=(1.0, 5.0))
        
        logger.info("Performing spectral analysis...")
        
        # Get spectrograms
        S_full, phase = librosa.magphase(librosa.stft(y_mono))
        S_harmonic = np.abs(librosa.stft(y_harmonic))
        S_percussive = np.abs(librosa.stft(y_percussive))
        
        # Create frequency masks
        freqs = librosa.fft_frequencies(sr=sr)
        
        # Vocals mask (human voice frequencies: 80Hz - 1100Hz with peak around 300-3400Hz)
        vocals_mask = np.zeros_like(S_full)
        vocal_indices = np.where((freqs >= 80) & (freqs <= 3400))[0]
        vocals_mask[vocal_indices, :] = 1.0
        
        # Bass mask (low frequencies: 20Hz - 250Hz)
        bass_mask = np.zeros_like(S_full)
        bass_indices = np.where((freqs >= 20) & (freqs <= 250))[0]
        bass_mask[bass_indices, :] = 1.0
        
        # Drums mask (use percussive component + mid-high frequencies)
        drums_mask = np.zeros_like(S_full)
        drum_indices = np.where((freqs >= 60) & (freqs <= 8000))[0]
        drums_mask[drum_indices, :] = 1.0
        
        logger.info("Creating separated tracks...")
        
        # Apply masks and create tracks
        tracks = {}
        
        # Vocals: harmonic content in vocal frequency range
        vocals_stft = S_harmonic * vocals_mask * phase
        vocals = librosa.istft(vocals_stft)
        # Enhance vocals by reducing bass frequencies
        vocals_filtered = librosa.effects.preemphasis(vocals)
        tracks['vocals'] = vocals_filtered
        
        # Bass: low frequency harmonic content
        bass_stft = S_harmonic * bass_mask * phase
        bass = librosa.istft(bass_stft)
        # Enhance bass with low-pass filtering
        bass_enhanced = librosa.effects.preemphasis(bass, coef=-0.97)  # Negative for bass boost
        tracks['bass'] = bass_enhanced
        
        # Drums: percussive content
        drums_stft = S_percussive * drums_mask * phase
        drums = librosa.istft(drums_stft)
        # Enhance drums with dynamic range compression
        tracks['drums'] = drums
        
        # Other: residual (original - vocals - bass - drums)
        other = y_mono - (vocals_filtered + bass_enhanced + drums) * 0.3
        tracks['other'] = other
        
        logger.info("Saving tracks...")
        
        # Normalize and save tracks
        for track_name, track_data in tracks.items():
            # Normalize audio
            if np.max(np.abs(track_data)) > 0:
                track_data = track_data / np.max(np.abs(track_data)) * 0.8
            
            # Convert to stereo
            if len(track_data.shape) == 1:
                stereo_data = np.column_stack([track_data, track_data])
            else:
                stereo_data = track_data
            
            output_path = os.path.join(output_dir, f"{track_name}.wav")
            sf.write(output_path, stereo_data, sr)
            logger.info(f"Saved {track_name} track to {output_path}")
        
        logger.info("Optimized separation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during separation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) != 3:
        logger.error("Usage: python optimized-processor.py <input_file> <output_directory>")
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
    success = optimized_separation(input_path, output_dir)
    
    if success:
        logger.info("Optimized audio separation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Optimized audio separation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()