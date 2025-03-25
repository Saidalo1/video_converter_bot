"""
Video processing service using FFmpeg.
Handles format conversion, compression, trimming, and audio extraction.
"""
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import ffmpeg
from tenacity import retry, stop_after_attempt, wait_fixed

from utils.config import config
from utils.logger import logger


class VideoProcessor:
    """
    Video processing service using FFmpeg.
    Handles various video processing operations like conversion, compression,
    audio extraction, and trimming.
    """
    
    def __init__(self):
        self.temp_dir = config.TEMP_DIR
        self.ffmpeg_path = config.FFMPEG_PATH
    
    def _generate_temp_path(self, extension: str) -> Path:
        """
        Generate a temporary file path with the given extension.
        
        Args:
            extension: File extension (without dot)
            
        Returns:
            Path object for the temporary file
        """
        unique_id = str(uuid.uuid4())
        return self.temp_dir / f"{unique_id}.{extension}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _run_ffmpeg_command(self, input_path: Path, output_path: Path, options: Dict[str, Any]) -> bool:
        """
        Run FFmpeg command with specified options.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            options: Dictionary of FFmpeg options
            
        Returns:
            True if successful, False otherwise
        """
        try:
                    # Start with input file
            stream = ffmpeg.input(str(input_path))
            output_options = {}
            
            # Collect all options
            for option, value in options.items():
                if option == 'codec:v':
                    output_options['c:v'] = value
                elif option == 'codec:a':
                    output_options['c:a'] = value
                else:
                    output_options[option] = value
                    
            # Create output stream with all options at once
            stream = ffmpeg.output(stream, str(output_path), **output_options)
            
            # Log the command that would be run
            logger.info(f"FFmpeg command: {' '.join(ffmpeg.compile(stream))}")
            
            # Run the command with overwrite output flag
            ffmpeg.run(stream, overwrite_output=True)
            
            logger.info(f"FFmpeg operation completed: {input_path} -> {output_path}")
            return True
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
            return False
        except Exception as e:
            logger.error(f"Error in video processing: {str(e)}")
            return False
    
    def _convert_to_gif(self, input_path: Path, output_path: Path) -> Optional[Path]:
        """
        Convert video to GIF with optimized settings.
        
        Args:
            input_path: Path to input video file
            output_path: Path to output GIF file
            
        Returns:
            Path to the converted GIF file or None if conversion failed
        """
        try:
            # Create a palette for better color quality
            palette_path = self._generate_temp_path("png")
            
            # Improved settings for better GIF quality
            fps = 12       # Slightly higher FPS for smoother animation
            scale = 640    # Larger size for better quality
            dither = 'sierra2_4a'  # Better dithering algorithm
            
            # Generate palette first for better colors
            palette_cmd = [
                self.ffmpeg_path,
                '-i', str(input_path),
                '-vf', f'fps={fps},scale={scale}:-1:flags=lanczos,palettegen=stats_mode=diff',
                '-y', str(palette_path)
            ]
            
            # Execute the palette command
            import subprocess
            subprocess.run(palette_cmd, check=True, capture_output=True)
            
            # Create the GIF using the palette with improved settings
            gif_cmd = [
                self.ffmpeg_path,
                '-i', str(input_path),
                '-i', str(palette_path),
                '-filter_complex', 
                f'fps={fps},scale={scale}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither={dither}:diff_mode=rectangle',
                '-y', str(output_path)
            ]
            
            # Execute the GIF creation command
            subprocess.run(gif_cmd, check=True, capture_output=True)
            
            # Clean up palette
            self.cleanup_temp_file(palette_path)
            
            logger.info(f"GIF conversion completed with enhanced quality: {input_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting to GIF: {str(e)}")
            return None
    
    def convert_format(self, input_path: Path, output_format: str, 
                      video_codec: Optional[str] = None,
                      audio_codec: Optional[str] = None) -> Optional[Path]:
        """
        Convert video to a different format.
        
        Args:
            input_path: Path to input video file
            output_format: Target format (mp4, avi, mkv, etc.)
            video_codec: Optional video codec (h264, h265, etc.)
            audio_codec: Optional audio codec (aac, mp3, etc.)
            
        Returns:
            Path to the converted file or None if conversion failed
        """
        output_path = self._generate_temp_path(output_format)
        
        # Special case for GIF conversion
        if output_format.lower() == 'gif':
            return self._convert_to_gif(input_path, output_path)
        
        # Default options with good quality settings
        options = {}
        
        # Add common options for better quality output
        if output_format.lower() in ['mp4', 'mkv', 'webm', 'avi', 'mov']:
            options['movflags'] = '+faststart'  # Optimize for streaming
        
        # Set appropriate default codecs for common formats
        if not video_codec:
            if output_format.lower() in ['mp4', 'mkv', 'mov']:
                options['codec:v'] = 'libx264'
                options['crf'] = '20'  # Good quality
                options['preset'] = 'medium'
                options['pix_fmt'] = 'yuv420p'  # Better compatibility
            elif output_format.lower() == 'webm':
                options['codec:v'] = 'libvpx-vp9'
                options['crf'] = '30'  # Good for VP9
                options['b:v'] = '0'  # Use variable bitrate
                options['deadline'] = 'good'  # Better quality-speed balance
            elif output_format.lower() == 'avi':
                options['codec:v'] = 'mpeg4'
                options['qscale:v'] = '3'  # Good quality (1-31, lower is better)
        else:
            options['codec:v'] = video_codec
            
        # Set appropriate audio codec
        if not audio_codec:
            if output_format.lower() in ['mp4', 'mkv', 'mov']:
                options['codec:a'] = 'aac'
                options['b:a'] = '192k'
            elif output_format.lower() == 'webm':
                options['codec:a'] = 'libopus'
                options['b:a'] = '128k'
            elif output_format.lower() == 'avi':
                options['codec:a'] = 'libmp3lame'
                options['b:a'] = '192k'
        else:
            options['codec:a'] = audio_codec
        
        if self._run_ffmpeg_command(input_path, output_path, options):
            return output_path
        return None
    
    def compress_video(self, input_path: Path, quality: str = 'medium') -> Optional[Path]:
        """
        Compress video with specified quality level.
        
        Args:
            input_path: Path to input video file
            quality: Compression quality ('low', 'medium', 'high')
            
        Returns:
            Path to compressed file or None if compression failed
        """
        # Determine file extension from input
        extension = input_path.suffix[1:]  # Remove leading dot
        output_path = self._generate_temp_path(extension)
        
        # Set compression options based on quality
        compression_options = {
            'low': {'crf': '28', 'preset': 'faster'},  # Lower quality, smaller file
            'medium': {'crf': '23', 'preset': 'medium'},  # Balanced
            'high': {'crf': '20', 'preset': 'medium'}  # High quality but still compressed
        }
        
        # Use h264 codec with selected compression settings
        options = {
            'codec:v': 'libx264',
            **compression_options.get(quality, compression_options['medium'])
        }
        
        if self._run_ffmpeg_command(input_path, output_path, options):
            return output_path
        return None
    
    def extract_audio(self, input_path: Path, audio_format: str = 'mp3', 
                     bitrate: str = '192k', start_time: Optional[float] = None,
                     end_time: Optional[float] = None) -> Optional[Path]:
        """
        Extract audio from video file with optional time range.
        
        Args:
            input_path: Path to input video file
            audio_format: Target audio format (mp3, aac, etc.)
            bitrate: Audio bitrate
            start_time: Optional start time in seconds
            end_time: Optional end time in seconds
            
        Returns:
            Path to extracted audio file or None if extraction failed
        """
        output_path = self._generate_temp_path(audio_format)
        
        options = {
            'vn': None,  # No video
            'codec:a': 'libmp3lame' if audio_format == 'mp3' else 'aac',
            'b:a': bitrate
        }
        
        # Add time constraints if specified
        if start_time is not None:
            options['ss'] = str(start_time)
        if end_time is not None:
            options['to'] = str(end_time)
        
        if self._run_ffmpeg_command(input_path, output_path, options):
            return output_path
        return None
        
    def replace_audio(self, video_path: Path, audio_path: Path, 
                     output_format: Optional[str] = None) -> Optional[Path]:
        """
        Replace audio stream in video with a new audio file.
        
        Args:
            video_path: Path to input video file
            audio_path: Path to audio file to use as replacement
            output_format: Output format (uses input video format if not specified)
            
        Returns:
            Path to output video file with replaced audio or None if failed
        """
        # Use input format if output format not specified
        if not output_format:
            output_format = video_path.suffix[1:]
            
        output_path = self._generate_temp_path(output_format)
        
        try:
            # Using direct ffmpeg command for better control
            video_stream = ffmpeg.input(str(video_path))
            audio_stream = ffmpeg.input(str(audio_path))
            
            # Create output with video from first input and audio from second
            output = ffmpeg.output(
                video_stream.video,   # Take video stream from the video file
                audio_stream.audio,   # Take audio stream from the audio file
                str(output_path),
                c='copy',             # Use copy codec for faster processing
                shortest=None         # End when shortest input stream ends
            )
            
            # Run the command
            ffmpeg.run(output, overwrite_output=True)
            
            logger.info(f"Audio replacement completed: {video_path} + {audio_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error replacing audio: {str(e)}")
            return None
    
    def trim_video(self, input_path: Path, start_time: float, 
                  end_time: Optional[float] = None,
                  output_format: Optional[str] = None) -> Optional[Path]:
        """
        Trim video to specified time range.
        
        Args:
            input_path: Path to input video file
            start_time: Start time in seconds
            end_time: End time in seconds (optional)
            output_format: Output format (uses input format if not specified)
            
        Returns:
            Path to trimmed video file or None if trimming failed
        """
        # Use input format if output format not specified
        if not output_format:
            output_format = input_path.suffix[1:]
        
        output_path = self._generate_temp_path(output_format)
        
        # Two-pass approach for better quality
        # First, we seek to position and then encode
        options = {}
        
        # Seek to the specified position before input
        options['ss'] = str(start_time)
        
        # Add end time if specified
        if end_time is not None:
            options['to'] = str(end_time)
        
        # Use libx264 with high quality settings
        options['codec:v'] = 'libx264'
        options['crf'] = '16'  # Very high quality (lower is better)
        options['preset'] = 'medium'  # Better balance between speed and quality
        options['codec:a'] = 'aac'  # Use AAC for audio
        options['b:a'] = '192k'  # Higher audio quality
        options['flags'] = '+global_header'  # Better compatibility
        options['movflags'] = '+faststart'  # Optimize for streaming
        
        if self._run_ffmpeg_command(input_path, output_path, options):
            return output_path
        return None
    
    def cleanup_temp_file(self, file_path: Path) -> bool:
        """
        Delete a temporary file.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Only delete files in the temp directory
            if str(file_path).startswith(str(self.temp_dir)) and file_path.exists():
                os.remove(file_path)
                logger.info(f"Deleted temporary file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete temporary file {file_path}: {str(e)}")
            return False


# Create a global instance
video_processor = VideoProcessor()
