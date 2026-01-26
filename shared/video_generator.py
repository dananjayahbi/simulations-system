#!/usr/bin/env python3
# video_generator.py - Global video generation service using FFmpeg

"""
Video Generator Service
=======================
A global service that generates high-quality videos from frame folders.
Uses FFmpeg for efficient video encoding.

Usage:
    from shared.video_generator import VideoGenerator
    
    generator = VideoGenerator()
    generator.generate_video(
        frame_folder="path/to/frames",
        output_name="my_video",
        fps=60
    )
"""

import subprocess
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import json
import re

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "videos"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logger = logging.getLogger('video_generator')


class VideoGeneratorError(Exception):
    """Custom exception for video generation errors."""
    pass


class VideoGenerator:
    """
    Global video generation service using FFmpeg.
    
    Attributes:
        output_dir: Directory where generated videos are saved
        ffmpeg_path: Path to FFmpeg executable
    """
    
    # Supported image extensions for frames
    SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')
    
    # Video quality presets
    QUALITY_PRESETS = {
        'low': {'crf': 28, 'preset': 'fast', 'bitrate': '2M'},
        'medium': {'crf': 23, 'preset': 'medium', 'bitrate': '5M'},
        'high': {'crf': 18, 'preset': 'slow', 'bitrate': '10M'},
        'ultra': {'crf': 15, 'preset': 'veryslow', 'bitrate': '20M'},
        'lossless': {'crf': 0, 'preset': 'veryslow', 'bitrate': None}
    }
    
    def __init__(self, output_dir: Optional[Path] = None, ffmpeg_path: str = 'ffmpeg'):
        """
        Initialize the video generator.
        
        Args:
            output_dir: Custom output directory (defaults to BASE_DIR/output/videos)
            ffmpeg_path: Path to FFmpeg executable (defaults to 'ffmpeg' in PATH)
        """
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = ffmpeg_path
        
        # Check if FFmpeg is available
        self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available and log version."""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                logger.info(f"FFmpeg available: {version_line}")
                return True
            else:
                logger.warning("FFmpeg returned non-zero exit code")
                return False
        except FileNotFoundError:
            logger.error("FFmpeg not found. Please install FFmpeg and add to PATH.")
            return False
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg version check timed out")
            return False
        except Exception as e:
            logger.error(f"Error checking FFmpeg: {e}")
            return False
    
    def _get_frame_info(self, frame_folder: Path) -> Dict:
        """
        Analyze frames in a folder to get info about naming pattern and count.
        
        Returns:
            Dict with frame info: count, pattern, extension, first_frame, last_frame
        """
        frame_folder = Path(frame_folder)
        
        if not frame_folder.exists():
            raise VideoGeneratorError(f"Frame folder not found: {frame_folder}")
        
        # Find all image files
        frames = []
        for ext in self.SUPPORTED_EXTENSIONS:
            frames.extend(frame_folder.glob(f'*{ext}'))
            frames.extend(frame_folder.glob(f'*{ext.upper()}'))
        
        if not frames:
            raise VideoGeneratorError(f"No image files found in {frame_folder}")
        
        # Sort frames naturally (handle numeric sorting)
        def natural_sort_key(path):
            # Extract numbers from filename for natural sorting
            numbers = re.findall(r'\d+', path.stem)
            return [int(n) for n in numbers] if numbers else [path.stem]
        
        frames.sort(key=natural_sort_key)
        
        # Analyze naming pattern
        first_frame = frames[0]
        last_frame = frames[-1]
        
        # Detect numbering pattern
        stem = first_frame.stem
        numbers = re.findall(r'\d+', stem)
        
        # Common patterns: frame_0001.png, 0001.png, frame-1.png
        pattern = None
        if numbers:
            num = numbers[-1]  # Use last number in filename
            num_len = len(num)
            pattern = re.sub(r'\d+', f'%0{num_len}d', stem, count=1)
        
        return {
            'count': len(frames),
            'extension': first_frame.suffix,
            'pattern': pattern,
            'first_frame': first_frame,
            'last_frame': last_frame,
            'frames': frames
        }
    
    def generate_video(
        self,
        frame_folder: str | Path,
        output_name: Optional[str] = None,
        fps: int = 60,
        quality: str = 'high',
        codec: str = 'libx264',
        format: str = 'mp4',
        resolution: Optional[tuple] = None,
        custom_ffmpeg_args: Optional[List[str]] = None,
        overwrite: bool = True,
        progress_callback: Optional[callable] = None
    ) -> Path:
        """
        Generate a video from a folder of frames.
        
        Args:
            frame_folder: Path to folder containing frame images
            output_name: Output video filename (without extension). 
                        If None, uses folder name with timestamp
            fps: Frames per second (default: 60)
            quality: Quality preset ('low', 'medium', 'high', 'ultra', 'lossless')
            codec: Video codec (default: 'libx264' for H.264)
            format: Output format (default: 'mp4')
            resolution: Optional (width, height) to resize video
            custom_ffmpeg_args: Additional FFmpeg arguments
            overwrite: Overwrite existing output file (default: True)
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Path to the generated video file
        """
        frame_folder = Path(frame_folder)
        
        logger.info(f"Starting video generation from: {frame_folder}")
        
        # Analyze frames
        frame_info = self._get_frame_info(frame_folder)
        logger.info(f"Found {frame_info['count']} frames")
        
        # Determine output filename
        if not output_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f"{frame_folder.name}_{timestamp}"
        
        output_path = self.output_dir / f"{output_name}.{format}"
        
        # Get quality settings
        if quality not in self.QUALITY_PRESETS:
            logger.warning(f"Unknown quality preset '{quality}', using 'high'")
            quality = 'high'
        
        quality_settings = self.QUALITY_PRESETS[quality]
        
        # Build FFmpeg command
        cmd = [self.ffmpeg_path]
        
        # Overwrite flag
        if overwrite:
            cmd.append('-y')
        
        # Input settings
        cmd.extend([
            '-framerate', str(fps),
            '-i', str(frame_folder / f'%*{frame_info["extension"]}')
        ])
        
        # Use glob pattern for input if pattern detection failed
        # Alternative approach: create a file list
        input_pattern = str(frame_folder / f'*{frame_info["extension"]}')
        
        # Rebuild command with concat demuxer for reliability
        cmd = [self.ffmpeg_path]
        if overwrite:
            cmd.append('-y')
        
        # Create temporary file list for frames
        file_list_path = LOGS_DIR / f"frames_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(file_list_path, 'w', encoding='utf-8') as f:
            for frame in frame_info['frames']:
                # Escape single quotes and use FFmpeg's file list format
                escaped_path = str(frame).replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
                f.write(f"duration {1/fps}\n")
        
        cmd.extend([
            '-f', 'concat',
            '-safe', '0',
            '-i', str(file_list_path),
        ])
        
        # Video codec settings
        cmd.extend(['-c:v', codec])
        
        # Quality settings for H.264/H.265
        if codec in ['libx264', 'libx265']:
            cmd.extend([
                '-crf', str(quality_settings['crf']),
                '-preset', quality_settings['preset']
            ])
            
            # Pixel format for compatibility
            cmd.extend(['-pix_fmt', 'yuv420p'])
        
        # Resolution scaling if specified
        if resolution:
            cmd.extend(['-vf', f"scale={resolution[0]}:{resolution[1]}"])
        
        # Custom arguments
        if custom_ffmpeg_args:
            cmd.extend(custom_ffmpeg_args)
        
        # Output file
        cmd.append(str(output_path))
        
        logger.info(f"FFmpeg command: {' '.join(cmd)}")
        
        try:
            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            # Clean up file list
            if file_list_path.exists():
                file_list_path.unlink()
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise VideoGeneratorError(f"FFmpeg failed: {result.stderr}")
            
            logger.info(f"Video generated successfully: {output_path}")
            logger.info(f"Output size: {output_path.stat().st_size / (1024*1024):.2f} MB")
            
            return output_path
            
        except subprocess.TimeoutExpired:
            logger.error("Video generation timed out")
            raise VideoGeneratorError("Video generation timed out (exceeded 1 hour)")
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            raise VideoGeneratorError(f"Failed to generate video: {e}")
    
    def generate_from_multiple_folders(
        self,
        frame_folders: List[str | Path],
        output_name: str,
        fps: int = 60,
        quality: str = 'high',
        transition: Optional[str] = None,
        **kwargs
    ) -> Path:
        """
        Generate a single video from multiple frame folders.
        Frames are concatenated in the order provided.
        
        Args:
            frame_folders: List of paths to frame folders
            output_name: Output video filename
            fps: Frames per second
            quality: Quality preset
            transition: Optional transition between folders (future feature)
            **kwargs: Additional arguments passed to generate_video
        
        Returns:
            Path to the generated video file
        """
        logger.info(f"Generating video from {len(frame_folders)} folders")
        
        # Collect all frames from all folders
        all_frames = []
        for folder in frame_folders:
            folder = Path(folder)
            frame_info = self._get_frame_info(folder)
            all_frames.extend(frame_info['frames'])
        
        if not all_frames:
            raise VideoGeneratorError("No frames found in any of the provided folders")
        
        logger.info(f"Total frames: {len(all_frames)}")
        
        # Create combined file list
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_list_path = LOGS_DIR / f"combined_frames_{timestamp}.txt"
        
        with open(file_list_path, 'w', encoding='utf-8') as f:
            for frame in all_frames:
                escaped_path = str(frame).replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
                f.write(f"duration {1/fps}\n")
        
        # Get quality settings
        quality_settings = self.QUALITY_PRESETS.get(quality, self.QUALITY_PRESETS['high'])
        
        output_path = self.output_dir / f"{output_name}.mp4"
        
        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(file_list_path),
            '-c:v', 'libx264',
            '-crf', str(quality_settings['crf']),
            '-preset', quality_settings['preset'],
            '-pix_fmt', 'yuv420p',
            str(output_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            # Clean up
            if file_list_path.exists():
                file_list_path.unlink()
            
            if result.returncode != 0:
                raise VideoGeneratorError(f"FFmpeg failed: {result.stderr}")
            
            logger.info(f"Combined video generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating combined video: {e}")
            raise
    
    def get_video_info(self, video_path: str | Path) -> Dict:
        """Get information about a video file using FFprobe."""
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise VideoGeneratorError(f"Video file not found: {video_path}")
        
        try:
            # Use ffprobe to get video info
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {'error': result.stderr}
                
        except FileNotFoundError:
            return {'error': 'ffprobe not found'}
        except Exception as e:
            return {'error': str(e)}
    
    def list_output_videos(self) -> List[Dict]:
        """List all generated videos in the output directory."""
        videos = []
        
        for video_file in self.output_dir.glob('*.mp4'):
            stat = video_file.stat()
            videos.append({
                'name': video_file.name,
                'path': str(video_file),
                'size_mb': stat.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # Sort by modification time (newest first)
        videos.sort(key=lambda x: x['modified'], reverse=True)
        
        return videos


# Convenience function for simple usage
def generate_video(
    frame_folder: str | Path,
    output_name: Optional[str] = None,
    fps: int = 60,
    quality: str = 'high'
) -> Path:
    """
    Simple function to generate a video from frames.
    
    Args:
        frame_folder: Path to folder containing frame images
        output_name: Output video filename (optional)
        fps: Frames per second
        quality: Quality preset
    
    Returns:
        Path to the generated video
    """
    generator = VideoGenerator()
    return generator.generate_video(
        frame_folder=frame_folder,
        output_name=output_name,
        fps=fps,
        quality=quality
    )


if __name__ == '__main__':
    # Example usage / CLI
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate video from frames')
    parser.add_argument('frame_folder', help='Path to folder containing frames')
    parser.add_argument('-o', '--output', help='Output video name')
    parser.add_argument('-f', '--fps', type=int, default=60, help='Frames per second')
    parser.add_argument('-q', '--quality', default='high', 
                       choices=['low', 'medium', 'high', 'ultra', 'lossless'])
    
    args = parser.parse_args()
    
    # Configure logging for CLI
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    
    try:
        output = generate_video(
            frame_folder=args.frame_folder,
            output_name=args.output,
            fps=args.fps,
            quality=args.quality
        )
        print(f"\n✅ Video generated: {output}")
    except VideoGeneratorError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
