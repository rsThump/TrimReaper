# audio_slice.py
import os
import wave
import math

def slice_audio_file(input_file, output_prefix, bpm=120, bars_per_slice=2):
    """Slice a WAV file into segments of specified number of bars at given BPM."""
    try:
        with wave.open(input_file, 'rb') as wav_file:
            # Get audio parameters
            n_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            
            # Calculate segment length in samples
            # At 120 BPM, one beat is 0.5 seconds
            # One bar has 4 beats, so 2 bars = 8 beats
            seconds_per_beat = 60.0 / bpm
            seconds_per_slice = seconds_per_beat * 4 * bars_per_slice
            samples_per_slice = int(seconds_per_slice * framerate)
            
            # Read all audio data
            wav_file.rewind()
            audio_data = wav_file.readframes(n_frames)
            
            # Calculate number of segments
            n_segments = math.ceil(n_frames / samples_per_slice)
            
            success_count = 0
            output_files = []
            
            for i in range(n_segments):
                # Calculate start and end frame for this segment
                start_frame = i * samples_per_slice
                end_frame = min((i + 1) * samples_per_slice, n_frames)
                
                # Calculate byte positions (depends on channels and sample width)
                bytes_per_frame = n_channels * sample_width
                start_byte = start_frame * bytes_per_frame
                end_byte = end_frame * bytes_per_frame
                
                # Extract segment data
                segment_data = audio_data[start_byte:end_byte]
                
                # Skip empty segments
                if len(segment_data) == 0:
                    continue
                
                # Create output filename
                segment_number = i + 1
                output_file = f"{output_prefix}_{segment_number:02d}.wav"
                
                # Write segment to new file
                with wave.open(output_file, 'wb') as output:
                    output.setnchannels(n_channels)
                    output.setsampwidth(sample_width)
                    output.setframerate(framerate)
                    output.writeframes(segment_data)
                    
                print(f"Created segment: {output_file}")
                output_files.append(output_file)
                success_count += 1
            
            print(f"Successfully created {success_count} segments from {input_file}")
            return output_files
            
    except Exception as e:
        print(f"Error slicing {input_file}: {str(e)}")
        return []

def slice_directory(directory, bpm=120, bars_per_slice=2):
    """Slice all stereo WAV files in the directory."""
    files = [f for f in os.listdir(directory) if f.endswith('_stereo.wav')]
    
    if not files:
        print(f"No stereo WAV files found in {directory}")
        return False
    
    success_count = 0
    for file in files:
        input_path = os.path.join(directory, file)
        output_prefix = os.path.join(directory, file[:-4])  # Remove .wav extension
        
        print(f"Slicing file: {file}")
        if slice_audio_file(input_path, output_prefix, bpm, bars_per_slice):
            success_count += 1
    
    print(f"Sliced {success_count} out of {len(files)} files successfully.")
    return success_count > 0
