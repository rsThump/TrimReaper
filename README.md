# TrimReaper - Audio Processing Tool

TrimReaper is a versatile audio processing tool with both a Gradio web UI and command-line interface. It helps audio engineers and producers efficiently process and prepare audio files for mixing, mastering, and sample management.

![TrimReaper](https://github.com/rsThump/TrimReaper/raw/main/docs/images/trimreaper_logo.png)

## Features

- **Join Mono Files**: Combine left and right channel mono files into stereo files with automatic channel pairing
- **Slice Audio**: Split audio files into segments based on BPM and bars per slice
- **Normalize Audio**: Adjust audio levels to precise target peak values
- **Convert Audio**: Change sample rate and bit depth with high-quality conversion
- **Trim Audio**: Remove silence at the end of files with zero-crossing detection for clean edits
- **Rename Files**: Batch rename based on MIDI notes and General MIDI drum map

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Clone this repository:

```shell
git clone https://github.com/rsThump/TrimReaper.git
cd TrimReaper

```

2. Install the required dependencies:

```shell
pip install -r requirements.txt

```

## Usage

### Graphical User Interface

Launch the GUI for easy access to all features:


```shell
python trimmer.py --ui

```

## Module Details

### Join Mono Files
- Combines L/R mono WAV files into stereo
- Automatically pairs files based on naming patterns (e.g., "Kick L.wav" and "Kick R.wav")
- Supports batch processing of entire directories

### Slice Audio
- Divides audio files into equal segments based on musical timing
- Configurable BPM and bars per slice
- Creates accurately timed loops for sampling

### Normalize Audio
- Adjusts peak levels to target dB values (-0.1 dB default)
- Maintains relative dynamics while optimizing levels
- Works with various bit depths (16/24/32-bit)

### Convert Audio
- Changes sample rate (44.1, 48, 88.2, 96 kHz)
- Converts bit depth (16, 24, 32-bit)
- Handles multiple file formats (WAV, FLAC, AIFF)

### Trim Audio
- Removes silence at the end of files
- Uses zero-crossing detection for clean edits
- Configurable silence threshold and minimum tail duration
- Perfect for preparing samples for samplers and drum machines

### Rename Files
- Batch renames audio files using MIDI note numbers
- Maps to GM Drum Map instrument names
- Customizable naming patterns with format strings
- Preview mode to check changes before applying

## Interface Guide

### Join Mono Files Tab
- Upload individual L/R channel files or process entire directories
- Automatically handles naming conventions

### Slice Audio Tab
- Set BPM and bars per slice for accurate musical timing
- Process individual files or entire directories

### Normalize Audio Tab
- Adjust target peak level with precision slider
- Process files individually or in batch

### Convert Audio Tab
- Select sample rate and bit depth from dropdown menus
- Easily convert between different audio formats

### Trim Audio Tab
- Set silence threshold and minimum tail duration
- Preserves audio quality with zero-crossing detection

### Rename Files Tab
- Set starting MIDI note and customize naming format
- Preview mode shows changes before applying
- Includes GM Drum Map naming conventions

### Command Line Interface

TrimReaper can be used via command line for batch processing and automation.

#### Join Mono Files

Join two mono WAV files into a stereo file:

```shell
python trimmer.py join -l left_channel.wav -r right_channel.wav -o output_stereo.wav

```

Process all matching mono files in a directory:

```shell
python trimmer.py join -d /path/to/directory

```

#### Slice Audio

Slice a stereo file into segments based on BPM:

```shell
python trimmer.py slice -f input_file.wav -b 120 -a 2

```

Process all stereo files in a directory:

```shell
python trimmer.py slice -d /path/to/directory -b 120 -a 4

```

#### Normalize Audio

Normalize a file to a specific peak level:

```shell
python trimmer.py normalize -f input_file.wav -p -0.1 -o output_normalized.wav

```

Normalize all files in a directory:

```shell
python trimmer.py normalize -d /path/to/directory -p -0.5

```

#### Convert Audio

Convert a file's sample rate and bit depth:

```shell
python trimmer.py convert -f input_file.wav -s 44100 -b 16 -o output_converted.wav

```

Convert all files in a directory:

```shell
python trimmer.py convert -d /path/to/directory -s 48000 -b 24

```

#### Trim Audio

Trim silence from the end of a file:

```shell
# Not directly available in the CLI (use the UI for this feature)

```
## Requirements

- Python 3.7+
- SoundFile
- NumPy
- Gradio
- Wave (standard library)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- General MIDI drum mapping standard
- Zero-crossing detection techniques for clean audio editing

---

Created by Thump for Recluse Studios.
