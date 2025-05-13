# audio_trim.py
import os
import wave
import array
import math
import soundfile as sf

def calculate_db_level(sample, zero, max_val):
    """Calculate dB level of a sample relative to maximum possible value."""
    # Avoid division by zero or log of zero
    normalized = abs(sample - zero) / max_val
    if normalized <= 0:
        return -float('inf')  # Return negative infinity for silence
    else:
        return 20 * math.log10(normalized)

def find_zero_crossing(samples, position, direction='forward', window=1000):
    """Find the nearest zero crossing point from the given position."""
    zero_val = 0  # For most formats, zero point is at 0
    
    # Search forward
    if direction == 'forward':
        max_pos = min(position + window, len(samples) - 1)  # Avoid going out of bounds
        for i in range(position, max_pos - 1):
            # Check if we cross the zero line between current and next sample
            if ((samples[i] >= zero_val and samples[i+1] < zero_val) or 
                (samples[i] <= zero_val and samples[i+1] > zero_val)):
                return i
    # Search backward
    else:  # direction == 'backward'
        min_pos = max(0, position - window)
        for i in range(position, min_pos, -1):
            if i > 0:  # Avoid index out of range
                # Check if we cross the zero line between current and previous sample
                if ((samples[i] >= zero_val and samples[i-1] < zero_val) or 
                    (samples[i] <= zero_val and samples[i-1] > zero_val)):
                    return i
    
    # If no zero crossing found, return original position
    return position

def find_end_point(samples, zero, max_val, threshold_db=-60, window_size=1024, min_duration_sec=0.5, framerate=44100):
    """
    Find the point where audio falls below threshold_db and stays there.
    Uses a sliding window to avoid cutting off at brief quiet moments.
    """
    min_samples = int(min_duration_sec * framerate)
    
    # Start from the end and move backward
    for i in range(len(samples) - window_size, 0, -1):
        # Check if window is consistently below threshold
        window_max_db = max(calculate_db_level(samples[j], zero, max_val) for j in range(i, min(i + window_size, len(samples))))
        
        if window_max_db > threshold_db:
            # Found the end of significant audio
            # Add a small tail to avoid abrupt cutoffs
            end_point = min(i + window_size + min_samples, len(samples))
            
            # Find the nearest zero crossing point
            end_point = find_zero_crossing(samples, end_point, direction='backward')
            
            return end_point
    
    # If we got here, all audio is below threshold
    return len(samples)

def get_audio_format(file_path):
    """Determine the audio format of a file."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.wav':
        return 'wav'
    elif ext == '.flac':
        return 'flac'
    elif ext in ['.aiff', '.aif']:
        return 'aiff'
    else:
        raise ValueError(f"Unsupported audio format: {ext}")

def trim_audio_file(input_file, output_file, threshold_db=-60, min_duration_sec=0.5):
    """Trim audio file by removing silence at the end below specified threshold."""
    try:
        # Determine file format based on extension
        input_format = get_audio_format(input_file)
        output_format = get_audio_format(output_file)
        
        if input_format in ['flac', 'aiff', 'aif']:
            # Use soundfile for FLAC and AIFF
            data, samplerate = sf.read(input_file)
            n_channels = 1 if len(data.shape) == 1 else data.shape[1]
            
            # Process differently based on number of channels
            if n_channels > 1:
                # Multi-channel audio
                channel_end_points = []
                
                # Find end point for each channel
                for channel in range(n_channels):
                    channel_data = data[:, channel]
                    max_val = max(abs(sample) for sample in channel_data) or 1.0
                    end_point = find_end_point(channel_data, 0, max_val, threshold_db, 
                                               min_duration_sec=min_duration_sec, framerate=samplerate)
                    channel_end_points.append(end_point)
                
                # Use the latest end point
                end_point = max(channel_end_points)
                
                # Find nearest zero crossing in the first channel
                end_point = find_zero_crossing(data[:, 0], end_point, direction='backward')
                
                # Trim all channels to the same length
                trimmed_data = data[:end_point, :]
            else:
                # Mono audio
                max_val = max(abs(sample) for sample in data) or 1.0
                end_point = find_end_point(data, 0, max_val, threshold_db, 
                                          min_duration_sec=min_duration_sec, framerate=samplerate)
                
                # Find nearest zero crossing
                end_point = find_zero_crossing(data, end_point, direction='backward')
                
                trimmed_data = data[:end_point]
            
            # Calculate reduction percentage
            original_length = len(data)
            trimmed_length = len(trimmed_data)
            reduction = ((original_length - trimmed_length) / original_length) * 100 if original_length > 0 else 0
            
            # Write output file
            sf.write(output_file, trimmed_data, samplerate, format=output_format)
            
            print(f"Trimmed file: {output_file} (removed {reduction:.1f}% - {original_length-trimmed_length} samples)")
            return True
        
        # Handle WAV files with the existing wave module approach
        with wave.open(input_file, 'rb') as wav_file:
            # Get audio parameters
            n_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            
            # Read all audio data
            wav_file.rewind()
            audio_data = wav_file.readframes(n_frames)
            
            # Convert to array for processing
            if sample_width == 1:
                fmt = 'B'  # unsigned char
                # For 8-bit audio, the values are unsigned (0-255)
                # with 128 being the zero crossing point
                zero = 128
                max_val = 255
            elif sample_width == 2:
                fmt = 'h'  # signed short
                # For 16-bit audio, the values are signed (-32768 to 32767)
                zero = 0
                max_val = 32767
            elif sample_width == 3:
                # Handle 24-bit audio by converting to 32-bit
                print("Converting 24-bit audio to 32-bit for processing...")
                # Convert 3-byte samples to 4-byte (pad with 0)
                unpacked_data = bytearray()
                for i in range(0, len(audio_data), 3):
                    if i + 2 < len(audio_data):
                        # Extract 3 bytes and convert to 4 bytes (little endian)
                        b1, b2, b3 = audio_data[i], audio_data[i+1], audio_data[i+2]
                        # Sign extend if highest bit is set
                        b4 = 255 if (b3 & 128) else 0
                        unpacked_data.extend([b1, b2, b3, b4])
                
                fmt = 'i'  # signed int
                zero = 0
                max_val = 8388607  # 2^23 - 1 (24-bit max value)
                
                # Convert bytes to array
                samples = array.array(fmt)
                samples.frombytes(bytes(unpacked_data))
                
                # Continue with regular processing, but remember we're handling 24-bit
                original_sample_width = 3  # Keep track of original width
            elif sample_width == 4:
                fmt = 'i'  # signed int
                zero = 0
                max_val = 2147483647
            else:
                print(f"Unsupported sample width: {sample_width}")
                return False
            
            # Convert bytes to array if not already converted (for 24-bit case)
            if sample_width != 3:
                samples = array.array(fmt)
                samples.frombytes(audio_data)
                original_sample_width = sample_width
            
            # Process each channel separately for multichannel audio
            if n_channels > 1:
                # Split samples by channel
                channel_samples = [[] for _ in range(n_channels)]
                for i, sample in enumerate(samples):
                    channel_samples[i % n_channels].append(sample)
                
                # Find end point for each channel
                channel_end_points = []
                for channel in channel_samples:
                    channel_array = array.array(fmt, channel)
                    end_point = find_end_point(channel_array, zero, max_val, threshold_db, 
                                               min_duration_sec=min_duration_sec, framerate=framerate)
                    channel_end_points.append(end_point)
                
                # Use the latest end point to avoid cutting any channel too early
                end_point = max(channel_end_points)
                
                # Find the nearest zero crossing in the first channel
                if len(channel_samples[0]) > 0:
                    channel_zero_crossing = find_zero_crossing(
                        channel_samples[0], 
                        min(end_point, len(channel_samples[0]) - 1), 
                        direction='backward'
                    )
                    # Adjust the end point to match the zero crossing
                    end_point = channel_zero_crossing
                
                # Recombine samples with trimming
                trimmed_samples = array.array(fmt)
                for channel_idx in range(n_channels):
                    channel = channel_samples[channel_idx]
                    for i in range(min(end_point, len(channel))):
                        trimmed_samples.append(channel[i])
                
            else:
                # Single channel - find end point directly
                end_point = find_end_point(samples, zero, max_val, threshold_db, 
                                          min_duration_sec=min_duration_sec, framerate=framerate)
                
                # Find nearest zero crossing
                end_point = find_zero_crossing(samples, end_point, direction='backward')
                
                trimmed_samples = array.array(fmt, samples[:end_point])
            
            # Prepare output data
            if original_sample_width == 3:
                # Convert back to 24-bit
                packed_data = bytearray()
                for s in trimmed_samples:
                    # Handle negative values properly
                    s_unsigned = s & 0xFFFFFFFF
                    # Take only the 3 lower bytes
                    packed_data.append(s_unsigned & 0xFF)
                    packed_data.append((s_unsigned >> 8) & 0xFF)
                    packed_data.append((s_unsigned >> 16) & 0xFF)
                output_data = bytes(packed_data)
            else:
                output_data = trimmed_samples.tobytes()
            
            # Calculate reduction percentage
            original_length = n_frames
            trimmed_length = len(trimmed_samples) // n_channels
            reduction = ((original_length - trimmed_length) / original_length) * 100 if original_length > 0 else 0
            
            # Write trimmed data to output file
            with wave.open(output_file, 'wb') as output:
                output.setnchannels(n_channels)
                output.setsampwidth(original_sample_width)
                output.setframerate(framerate)
                output.writeframes(output_data)
            
            print(f"Trimmed file: {output_file} (removed {reduction:.1f}% - {original_length-trimmed_length} samples)")
            return True
            
    except Exception as e:
        print(f"Error trimming {input_file}: {str(e)}")
        return False

def trim_directory(directory, output_dir=None, threshold_db=-60, min_duration_sec=0.5):
    """Trim all audio files in the directory."""
    if not output_dir:
        output_dir = directory
        
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all supported audio files
    files = [f for f in os.listdir(directory) 
            if f.lower().endswith(('.wav', '.flac', '.aiff', '.aif'))]
    
    if not files:
        print(f"No supported audio files found in {directory}")
        return False
    
    success_count = 0
    for file in files:
        input_path = os.path.join(directory, file)
        base_name, ext = os.path.splitext(file)
        output_path = os.path.join(output_dir, f"{base_name}_trimmed{ext}")
        
        print(f"Trimming file: {file}")
        if trim_audio_file(input_path, output_path, threshold_db, min_duration_sec):
            success_count += 1
    
    print(f"Trimmed {success_count} out of {len(files)} files successfully.")
    return success_count > 0
