#!/usr/bin/env python3
"""
Video to Single GIF Converter

Converts a specified duration of video to a single GIF file.

Requirements:
    ffmpeg (usually pre-installed on most systems)

Usage:
    python video_to_single_gif.py input_video.mp4 --duration 10 --start 0
"""

import argparse
import os
import subprocess
from pathlib import Path


def convert_video_to_gif(
    video_path: str,
    start_time: float = 0,
    duration: float = 10,
    fps: int = 10,
    max_width: int = 480,
    output_path: str = None,
    quality: str = 'medium'
):
    """
    Convert a portion of video to a single GIF.
    
    Args:
        video_path: Path to the input video file
        start_time: Start time in seconds (default: 0)
        duration: Duration in seconds (default: 10)
        fps: Frames per second for the output GIF (default: 10)
        max_width: Maximum width in pixels (default: 480)
        output_path: Output file path (default: same name as video with .gif extension)
        quality: Quality preset - 'low', 'medium', 'high' (default: 'medium')
    """
    
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("ffmpeg is not installed or not in PATH")
    
    # Validate input file
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    video_path = Path(video_path)
    
    # Set output path
    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}.gif"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Input video: {video_path}")
    print(f"Converting {duration}s starting from {start_time}s")
    print(f"Output: {output_path}")
    
    # Quality settings
    quality_settings = {
        'low': {'colors': '128', 'dither': 'bayer:bayer_scale=3'},
        'medium': {'colors': '256', 'dither': 'bayer:bayer_scale=5'},
        'high': {'colors': '256', 'dither': 'none'}
    }
    
    q_settings = quality_settings.get(quality, quality_settings['medium'])
    
    # Temporary palette file
    palette_path = output_path.parent / f"palette_temp.png"
    
    try:
        print("Generating color palette...")
        # Generate palette
        palette_cmd = [
            'ffmpeg',
            '-ss', str(start_time),
            '-t', str(duration),
            '-i', str(video_path),
            '-vf', f'fps={fps},scale={max_width}:-1:flags=lanczos,palettegen=max_colors={q_settings["colors"]}',
            '-y',
            str(palette_path)
        ]
        subprocess.run(palette_cmd, capture_output=True, check=True)
        
        print("Creating GIF...")
        # Create GIF using palette
        gif_cmd = [
            'ffmpeg',
            '-ss', str(start_time),
            '-t', str(duration),
            '-i', str(video_path),
            '-i', str(palette_path),
            '-lavfi', f'fps={fps},scale={max_width}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither={q_settings["dither"]}',
            '-y',
            str(output_path)
        ]
        subprocess.run(gif_cmd, capture_output=True, check=True)
        
        # Clean up palette
        palette_path.unlink()
        
        # Get file size
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ Success! Created: {output_path}")
        print(f"  File size: {size_mb:.2f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        if palette_path.exists():
            palette_path.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Convert video to a single GIF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First 10 seconds
  python video_to_single_gif.py my_video.mp4
  
  # 15 seconds starting from 5 seconds
  python video_to_single_gif.py my_video.mp4 --start 5 --duration 15
  
  # High quality, 15 fps
  python video_to_single_gif.py my_video.mp4 --quality high --fps 15
  
  # Custom output path
  python video_to_single_gif.py my_video.mp4 --output ./output/result.gif
        """
    )
    
    parser.add_argument(
        "video_path",
        help="Path to the input video file"
    )
    
    parser.add_argument(
        "-s", "--start",
        type=float,
        default=3,
        help="Start time in seconds (default: 0)"
    )
    
    parser.add_argument(
        "-d", "--duration",
        type=float,
        default=10,
        help="Duration in seconds (default: 10)"
    )
    
    parser.add_argument(
        "-f", "--fps",
        type=int,
        default=10,
        help="Frames per second (default: 10)"
    )
    
    parser.add_argument(
        "-w", "--max-width",
        type=int,
        default=480,
        help="Maximum width in pixels (default: 480)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: same name as video with .gif extension)"
    )
    
    parser.add_argument(
        "-q", "--quality",
        choices=['low', 'medium', 'high'],
        default='medium',
        help="Quality preset (default: medium)"
    )
    
    args = parser.parse_args()
    
    try:
        convert_video_to_gif(
            video_path=args.video_path,
            start_time=args.start,
            duration=args.duration,
            fps=args.fps,
            max_width=args.max_width,
            output_path=args.output,
            quality=args.quality
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())