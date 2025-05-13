# audio_ui.py
import os
import tempfile
import shutil
import gradio as gr

# Import our modules
from audio_join import join_mono_to_stereo, find_channel_pairs
from audio_slice import slice_audio_file
from audio_normalize import normalize_audio_file
from audio_convert import convert_audio_file
from audio_trim import trim_audio_file
from audio_rename import rename_files_by_midi_notes


# Gradio interface functions
def gradio_join_mono_files(left_file, right_file, output_dir):
    """Join two mono WAV files into a stereo WAV file using Gradio interface."""
    if not left_file or not right_file:
        return "Please upload both left and right channel files"
    
    if not output_dir:
        output_dir = os.path.dirname(left_file)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output filename
    left_basename = os.path.basename(left_file)
    if " L.wav" in left_basename:
        base_name = left_basename.replace(" L.wav", "")
    else:
        base_name = os.path.splitext(left_basename)[0]
    
    output_file = os.path.join(output_dir, f"{base_name}_stereo.wav")
    
    # Join the files
    if join_mono_to_stereo(left_file, right_file, output_file):
        return f"Successfully created stereo file: {output_file}"
    else:
        return "Failed to join mono files. Check console for details."


def gradio_slice_audio(input_file, output_dir, bpm, bars_per_slice):
    """Slice a stereo WAV file using Gradio interface."""
    if not input_file:
        return "Please upload an audio file to slice"
    
    if not output_dir:
        output_dir = os.path.dirname(input_file)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output prefix
    basename = os.path.basename(input_file)
    base_name = os.path.splitext(basename)[0]
    output_prefix = os.path.join(output_dir, base_name)
    
    # Slice the file
    output_files = slice_audio_file(input_file, output_prefix, bpm, bars_per_slice)
    if output_files:
        return f"Successfully created {len(output_files)} segments in {output_dir}"
    else:
        return "Failed to slice audio file. Check console for details."


def gradio_join_directory(input_dir, output_dir):
    """Join all matching mono files in a directory using Gradio interface."""
    if not input_dir:
        return "Please select an input directory"
    
    if not output_dir:
        output_dir = input_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy files to temp directory
        for file in os.listdir(input_dir):
            if file.endswith('.wav'):
                src = os.path.join(input_dir, file)
                dst = os.path.join(temp_dir, file)
                shutil.copy2(src, dst)
        
        # Process the directory
        pairs = find_channel_pairs(temp_dir)
        
        if not pairs:
            return f"No matching L and R pairs found in {input_dir}"
        
        success_count = 0
        for left_file, right_file, temp_output_file in pairs:
            base_name = os.path.basename(temp_output_file)
            final_output = os.path.join(output_dir, base_name)
            
            left_base = os.path.basename(left_file)
            right_base = os.path.basename(right_file)
            
            if join_mono_to_stereo(
                    os.path.join(input_dir, left_base),
                    os.path.join(input_dir, right_base),
                    final_output):
                success_count += 1
        
        return f"Processed {success_count} out of {len(pairs)} file pairs successfully to {output_dir}"


def gradio_slice_directory(input_dir, output_dir, bpm, bars_per_slice):
    """Slice all stereo WAV files in a directory using Gradio interface."""
    if not input_dir:
        return "Please select an input directory"
    
    if not output_dir:
        output_dir = input_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    files = [f for f in os.listdir(input_dir) if f.endswith('_stereo.wav')]
    
    if not files:
        return f"No stereo WAV files found in {input_dir}"
    
    success_count = 0
    total_segments = 0
    
    for file in files:
        input_path = os.path.join(input_dir, file)
        base_name = file[:-4]  # Remove .wav extension
        output_prefix = os.path.join(output_dir, base_name)
        
        output_files = slice_audio_file(input_path, output_prefix, bpm, bars_per_slice)
        if output_files:
            success_count += 1
            total_segments += len(output_files)
    
    return f"Sliced {success_count} files into {total_segments} segments in {output_dir}"


def gradio_normalize_audio(input_file, output_dir, peak_db):
    """Normalize a WAV file using Gradio interface."""
    if not input_file:
        return "Please upload an audio file to normalize"
    
    if not output_dir:
        output_dir = os.path.dirname(input_file)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output filename
    basename = os.path.basename(input_file)
    base_name, ext = os.path.splitext(basename)
    output_file = os.path.join(output_dir, f"{base_name}_normalized{ext}")
    
    # Normalize the file
    if normalize_audio_file(input_file, output_file, peak_db):
        return f"Successfully normalized file: {output_file} to {peak_db} dB"
    else:
        return "Failed to normalize audio file. Check console for details."


def gradio_normalize_directory(input_dir, output_dir, peak_db):
    """Normalize all WAV files in a directory using Gradio interface."""
    if not input_dir:
        return "Please select an input directory"
    
    if not output_dir:
        output_dir = input_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    files = [f for f in os.listdir(input_dir) if f.endswith('.wav')]
    
    if not files:
        return f"No WAV files found in {input_dir}"
    
    success_count = 0
    
    for file in files:
        input_path = os.path.join(input_dir, file)
        base_name, ext = os.path.splitext(file)
        output_file = os.path.join(output_dir, f"{base_name}_normalized{ext}")
        
        if normalize_audio_file(input_path, output_file, peak_db):
            success_count += 1
    
    return f"Normalized {success_count} out of {len(files)} files successfully in {output_dir}"


def gradio_convert_audio(input_file, output_dir, sample_rate, bit_depth):
    """Convert a WAV file using Gradio interface."""
    if not input_file:
        return "Please upload an audio file to convert"
    
    if not output_dir:
        output_dir = os.path.dirname(input_file)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output filename
    basename = os.path.basename(input_file)
    base_name, ext = os.path.splitext(basename)
    output_file = os.path.join(output_dir, f"{base_name}_converted{ext}")
    
    # Convert the file
    if convert_audio_file(input_file, output_file, sample_rate, bit_depth):
        return f"Successfully converted file: {output_file} to {sample_rate}Hz, {bit_depth}-bit"
    else:
        return "Failed to convert audio file. Check console for details."


def gradio_convert_directory(input_dir, output_dir, sample_rate, bit_depth):
    """Convert all WAV files in a directory using Gradio interface."""
    if not input_dir:
        return "Please select an input directory"
    
    if not output_dir:
        output_dir = input_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    files = [f for f in os.listdir(input_dir) if f.endswith('.wav')]
    
    if not files:
        return f"No WAV files found in {input_dir}"
    
    success_count = 0
    
    for file in files:
        input_path = os.path.join(input_dir, file)
        base_name, ext = os.path.splitext(file)
        output_file = os.path.join(output_dir, f"{base_name}_converted{ext}")
        
        if convert_audio_file(input_path, output_file, sample_rate, bit_depth):
            success_count += 1
    
    return f"Converted {success_count} out of {len(files)} files successfully in {output_dir}"


def gradio_trim_audio(input_file, output_dir, threshold_db, min_duration):
    """Trim a WAV file using Gradio interface."""
    if not input_file:
        return "Please upload an audio file to trim"
    
    if not output_dir:
        output_dir = os.path.dirname(input_file)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output filename
    basename = os.path.basename(input_file)
    base_name, ext = os.path.splitext(basename)
    output_file = os.path.join(output_dir, f"{base_name}_trimmed{ext}")
    
    # Trim the file
    if trim_audio_file(input_file, output_file, threshold_db, min_duration):
        return f"Successfully trimmed file: {output_file}"
    else:
        return "Failed to trim audio file. Check console for details."


def gradio_trim_directory(input_dir, output_dir, threshold_db, min_duration):
    """Trim all WAV files in a directory using Gradio interface."""
    if not input_dir:
        return "Please select an input directory"
    
    if not output_dir:
        output_dir = input_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    files = [f for f in os.listdir(input_dir) if f.endswith('.wav')]
    
    if not files:
        return f"No WAV files found in {input_dir}"
    
    success_count = 0
    
    for file in files:
        input_path = os.path.join(input_dir, file)
        base_name, ext = os.path.splitext(file)
        output_file = os.path.join(output_dir, f"{base_name}_trimmed{ext}")
        
        if trim_audio_file(input_path, output_file, threshold_db, min_duration):
            success_count += 1
    
    return f"Trimmed {success_count} out of {len(files)} files successfully in {output_dir}"

def gradio_rename_files(input_dir, output_dir, start_note, name_format, preview_only):
    """Rename audio files according to MIDI notes using Gradio interface."""
    from audio_rename import rename_files_by_midi_notes, GM_DRUM_MAP
    
    if not input_dir:
        return "Please select an input directory"
    
    if not output_dir:
        output_dir = input_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Preview or perform the rename operation
    success, result = rename_files_by_midi_notes(
        input_dir, 
        output_dir, 
        start_note=start_note, 
        name_format=name_format,
        preview_only=preview_only
    )
    
    if not success:
        return f"Error: {result}"
    
    if preview_only:
        # Format the mapping as a readable list for preview
        preview_text = "Preview of rename operations (Old → New):\n\n"
        for old_path, new_path, old_name, new_name in result:
            preview_text += f"{old_name} → {new_name}\n"
        return preview_text
    else:
        return f"{result}"

def launch_gradio_interface():
    """Launch the Gradio interface for the audio processing tool."""
    with gr.Blocks(title="TrimReaper") as app:
        gr.Markdown("# TrimReaper")
        
        with gr.Tab("Join Mono Files"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Join Individual Mono Files")
                    left_file = gr.File(label="Left Channel (Mono WAV)")
                    right_file = gr.File(label="Right Channel (Mono WAV)")
                    output_dir1 = gr.Textbox(label="Output Directory (optional)")
                    join_btn = gr.Button("Join Files")
                    join_result = gr.Textbox(label="Result")
                    
                    join_btn.click(
                        fn=gradio_join_mono_files,
                        inputs=[left_file, right_file, output_dir1],
                        outputs=join_result
                    )
                
                with gr.Column():
                    gr.Markdown("### Join All Mono Files in Directory")
                    input_dir1 = gr.Textbox(label="Input Directory")
                    output_dir2 = gr.Textbox(label="Output Directory (optional)")
                    join_dir_btn = gr.Button("Process Directory")
                    join_dir_result = gr.Textbox(label="Result")
                    
                    join_dir_btn.click(
                        fn=gradio_join_directory,
                        inputs=[input_dir1, output_dir2],
                        outputs=join_dir_result
                    )
        
        with gr.Tab("Slice Audio"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Slice Individual Audio File")
                    input_file = gr.File(label="Audio File (WAV)")
                    output_dir3 = gr.Textbox(label="Output Directory (optional)")
                    bpm1 = gr.Slider(label="BPM", minimum=60, maximum=200, value=120, step=1)
                    bars1 = gr.Slider(label="Bars per Slice", minimum=1, maximum=8, value=2, step=1)
                    slice_btn = gr.Button("Slice File")
                    slice_result = gr.Textbox(label="Result")
                    
                    slice_btn.click(
                        fn=gradio_slice_audio,
                        inputs=[input_file, output_dir3, bpm1, bars1],
                        outputs=slice_result
                    )
                
                with gr.Column():
                    gr.Markdown("### Slice All Audio Files in Directory")
                    input_dir2 = gr.Textbox(label="Input Directory")
                    output_dir4 = gr.Textbox(label="Output Directory (optional)")
                    bpm2 = gr.Slider(label="BPM", minimum=60, maximum=200, value=120, step=1)
                    bars2 = gr.Slider(label="Bars per Slice", minimum=1, maximum=8, value=2, step=1)
                    slice_dir_btn = gr.Button("Process Directory")
                    slice_dir_result = gr.Textbox(label="Result")
                    
                    slice_dir_btn.click(
                        fn=gradio_slice_directory,
                        inputs=[input_dir2, output_dir4, bpm2, bars2],
                        outputs=slice_dir_result
                    )
        
        with gr.Tab("Normalize Audio"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Normalize Individual Audio File")
                    norm_input_file = gr.File(label="Audio File (WAV)")
                    norm_output_dir = gr.Textbox(label="Output Directory (optional)")
                    peak_db = gr.Slider(label="Target Peak (dB)", minimum=-12.0, maximum=0.0, value=-0.1, step=0.1)
                    norm_btn = gr.Button("Normalize File")
                    norm_result = gr.Textbox(label="Result")
                    
                    norm_btn.click(
                        fn=gradio_normalize_audio,
                        inputs=[norm_input_file, norm_output_dir, peak_db],
                        outputs=norm_result
                    )
                
                with gr.Column():
                    gr.Markdown("### Normalize All Audio Files in Directory")
                    norm_input_dir = gr.Textbox(label="Input Directory")
                    norm_output_dir2 = gr.Textbox(label="Output Directory (optional)")
                    peak_db2 = gr.Slider(label="Target Peak (dB)", minimum=-12.0, maximum=0.0, value=-0.1, step=0.1)
                    norm_dir_btn = gr.Button("Process Directory")
                    norm_dir_result = gr.Textbox(label="Result")
                    
                    norm_dir_btn.click(
                        fn=gradio_normalize_directory,
                        inputs=[norm_input_dir, norm_output_dir2, peak_db2],
                        outputs=norm_dir_result
                    )
        
        with gr.Tab("Convert Audio"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Convert Individual Audio File")
                    conv_input_file = gr.File(label="Audio File (WAV)")
                    conv_output_dir = gr.Textbox(label="Output Directory (optional)")
                    sample_rate = gr.Dropdown(
                        label="Sample Rate", 
                        choices=["44100", "48000", "88200", "96000"], 
                        value="44100"
                    )
                    bit_depth = gr.Dropdown(
                        label="Bit Depth",
                        choices=["16", "24", "32"],
                        value="16"
                    )
                    conv_btn = gr.Button("Convert File")
                    conv_result = gr.Textbox(label="Result")
                    
                    conv_btn.click(
                        fn=gradio_convert_audio,
                        inputs=[conv_input_file, conv_output_dir, sample_rate, bit_depth],
                        outputs=conv_result
                    )
                
                with gr.Column():
                    gr.Markdown("### Convert All Audio Files in Directory")
                    conv_input_dir = gr.Textbox(label="Input Directory")
                    conv_output_dir2 = gr.Textbox(label="Output Directory (optional)")
                    sample_rate2 = gr.Dropdown(
                        label="Sample Rate", 
                        choices=["44100", "48000", "88200", "96000"], 
                        value="44100"
                    )
                    bit_depth2 = gr.Dropdown(
                        label="Bit Depth",
                        choices=["16", "24", "32"],
                        value="16"
                    )
                    conv_dir_btn = gr.Button("Process Directory")
                    conv_dir_result = gr.Textbox(label="Result")
                    
                    conv_dir_btn.click(
                        fn=gradio_convert_directory,
                        inputs=[conv_input_dir, conv_output_dir2, sample_rate2, bit_depth2],
                        outputs=conv_dir_result
                    )
        
        with gr.Tab("Trim Audio"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Trim Individual Audio File")
                    trim_input_file = gr.File(label="Audio File (WAV)")
                    trim_output_dir = gr.Textbox(label="Output Directory (optional)")
                    threshold_db = gr.Slider(label="Silence Threshold (dB)", minimum=-90.0, maximum=-30.0, value=-60.0, step=1.0)
                    min_duration = gr.Slider(label="Minimum Tail Duration (sec)", minimum=0.0, maximum=2.0, value=0.5, step=0.1)
                    trim_btn = gr.Button("Trim File")
                    trim_result = gr.Textbox(label="Result")
                    
                    trim_btn.click(
                        fn=gradio_trim_audio,
                        inputs=[trim_input_file, trim_output_dir, threshold_db, min_duration],
                        outputs=trim_result
                    )
                
                with gr.Column():
                    gr.Markdown("### Trim All Audio Files in Directory")
                    trim_input_dir = gr.Textbox(label="Input Directory")
                    trim_output_dir2 = gr.Textbox(label="Output Directory (optional)")
                    threshold_db2 = gr.Slider(label="Silence Threshold (dB)", minimum=-90.0, maximum=-30.0, value=-60.0, step=1.0)
                    min_duration2 = gr.Slider(label="Minimum Tail Duration (sec)", minimum=0.0, maximum=2.0, value=0.5, step=0.1)
                    trim_dir_btn = gr.Button("Process Directory")
                    trim_dir_result = gr.Textbox(label="Result")
                    
                    trim_dir_btn.click(
                        fn=gradio_trim_directory,
                        inputs=[trim_input_dir, trim_output_dir2, threshold_db2, min_duration2],
                        outputs=trim_dir_result
                    )
        
        with gr.Tab("Rename Files"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Rename Files by MIDI Notes")
                    rename_input_dir = gr.Textbox(label="Input Directory")
                    rename_output_dir = gr.Textbox(label="Output Directory (optional)")
                    start_note = gr.Number(label="Starting MIDI Note", value=35, minimum=0, maximum=127, step=1)
                    name_format = gr.Textbox(label="Name Format", value="{original_name}_{note:03d}_{instrument}{ext}")
                    preview_check = gr.Checkbox(label="Preview Only", value=True)
                    rename_btn = gr.Button("Rename Files")
                    rename_result = gr.Textbox(label="Result", lines=10)
                    
                    gr.Markdown("""
                    ### Name Format Help
                    Available placeholders:
                    - `{original_name}`: Original filename without extension
                    - `{note}`: MIDI note number
                    - `{instrument}`: Instrument name from GM Drum Map
                    - `{ext}`: File extension (including the dot)

                    Examples:
                    - `{original_name}_{note:03d}_{instrument}{ext}` -> `12Thundadome_036_Bass_Drum_1.wav`
                    - `{note:03d}_{original_name}{ext}` -> `036_12Thundadome.wav`
                    """)
                                        
                    rename_btn.click(
                        fn=gradio_rename_files,
                        inputs=[rename_input_dir, rename_output_dir, start_note, name_format, preview_check],
                        outputs=rename_result
                    )
    
    app.launch()
