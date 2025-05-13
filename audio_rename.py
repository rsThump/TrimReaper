# audio_rename.py
import os
import re

# Complete GM Drum Map
GM_DRUM_MAP = {
    35: "Acoustic Bass Drum",
    36: "Bass Drum 1",
    37: "Side Stick",
    38: "Acoustic Snare",
    39: "Hand Clap",
    40: "Electric Snare",
    41: "Low Floor Tom",
    42: "Closed Hi-Hat",
    43: "High Floor Tom",
    44: "Pedal Hi-Hat",
    45: "Low Tom",
    46: "Open Hi-Hat",
    47: "Low-Mid Tom",
    48: "Hi-Mid Tom",
    49: "Crash Cymbal 1",
    50: "High Tom",
    51: "Ride Cymbal 1",
    52: "Chinese Cymbal",
    53: "Ride Bell",
    54: "Tambourine",
    55: "Splash Cymbal",
    56: "Cowbell",
    57: "Crash Cymbal 2",
    58: "Vibraslap",
    59: "Ride Cymbal 2",
    60: "Hi Bongo",
    61: "Low Bongo",
    62: "Mute Hi Conga",
    63: "Open Hi Conga",
    64: "Low Conga",
    65: "High Timbale",
    66: "Low Timbale",
    67: "High Agogo",
    68: "Low Agogo",
    69: "Cabasa",
    70: "Maracas",
    71: "Short Whistle",
    72: "Long Whistle",
    73: "Short Guiro",
    74: "Long Guiro",
    75: "Claves",
    76: "Hi Wood Block",
    77: "Low Wood Block",
    78: "Mute Cuica",
    79: "Open Cuica",
    80: "Mute Triangle",
    81: "Open Triangle"
}


def rename_files_by_midi_notes(directory, output_dir, start_note=35, name_format="{original_name}_{note:03d}_{instrument}{ext}", 
                              overwrite=False, preview_only=True):
    """Rename audio files in directory according to MIDI notes, starting from start_note."""
    if not os.path.isdir(directory):
        return False, "Input directory doesn't exist"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all audio files
    audio_files = [f for f in os.listdir(directory) 
                  if f.endswith(('.wav', '.flac', '.aiff', '.aif'))]
    audio_files.sort()  # Sort to ensure consistent ordering
    
    # Check if we have enough notes
    if start_note + len(audio_files) - 1 > 127:
        return False, f"Not enough MIDI notes available. Need {len(audio_files)} notes starting from {start_note}."
    
    # Generate new names
    rename_mapping = []
    current_note = start_note
    
    for old_file in audio_files:
        old_path = os.path.join(directory, old_file)
        base_name, ext = os.path.splitext(old_file)
        
        # Get instrument name if available in GM drum map
        instrument = GM_DRUM_MAP.get(current_note, "Unnamed")
        
        # Format new name
        safe_instrument = re.sub(r'[^\w\s-]', '', instrument).replace(' ', '_')
        new_name = name_format.format(
            original_name=base_name,
            note=current_note,
            instrument=safe_instrument,
            ext=ext
        )
        
        # Replace extension if needed
        if not new_name.lower().endswith(ext.lower()):
            new_name = new_name.replace('.wav', ext)
        
        new_path = os.path.join(output_dir, new_name)
        rename_mapping.append((old_path, new_path, old_file, new_name))
        
        current_note += 1
    
    # Perform renaming if not preview only
    if not preview_only:
        success_count = 0
        for old_path, new_path, _, _ in rename_mapping:
            if os.path.exists(new_path) and not overwrite:
                print(f"Skipping {new_path} - file already exists")
                continue
                
            try:
                if directory != output_dir:
                    # Copy file to new location with new name
                    with open(old_path, 'rb') as src_file, open(new_path, 'wb') as dst_file:
                        dst_file.write(src_file.read())
                else:
                    # Direct rename
                    os.rename(old_path, new_path)
                success_count += 1
            except Exception as e:
                print(f"Error renaming {old_path}: {str(e)}")
        
        return True, f"Renamed {success_count} files successfully"
    
    # Just return the mapping for preview
    return True, rename_mapping
