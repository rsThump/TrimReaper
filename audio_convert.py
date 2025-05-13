# audio_convert.py
import os
import wave
import subprocess
import tempfile

def convert_audio_file(input_file, output_file, sample_rate=44100, bit_depth=16):
    """Convert WAV file to specified sample rate and bit depth using ffmpeg."""
    try:
        # FFmpeg command to convert sample rate and bit depth
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-ar', str(sample_rate),  # sample rate
            '-sample_fmt', f's{bit_depth}',  # bit depth
            '-y',  # overwrite output file
            output_file
        ]
        
        # Run FFmpeg
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if process.returncode != 0:
            print(f"Error converting {input_file}: {process.stderr.decode()}")
            return False
        
        print(f"Converted file: {output_file} to {sample_rate}Hz, {bit_depth}-bit")
        return True
    
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return False

def convert_directory(directory, sample_rate=44100, bit_depth=16):
    """Convert all WAV files in the directory."""
    files = [f for f in os.listdir(directory) if f.endswith('.wav')]
    
    if not files:
        print(f"No WAV files found in {directory}")
        return False
    
    success_count = 0
    for file in files:
        input_path = os.path.join(directory, file)
        output_path = os.path.join(directory, f"{os.path.splitext(file)[0]}_converted.wav")
        
        print(f"Converting file: {file}")
        if convert_audio_file(input_path, output_path, sample_rate, bit_depth):
            success_count += 1
    
    print(f"Converted {success_count} out of {len(files)} files successfully.")
    return success_count > 0
