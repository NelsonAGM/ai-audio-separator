#!/usr/bin/env python3
import sys
import os
import logging
import time
import psutil
import librosa
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_audio_file(input_path):
    """
    Analyze audio file to determine best processing approach
    """
    try:
        # Get file info
        file_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        duration = librosa.get_duration(path=input_path)
        
        # Get system resources
        memory_available = psutil.virtual_memory().available / (1024 * 1024 * 1024)  # GB
        cpu_count = psutil.cpu_count()
        
        logger.info(f"Audio analysis: {file_size:.1f}MB, {duration:.1f}s")
        logger.info(f"System: {memory_available:.1f}GB RAM, {cpu_count} CPUs")
        
        return {
            'file_size_mb': file_size,
            'duration_seconds': duration,
            'memory_gb': memory_available,
            'cpu_count': cpu_count
        }
    except Exception as e:
        logger.error(f"Error analyzing audio: {e}")
        return None

def select_processor(audio_info):
    """
    Intelligently select the best processor based on audio and system characteristics
    """
    if not audio_info:
        return 'simple'
    
    file_size = audio_info['file_size_mb']
    duration = audio_info['duration_seconds']
    memory = audio_info['memory_gb']
    
    # Decision matrix
    if memory >= 4.0 and file_size <= 50 and duration <= 300:  # 4GB+ RAM, small file
        logger.info("Selecting Demucs (high quality)")
        return 'demucs'
    elif memory >= 2.0 and file_size <= 100 and duration <= 600:  # 2GB+ RAM, medium file
        logger.info("Selecting Advanced processor")
        return 'advanced'
    elif memory >= 1.0 and file_size <= 200:  # 1GB+ RAM, large file
        logger.info("Selecting Fast processor")
        return 'fast'
    else:
        logger.info("Selecting Simple processor (fallback)")
        return 'simple'

def run_processor(processor_type, input_path, output_dir):
    """
    Run the selected processor
    """
    start_time = time.time()
    
    try:
        if processor_type == 'demucs':
            from demucs_processor import lightweight_demucs
            success = lightweight_demucs(input_path, output_dir)
        elif processor_type == 'advanced':
            from advanced_processor import advanced_separation
            success = advanced_separation(input_path, output_dir)
        elif processor_type == 'fast':
            from fast_processor import fast_separation
            success = fast_separation(input_path, output_dir)
        else:  # simple
            from simple_processor import create_simple_separation
            success = create_simple_separation(input_path, output_dir)
        
        processing_time = time.time() - start_time
        logger.info(f"{processor_type.capitalize()} processor completed in {processing_time:.1f}s")
        
        return success
        
    except ImportError as e:
        logger.error(f"Processor {processor_type} not available: {e}")
        # Fallback to simple processor
        if processor_type != 'simple':
            logger.info("Falling back to simple processor")
            from simple_processor import create_simple_separation
            return create_simple_separation(input_path, output_dir)
        return False
    except Exception as e:
        logger.error(f"Error in {processor_type} processor: {e}")
        return False

def ai_separation(input_path, output_dir):
    """
    Main AI-powered separation function with intelligent processor selection
    """
    try:
        logger.info(f"Starting AI-powered separation: {input_path}")
        
        # Step 1: Analyze audio file and system resources
        audio_info = analyze_audio_file(input_path)
        
        # Step 2: Select best processor
        processor_type = select_processor(audio_info)
        
        # Step 3: Run separation
        success = run_processor(processor_type, input_path, output_dir)
        
        if success:
            logger.info(f"AI separation completed successfully using {processor_type} processor")
            return True
        else:
            logger.error("AI separation failed")
            return False
            
    except Exception as e:
        logger.error(f"Error in AI separation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) != 3:
        logger.error("Usage: python ai-processor.py <input_file> <output_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Validate input file exists
    if not os.path.exists(input_path):
        logger.error(f"Input file does not exist: {input_path}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Perform AI-powered separation
    success = ai_separation(input_path, output_dir)
    
    if success:
        logger.info("SUCCESS: AI-powered audio separation completed!")
        sys.exit(0)
    else:
        logger.error("FAILED: AI-powered audio separation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 