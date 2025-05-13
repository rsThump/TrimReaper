# audio_normalize.py
import os
import wave
import array
import math

def normalize_audio_file(input_file, output_file, target_peak_db=-0.1):
    """Normalize WAV file to target peak level in dB."""
    try:
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
                sample_width = 3  # Keep track of original width
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
            
            # Find the peak value
            peak = max(abs(s - zero) for s in samples)
            
            # Calculate target peak value
            target_peak_linear = 10 ** (target_peak_db / 20.0) * max_val
            
            # Calculate scaling factor
            if peak == 0:
                print("Warning: Audio contains only silence")
                scale_factor = 1.0
            else:
                scale_factor = target_peak_linear / peak
                
            # Apply scaling
            for i in range(len(samples)):
                # Apply gain and ensure we don't exceed the range
                sample_value = (samples[i] - zero) * scale_factor + zero
                samples[i] = max(min(int(sample_value), max_val), -max_val if zero == 0 else 0)
            
            # For 24-bit, convert back from 32-bit to 24-bit
            if sample_width == 3:
                # Convert the 32-bit samples back to 24-bit
                packed_data = bytearray()
                for s in samples:
                    # Handle negative values properly by using the lowest 3 bytes of the integer's two's complement representation
                    # Convert value to unsigned 32-bit int (which Python handles internally)
                    s_unsigned = s & 0xFFFFFFFF
                    # Take only the 3 lower bytes
                    packed_data.append(s_unsigned & 0xFF)
                    packed_data.append((s_unsigned >> 8) & 0xFF)
                    packed_data.append((s_unsigned >> 16) & 0xFF)
                output_data = bytes(packed_data)
            else:
                output_data = samples.tobytes()
            
            # Write normalized data to output file
            with wave.open(output_file, 'wb') as output:
                output.setnchannels(n_channels)
                output.setsampwidth(sample_width)  # Use original sample width
                output.setframerate(framerate)
                output.writeframes(output_data)
            
            print(f"Normalized file: {output_file} to {target_peak_db} dB")
            return True
            
    except Exception as e:
        print(f"Error normalizing {input_file}: {str(e)}")
        return False

def normalize_directory(directory, target_peak_db=-0.1):
    """Normalize all WAV files in the directory."""
    files = [f for f in os.listdir(directory) if f.endswith('.wav')]
    
    if not files:
        print(f"No WAV files found in {directory}")
        return False
    
    success_count = 0
    for file in files:
        input_path = os.path.join(directory, file)
        output_path = os.path.join(directory, f"{os.path.splitext(file)[0]}_normalized.wav")
        
        print(f"Normalizing file: {file}")
        if normalize_audio_file(input_path, output_path, target_peak_db):
            success_count += 1
    
    print(f"Normalized {success_count} out of {len(files)} files successfully.")
    return success_count > 0
