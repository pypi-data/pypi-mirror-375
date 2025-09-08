# MetaToolkit

[![PyPI version](https://badge.fury.io/py/metatoolkit.svg)](https://badge.fury.io/py/metatoolkit)
[![Python version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python library for processing metadata of images, videos, and audio files. Supports adding, reading, and managing metadata information for various media files.

## Features

- 🖼️ **Image Metadata Processing** - Support for EXIF, XMP metadata in JPEG, PNG formats
- 🎬 **Video Metadata Processing** - Support for metadata tags in MP4, AVI and other formats
- 🎵 **Audio Metadata Processing** - Support for ID3 tags in MP3, WAV and other formats
- 📝 **Custom Metadata** - Support for adding custom metadata fields
- 🔧 **Command Line Tool** - Convenient command-line interface
- 🐍 **Python API** - Simple and easy-to-use Python interface

## Installation

### Install from PyPI

```bash
pip install metatoolkit
```

### Install from Source

```bash
git clone https://github.com/ihmily/metatoolkit.git
cd metatoolkit
pip install -e .
```

### Requirements

- Python >= 3.10
- Pillow >= 9.5.0
- pyexiv2 >= 2.15.4

> **Note**: Video and audio metadata writing functionality requires FFmpeg environment. Please ensure FFmpeg is properly installed on your system and accessible from the command line.

## Quick Start

### Image Metadata Processing

```python
import metatoolkit
from datetime import datetime

# Add custom metadata to image
custom_metadata = {
    "model": "stable-diffusion-v1.5",
    "prompt": "A beautiful landscape",
    "timestamp": datetime.now().isoformat(),
    "creator": "MetaToolkit"
}

# Add metadata
output_path = metatoolkit.add_image_metadata("input.png", custom_metadata=custom_metadata)

# Read metadata
metadata = metatoolkit.read_image_metadata(output_path)
print(metadata)
```

### Video Metadata Processing

```python
import metatoolkit

# Add video metadata
video_metadata = {
    "title": "My Video",
    "description": "This is a test video",
    "author": "MetaToolkit User",
    "creation_date": "2024-01-01"
}

# Add metadata
metatoolkit.add_video_metadata("input.mp4", custom_metadata=video_metadata)

# Read metadata
metadata = metatoolkit.read_video_metadata("input.mp4")
print(metadata)
```

### Audio Metadata Processing

```python
import metatoolkit

# Add audio metadata
audio_metadata = {
    "title": "My Music",
    "artist": "Artist Name",
    "album": "Album Name",
    "year": "2024"
}

# Add metadata
metatoolkit.add_audio_metadata("input.mp3", custom_metadata=audio_metadata)

# Read metadata
metadata = metatoolkit.read_audio_metadata("input.mp3")
print(metadata)
```

## Command Line Tool

MetaToolkit provides a convenient command-line tool that can be used directly in the terminal:

```bash
# Show help
metatoolkit --help

# Add image metadata
metatoolkit image add image.png --field MyTag='{\"title\":\"My Image\",\"author\":\"User\"}'

# Read image metadata
metatoolkit image read image.png

# Add video metadata
metatoolkit video add video.mp4 --field MyTag1=MyTest01 --field MyTag2=MyTest02

# Read video metadata
metatoolkit video read video.mp4

# Add audio metadata
metatoolkit audio add audio.mp3 --field MyTag1=MyTest01 --field MyTag2=MyTest02 --field MyTag3=MyTest03

# Read audio metadata
metatoolkit audio read audio.mp3
```

## API Reference

### Image Processing

- `add_image_metadata(image_path, custom_metadata=None, output_path=None)` - Add image metadata
- `read_image_metadata(image_path)` - Read image metadata
- `get_all_image_metadata(image_path)` - Get all image metadata

### Video Processing

- `add_video_metadata(video_path, custom_metadata=metadata_dict)` - Add video metadata
- `read_video_metadata(video_path)` - Read video metadata
- `get_all_video_metadata(video_path)` - Get all video metadata

### Audio Processing

- `add_audio_metadata(audio_path, custom_metadata=metadata_dict)` - Add audio metadata
- `read_audio_metadata(audio_path)` - Read audio metadata
- `get_all_audio_metadata(audio_path)` - Get all audio metadata

## Supported Formats

### Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)

### Video Formats

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)

### Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- FLAC (.flac)
- M4A (.m4a)
- OGG (.ogg)
- AAC (.aac)

## Related Tools

### Viewing and Verifying Metadata

#### ExifTool

[ExifTool](https://exiftool.org/) is a powerful command-line tool for reading, writing, and editing metadata in various file formats. It's particularly useful for viewing and verifying metadata in images.

```bash
# View all metadata in an image
exiftool image.png

# View metadata in a video
exiftool video.mp4

# View metadata in a audio
exiftool audio.mp3
```

#### FFprobe

FFprobe is part of the FFmpeg suite and is excellent for analyzing audio and video files.

```bash
# View video metadata
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4

# View audio metadata
ffprobe -v quiet -print_format json -show_format audio.mp3
```

### Installation

```bash
# Install ExifTool (Windows)
# Download from https://exiftool.org/

# Install ExifTool (macOS)
brew install exiftool

# Install ExifTool (Ubuntu/Debian)
sudo apt-get install libimage-exiftool-perl

# Install FFmpeg/FFprobe (Windows)
# Download from https://ffmpeg.org/download.html

# Install FFmpeg/FFprobe (macOS)
brew install ffmpeg

# Install FFmpeg/FFprobe (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

## Examples

Check the `examples/basic_usage.py` file for more usage examples.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version update history.

## Contact

- Project Homepage: https://github.com/ihmily/metatoolkit
- Issue Tracker: https://github.com/ihmily/metatoolkit/issues

## Acknowledgments

Thanks to all the developers who contributed to this project!