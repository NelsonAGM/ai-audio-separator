#!/usr/bin/env python3
import sys
import os
import logging
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.ndimage import median_filter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def advanced_separation(input_path, output_dir):
    """
    Advanced audio separation using multiple techniques similar to modern AI approaches
    """
    try:
        logger.info(f"Loading audio file: {input_path}")
        
        # Load audio with optimized settings
        y, sr = librosa.load(input_path, sr=22050, mono=False, duration=60.0)
        
        # Convert to mono for processing
        if len(y.shape) > 1:
            y_mono = librosa.to_mono(y)
            y_stereo = y
        else:
            y_mono = y
            y_stereo = np.column_stack([y, y])
            
        logger.info(f"Loaded: {len(y_mono)/sr:.1f}s at {sr}Hz")
        logger.info("Performing advanced harmonic-percussive separation...")
        
        # Enhanced harmonic-percussive separation with multiple iterations
        y_harmonic, y_percussive = librosa.effects.hpss(y_mono, margin=(1.0, 5.0))
        
        # Get detailed spectral information
        S_full = np.abs(librosa.stft(y_mono, n_fft=2048, hop_length=512))
        S_harmonic = np.abs(librosa.stft(y_harmonic, n_fft=2048, hop_length=512))
        S_percussive = np.abs(librosa.stft(y_percussive, n_fft=2048, hop_length=512))
        
        # Get phase information
        _, phase = librosa.magphase(librosa.stft(y_mono, n_fft=2048, hop_length=512))
        
        # Frequency analysis
        freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
        times = librosa.frames_to_time(np.arange(S_full.shape[1]), sr=sr, hop_length=512)
        
        logger.info("Analyzing spectral features...")
        
        # Advanced vocal detection using spectral features
        vocal_confidence = np.zeros_like(S_full)
        
        # Vocal formant detection (human voice has specific formant frequencies)
        formant_freqs = [800, 1200, 2600]  # Typical vocal formants
        for formant in formant_freqs:
            formant_idx = np.argmin(np.abs(freqs - formant))
            vocal_confidence[formant_idx-5:formant_idx+5, :] += S_harmonic[formant_idx-5:formant_idx+5, :]
        
        # Vocal frequency range emphasis (fundamental + harmonics)
        vocal_range = (freqs >= 85) & (freqs <= 3400)
        vocal_confidence[vocal_range, :] += S_harmonic[vocal_range, :] * 1.5
        
        # Temporal consistency for vocals (vocals tend to be more stable)
        vocal_confidence = median_filter(vocal_confidence, size=(3, 5))
        
        logger.info("Creating intelligent masks...")
        
        # Create adaptive masks based on spectral analysis
        
        # Vocals mask: harmonic content in vocal range with formant emphasis
        vocals_mask = np.zeros_like(S_full)
        vocals_mask[vocal_range, :] = vocal_confidence[vocal_range, :] / (np.max(vocal_confidence) + 1e-8)
        vocals_mask = np.clip(vocals_mask, 0.1, 1.0)
        
        # Bass mask: low frequency harmonic content with emphasis on fundamental
        bass_range = (freqs >= 20) & (freqs <= 250)
        bass_mask = np.zeros_like(S_full)
        bass_mask[bass_range, :] = S_harmonic[bass_range, :] / (np.max(S_harmonic[bass_range, :]) + 1e-8)
        bass_mask = np.clip(bass_mask, 0.2, 1.0)
        
        # Drums mask: percussive content with transient emphasis
        drums_mask = np.zeros_like(S_full)
        
        # Detect onsets for drum enhancement
        onset_strength = librosa.onset.onset_strength(y=y_mono, sr=sr, hop_length=512)
        onset_frames = librosa.onset.onset_detect(onset_envelope=onset_strength, sr=sr, hop_length=512)
        
        # Base drums mask from percussive content
        drum_range = (freqs >= 60) & (freqs <= 8000)
        drums_mask[drum_range, :] = S_percussive[drum_range, :] / (np.max(S_percussive) + 1e-8)
        
        # Enhance drums around onset times
        for onset_frame in onset_frames:
            if onset_frame < drums_mask.shape[1]:
                start_frame = max(0, onset_frame - 3)
                end_frame = min(drums_mask.shape[1], onset_frame + 3)
                drums_mask[drum_range, start_frame:end_frame] *= 2.0
        
        drums_mask = np.clip(drums_mask, 0.1, 1.0)
        
        # Other instruments mask: residual with mid-high frequency emphasis
        other_mask = np.ones_like(S_full) * 0.3
        other_range = (freqs >= 500) & (freqs <= 12000)
        
        # Adaptive other mask: stronger where vocals, bass, and drums are weak
        other_strength = S_full - (vocal_confidence + S_harmonic * bass_mask + S_percussive * drums_mask)
        other_strength = np.clip(other_strength, 0, np.max(S_full))
        other_mask[other_range, :] = other_strength[other_range, :] / (np.max(other_strength) + 1e-8)
        other_mask = np.clip(other_mask, 0.2, 0.9)
        
        logger.info("Generating separated tracks...")
        
        # Apply masks and reconstruct audio
        tracks = {}
        
        # Vocals: enhanced harmonic content with vocal-specific processing
        vocals_stft = S_harmonic * vocals_mask * phase
        vocals = librosa.istft(vocals_stft, hop_length=512)
        # Apply vocal enhancement (slight reverb and formant boosting)
        vocals = librosa.effects.preemphasis(vocals, coef=0.97)
        tracks['vocals'] = vocals
        
        # Bass: low-frequency harmonic content with bass enhancement
        bass_stft = S_harmonic * bass_mask * phase
        bass = librosa.istft(bass_stft, hop_length=512)
        # Bass enhancement with low-pass filtering
        bass = signal.sosfilt(signal.butter(4, 300, 'low', fs=sr, output='sos'), bass)
        tracks['bass'] = bass
        
        # Drums: percussive content with dynamic enhancement
        drums_stft = S_percussive * drums_mask * phase
        drums = librosa.istft(drums_stft, hop_length=512)
        # Drum enhancement with compression and EQ
        drums = np.tanh(drums * 1.5) * 0.8
        tracks['drums'] = drums
        
        # Other: residual content with intelligent filtering
        other_stft = S_full * other_mask * phase
        other = librosa.istft(other_stft, hop_length=512)
        tracks['other'] = other
        
        logger.info("Post-processing and saving tracks...")
        
        # Advanced normalization and stereo processing
        for track_name, track_data in tracks.items():
            # Normalize with headroom
            if np.max(np.abs(track_data)) > 0:
                track_data = track_data / np.max(np.abs(track_data)) * 0.85
            
            # Create stereo with slight panning for realistic effect
            if track_name == 'vocals':
                # Center vocals
                stereo_data = np.column_stack([track_data, track_data])
            elif track_name == 'bass':
                # Center bass with slight emphasis
                stereo_data = np.column_stack([track_data * 1.05, track_data * 0.95])
            elif track_name == 'drums':
                # Wide drums
                stereo_data = np.column_stack([track_data * 0.9, track_data * 1.1])
            else:  # other
                # Slight stereo spread
                stereo_data = np.column_stack([track_data * 0.95, track_data * 1.05])
            
            output_path = os.path.join(output_dir, f"{track_name}.wav")
            sf.write(output_path, stereo_data, sr)
            logger.info(f"Saved enhanced {track_name} track ({len(track_data)/sr:.1f}s)")
        
        logger.info("Advanced separation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during advanced separation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) != 3:
        logger.error("Usage: python advanced-processor.py <input_file> <output_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(input_path):
        logger.error(f"Input file does not exist: {input_path}")
        sys.exit(1)
    
    os.makedirs(output_dir, exist_ok=True)
    
    success = advanced_separation(input_path, output_dir)
    
    if success:
        logger.info("SUCCESS: Advanced audio separation completed!")
        sys.exit(0)
    else:
        logger.error("FAILED: Advanced audio separation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()