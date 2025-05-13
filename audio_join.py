# audio_join.py
import os
import wave

def join_mono_to_stereo(left_file, right_file, output_file):
    """Join two mono WAV files into a single stereo WAV file."""
    try:
        # Open the input files
        with wave.open(left_file, 'rb') as left, wave.open(right_file, 'rb') as right:
            # Check if both files are mono
            if left.getnchannels() != 1 or right.getnchannels() != 1:
                print("Error: Both input files must be mono.")
                return False
            
            # Check if both files have the same parameters
            if (left.getframerate() != right.getframerate() or 
                left.getsampwidth() != right.getsampwidth()):
                print("Error: Input files must have the same sample rate and bit depth.")
                return False

            # Create output file with stereo parameters
            with wave.open(output_file, 'wb') as output:
                output.setnchannels(2)
                output.setsampwidth(left.getsampwidth())
                output.setframerate(left.getframerate())
                
                # Process audio data
                frames_left = left.readframes(left.getnframes())
                frames_right = right.readframes(right.getnframes())
                
                # Ensure equal length (use shorter file's length)
                min_length = min(len(frames_left), len(frames_right))
                frames_left = frames_left[:min_length]
                frames_right = frames_right[:min_length]
                
                # Interleave frames from left and right channels
                merged_frames = bytearray()
                for i in range(0, min_length, left.getsampwidth()):
                    if i + left.getsampwidth() <= min_length:
                        merged_frames.extend(frames_left[i:i+left.getsampwidth()])
                        merged_frames.extend(frames_right[i:i+left.getsampwidth()])
                
                output.writeframes(bytes(merged_frames))
            
            print(f"Successfully created stereo file: {output_file}")
            return True
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def find_channel_pairs(directory):
    """Find matching pairs of _L and _R files in the given directory."""
    files = os.listdir(directory)
    
    # Find all left channel files
    left_files = [f for f in files if f.endswith(' L.wav')]
    pairs = []
    
    for left_file in left_files:
        # Construct expected right file name
        base_name = left_file[:-6]  # Remove ' L.wav'
        right_file = f"{base_name} R.wav"
        
        if right_file in files:
            left_path = os.path.join(directory, left_file)
            right_path = os.path.join(directory, right_file)
            output_file = os.path.join(directory, f"{base_name}_stereo.wav")
            pairs.append((left_path, right_path, output_file))
    
    return pairs

def process_directory(directory):
    """Process all matching _L and _R files in the directory."""
    pairs = find_channel_pairs(directory)
    
    if not pairs:
        print(f"No matching L and R pairs found in {directory}")
        return False
    
    success_count = 0
    for left_file, right_file, output_file in pairs:
        print(f"Processing pair: {os.path.basename(left_file)} + {os.path.basename(right_file)} -> {os.path.basename(output_file)}")
        if join_mono_to_stereo(left_file, right_file, output_file):
            success_count += 1
    
    print(f"Processed {success_count} out of {len(pairs)} file pairs successfully.")
    return success_count > 0
