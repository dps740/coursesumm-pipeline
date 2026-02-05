"""Transcription using local Whisper."""

import logging
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm

logger = logging.getLogger(__name__)


class Transcriber:
    """Transcribe audio files using Whisper."""
    
    def __init__(self, model_size: str = "medium", device: Optional[str] = None):
        """
        Initialize transcriber.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to use (cuda/cpu), auto-detects if None
        """
        self.model_size = model_size
        self.device = device
        self.model = None
        
    def _load_model(self):
        """Lazy load Whisper model."""
        if self.model is None:
            try:
                import whisper
                import torch
                
                # Auto-detect device if not specified
                if self.device is None:
                    self.device = "cuda" if torch.cuda.is_available() else "cpu"
                
                logger.info(f"Loading Whisper model '{self.model_size}' on {self.device}...")
                self.model = whisper.load_model(self.model_size, device=self.device)
                
                if self.device == "cuda":
                    gpu_name = torch.cuda.get_device_name(0)
                    logger.info(f"  ✓ Using GPU: {gpu_name}")
                else:
                    logger.info(f"  ✓ Using CPU")
                    
            except ImportError:
                raise RuntimeError(
                    "Whisper not installed. Install with:\n"
                    "  pip install openai-whisper"
                )
    
    def transcribe_file(self, audio_path: Path) -> str:
        """
        Transcribe a single audio file.
        
        Args:
            audio_path: Path to audio file (MP3, WAV, etc.)
            
        Returns:
            Transcription text
        """
        self._load_model()
        
        logger.info(f"Transcribing: {audio_path.name}")
        
        try:
            result = self.model.transcribe(str(audio_path))
            text = result["text"].strip()
            
            word_count = len(text.split())
            logger.info(f"  ✓ Transcribed {word_count} words")
            
            return text
            
        except Exception as e:
            logger.error(f"Transcription failed for {audio_path}: {e}")
            raise
    
    def transcribe_folder(
        self,
        audio_folder: Path,
        output_folder: Path,
        audio_files: Optional[List[Path]] = None
    ) -> List[Path]:
        """
        Transcribe all audio files in a folder.
        
        Args:
            audio_folder: Folder containing audio files
            output_folder: Folder for transcript text files
            audio_files: Optional list of specific files to transcribe
            
        Returns:
            List of transcript file paths
        """
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Get files to transcribe
        if audio_files is None:
            audio_files = sorted([
                f for f in audio_folder.iterdir()
                if f.suffix.lower() in {".mp3", ".wav", ".m4a", ".aac"}
            ])
        
        if not audio_files:
            logger.warning(f"No audio files found in {audio_folder}")
            return []
        
        logger.info(f"Found {len(audio_files)} audio files to transcribe")
        
        transcript_paths = []
        
        # Process each file with progress bar
        for audio_path in tqdm(audio_files, desc="Transcribing", unit="file"):
            output_path = output_folder / f"{audio_path.stem}.txt"
            
            # Skip if already transcribed
            if output_path.exists():
                logger.info(f"Skipping {audio_path.name} (already transcribed)")
                transcript_paths.append(output_path)
                continue
            
            try:
                # Transcribe
                text = self.transcribe_file(audio_path)
                
                # Save
                output_path.write_text(text, encoding="utf-8")
                transcript_paths.append(output_path)
                
                logger.info(f"  ✓ Saved to: {output_path}")
                
            except Exception as e:
                logger.error(f"Failed to transcribe {audio_path.name}: {e}")
                continue
        
        logger.info(f"Transcription complete: {len(transcript_paths)} files")
        return transcript_paths


def transcribe_batch(
    audio_folder: Path,
    output_folder: Path,
    model_size: str = "medium",
    audio_files: Optional[List[Path]] = None
) -> List[Path]:
    """
    Convenience function to transcribe all audio files.
    
    Args:
        audio_folder: Folder with audio files
        output_folder: Folder for transcripts
        model_size: Whisper model size
        audio_files: Optional specific files to transcribe
        
    Returns:
        List of transcript file paths
    """
    transcriber = Transcriber(model_size=model_size)
    return transcriber.transcribe_folder(audio_folder, output_folder, audio_files)
