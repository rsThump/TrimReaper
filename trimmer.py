# trimmer.py (main script)
import argparse
import os
import sys

# Import our modules
from audio_join import join_mono_to_stereo, process_directory as join_directory
from audio_slice import slice_audio_file, slice_directory
from audio_normalize import normalize_audio_file, normalize_directory
from audio_convert import convert_audio_file, convert_directory
from audio_ui import launch_gradio_interface

def main():
    parser = argparse.ArgumentParser(description='Audio file processing utility.')
    
    # Add a UI option
    parser.add_argument('--ui', action='store_true', help='Launch the Gradio UI')
    
    # Create subparsers for different functions
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Join parser
    join_parser = subparsers.add_parser('join', help='Join mono files into stereo')
    join_group = join_parser.add_mutually_exclusive_group(required=True)
    join_group.add_argument('-d', '--directory', help='Directory containing L and R mono files')
    join_group.add_argument('-l', '--left', help='Left channel mono audio file (WAV)')
    join_parser.add_argument('-r', '--right', help='Right channel mono audio file (WAV)')
    join_parser.add_argument('-o', '--output', help='Output stereo file (WAV)', 
                        default='output_stereo.wav')
    
    # Slice parser
    slice_parser = subparsers.add_parser('slice', help='Slice audio files into segments')
    slice_parser.add_argument('-f', '--file', help='Stereo audio file to slice')
    slice_parser.add_argument('-d', '--directory', help='Directory containing stereo files to slice')
    slice_parser.add_argument('-b', '--bpm', type=int, default=120, help='Tempo in BPM (default: 120)')
    slice_parser.add_argument('-a', '--bars', type=int, default=2, help='Bars per slice (default: 2)')
    
    # Normalize parser
    norm_parser = subparsers.add_parser('normalize', help='Normalize audio files')
    norm_parser.add_argument('-f', '--file', help='Audio file to normalize')
    norm_parser.add_argument('-d', '--directory', help='Directory containing audio files to normalize')
    norm_parser.add_argument('-p', '--peak', type=float, default=-0.1, help='Target peak level in dB (default: -0.1)')
    norm_parser.add_argument('-o', '--output', help='Output normalized file (WAV)', 
                        default='output_normalized.wav')
    
    # Convert parser
    conv_parser = subparsers.add_parser('convert', help='Convert audio files')
    conv_parser.add_argument('-f', '--file', help='Audio file to convert')
    conv_parser.add_argument('-d', '--directory', help='Directory containing audio files to convert')
    conv_parser.add_argument('-s', '--samplerate', type=int, default=44100, help='Target sample rate (default: 44100)')
    conv_parser.add_argument('-b', '--bitdepth', type=int, default=16, help='Target bit depth (default: 16)')
    conv_parser.add_argument('-o', '--output', help='Output converted file (WAV)', 
                        default='output_converted.wav')
    
    args = parser.parse_args()
    
    # Handle UI option
    if args.ui:
        try:
            launch_gradio_interface()
            return
        except ImportError:
            print("Error: Gradio is not installed. Install it with 'pip install gradio'.")
            sys.exit(1)
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'join':
        if args.directory:
            # Process all matching files in the directory
            if not os.path.isdir(args.directory):
                print(f"Error: '{args.directory}' is not a valid directory.")
                sys.exit(1)
            
            success = join_directory(args.directory)
            if not success:
                sys.exit(1)
        else:
            # Process individual files
            if not args.right:
                join_parser.error("--right is required when --left is specified")
            
            # Check if input files exist
            for input_file in [args.left, args.right]:
                if not os.path.exists(input_file):
                    print(f"Error: Input file '{input_file}' does not exist.")
                    sys.exit(1)
            
            # Join the files
            success = join_mono_to_stereo(args.left, args.right, args.output)
            if not success:
                sys.exit(1)
    
    elif args.command == 'slice':
        if args.file:
            # Slice a single file
            if not os.path.exists(args.file):
                print(f"Error: Input file '{args.file}' does not exist.")
                sys.exit(1)
            
            # Get output prefix (remove .wav extension)
            output_prefix = args.file[:-4] if args.file.lower().endswith('.wav') else args.file
            
            success = slice_audio_file(args.file, output_prefix, args.bpm, args.bars)
            if not success:
                sys.exit(1)
                
        elif args.directory:
            # Slice all stereo files in the directory
            if not os.path.isdir(args.directory):
                print(f"Error: '{args.directory}' is not a valid directory.")
                sys.exit(1)
            
            success = slice_directory(args.directory, args.bpm, args.bars)
            if not success:
                sys.exit(1)
                
        else:
            slice_parser.error("either --file or --directory must be specified")
    
    elif args.command == 'normalize':
        if args.file:
            # Normalize a single file
            if not os.path.exists(args.file):
                print(f"Error: Input file '{args.file}' does not exist.")
                sys.exit(1)
            
            success = normalize_audio_file(args.file, args.output, args.peak)
            if not success:
                sys.exit(1)
                
        elif args.directory:
            # Normalize all files in the directory
            if not os.path.isdir(args.directory):
                print(f"Error: '{args.directory}' is not a valid directory.")
                sys.exit(1)
            
            success = normalize_directory(args.directory, args.peak)
            if not success:
                sys.exit(1)
                
        else:
            norm_parser.error("either --file or --directory must be specified")
    
    elif args.command == 'convert':
        if args.file:
            # Convert a single file
            if not os.path.exists(args.file):
                print(f"Error: Input file '{args.file}' does not exist.")
                sys.exit(1)
            
            success = convert_audio_file(args.file, args.output, args.samplerate, args.bitdepth)
            if not success:
                sys.exit(1)
                
        elif args.directory:
            # Convert all files in the directory
            if not os.path.isdir(args.directory):
                print(f"Error: '{args.directory}' is not a valid directory.")
                sys.exit(1)
            
            success = convert_directory(args.directory, args.samplerate, args.bitdepth)
            if not success:
                sys.exit(1)
                
        else:
            conv_parser.error("either --file or --directory must be specified")

if __name__ == "__main__":
    main()
