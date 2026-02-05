"""Audio extraction from video files using FFmpeg."""

import subprocess
from pathlib import Path
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class AudioExtractor:
    """Extract audio from video files using FFmpeg."""
    
    def __init__(self):
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is installed."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg:\n"
                "  Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "  MacOS: brew install ffmpeg\n"
                "  Windows: Download from https://ffmpeg.org/download.html"
            )
    
    def extract_audio(
        self,
        video_path: Path,
        output_path: Path,
        quality: int = 2
    ) -> Path:
        """
        Extract audio from video file to MP3.
        
        Args:
            video_path: Path to input video file (MP4, etc.)
            output_path: Path to output MP3 file
            quality: MP3 quality (0=best, 9=worst), default 2
            
        Returns:
            Path to output MP3 file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "libmp3lame",
            "-q:a", str(quality),
            "-y",  # Overwrite output file
            str(output_path)
        ]
        
        logger.info(f"Extracting audio from {video_path.name} -> {output_path.name}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"  ✓ Audio extracted: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise RuntimeError(f"Failed to extract audio from {video_path}: {e.stderr}")
    
    def process_folder(
        self,
        input_folder: Path,
        output_folder: Path
    ) -> List[Tuple[Path, Path]]:
        """
        Process all video/audio files in a folder.
        
        Returns MP3 as-is, extracts audio from MP4/other video formats.
        
        Args:
            input_folder: Folder containing video/audio files
            output_folder: Folder for output MP3 files
            
        Returns:
            List of tuples (source_file, output_mp3)
        """
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Supported formats
        video_extensions = {".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv", ".webm"}
        audio_extensions = {".mp3", ".wav", ".m4a", ".aac", ".flac"}
        
        results = []
        
        for file_path in sorted(input_folder.iterdir()):
            if file_path.is_dir():
                continue
            
            ext = file_path.suffix.lower()
            
            if ext == ".mp3":
                # MP3 already - just note it for transcription
                logger.info(f"Found MP3: {file_path.name}")
                results.append((file_path, file_path))
                
            elif ext in video_extensions:
                # Extract audio from video
                output_mp3 = output_folder / f"{file_path.stem}.mp3"
                self.extract_audio(file_path, output_mp3)
                results.append((file_path, output_mp3))
                
            elif ext in audio_extensions:
                # Convert other audio formats to MP3
                output_mp3 = output_folder / f"{file_path.stem}.mp3"
                self.extract_audio(file_path, output_mp3)
                results.append((file_path, output_mp3))
        
        logger.info(f"Processed {len(results)} files")
        return results


def extract_audio_batch(
    input_folder: Path,
    output_folder: Path
) -> List[Path]:
    """
    Convenience function to extract audio from all files in a folder.
    
    Returns:
        List of MP3 file paths ready for transcription
    """
    extractor = AudioExtractor()
    results = extractor.process_folder(input_folder, output_folder)
    return [output_mp3 for _, output_mp3 in results]
