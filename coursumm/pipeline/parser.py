"""Transcript parsing and chunking."""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re

from coursumm.models import TranscriptChunk
from coursumm.config import get_config


def parse_transcripts(transcripts_dir: Path) -> Tuple[List[TranscriptChunk], Dict[str, str]]:
    """
    Parse all transcripts in a directory.
    
    Args:
        transcripts_dir: Directory containing transcript files (L##_title.txt)
        
    Returns:
        (list of chunks, dict of lecture_id -> lecture_title)
    """
    config = get_config()
    
    chunks = []
    lecture_titles = {}
    
    # Find all transcript files
    transcript_files = sorted(
        list(transcripts_dir.glob("L*.txt")) +
        list(transcripts_dir.glob("L*.md")) +
        list(transcripts_dir.glob("L*.docx"))
    )
    
    for filepath in transcript_files:
        lecture_id, title = _parse_filename(filepath.name)
        lecture_titles[lecture_id] = title
        
        # Read content
        if filepath.suffix == ".docx":
            text = _read_docx(filepath)
        else:
            text = filepath.read_text(encoding="utf-8")
        
        # Clean and chunk
        text = _clean_transcript(text)
        lecture_chunks = _chunk_text(
            text, 
            lecture_id,
            min_words=config.chunk_min_words,
            max_words=config.chunk_max_words,
        )
        chunks.extend(lecture_chunks)
    
    return chunks, lecture_titles


def _parse_filename(filename: str) -> Tuple[str, str]:
    """
    Extract lecture ID and title from filename.
    
    Formats:
        L01_introduction.txt -> ("L01", "introduction")
        L01.txt -> ("L01", "Lecture 1")
    """
    # Remove extension
    name = Path(filename).stem
    
    # Try to split on underscore
    parts = name.split("_", 1)
    
    lecture_id = parts[0].upper()  # e.g., "L01"
    
    if len(parts) > 1:
        title = parts[1].replace("_", " ").title()
    else:
        # Generate default title
        num = re.search(r'\d+', lecture_id)
        title = f"Lecture {num.group()}" if num else lecture_id
    
    return lecture_id, title


def _read_docx(filepath: Path) -> str:
    """Read text from a Word document."""
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n\n".join([para.text for para in doc.paragraphs])
    except ImportError:
        raise ImportError("python-docx required to read .docx files: pip install python-docx")


def _clean_transcript(text: str) -> str:
    """
    Clean transcript text.
    
    - Remove timestamps
    - Remove speaker labels (if consistent format)
    - Normalize whitespace
    """
    # Remove common timestamp formats
    # [00:00:00] or (00:00) or 00:00:00
    text = re.sub(r'\[?\(?\d{1,2}:\d{2}(:\d{2})?\)?\]?', '', text)
    
    # Remove speaker labels like "SPEAKER:" at start of lines
    text = re.sub(r'^[A-Z]+:\s*', '', text, flags=re.MULTILINE)
    
    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    return text.strip()


def _chunk_text(
    text: str,
    lecture_id: str,
    min_words: int = 300,
    max_words: int = 800,
) -> List[TranscriptChunk]:
    """
    Split text into chunks of appropriate size.
    
    Strategy:
    1. Split on paragraph boundaries
    2. Combine paragraphs until reaching target size
    3. Ensure chunks don't exceed max_words
    """
    paragraphs = text.split("\n\n")
    chunks = []
    
    current_chunk = []
    current_words = 0
    current_pos = 0
    chunk_idx = 1
    
    for para in paragraphs:
        para_words = len(para.split())
        
        # If adding this paragraph exceeds max, save current chunk
        if current_words > 0 and current_words + para_words > max_words:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append(TranscriptChunk(
                lecture_id=lecture_id,
                chunk_id=f"{lecture_id}_C{chunk_idx:03d}",
                text=chunk_text,
                word_count=current_words,
                start_position=current_pos,
            ))
            chunk_idx += 1
            current_chunk = []
            current_words = 0
            current_pos = text.find(para)
        
        current_chunk.append(para)
        current_words += para_words
        
        # If we've reached min_words and hit a good break, save
        if current_words >= min_words:
            # Look for natural break (period at end)
            if para.rstrip().endswith(('.', '?', '!')):
                chunk_text = "\n\n".join(current_chunk)
                chunks.append(TranscriptChunk(
                    lecture_id=lecture_id,
                    chunk_id=f"{lecture_id}_C{chunk_idx:03d}",
                    text=chunk_text,
                    word_count=current_words,
                    start_position=current_pos,
                ))
                chunk_idx += 1
                current_chunk = []
                current_words = 0
                current_pos = text.find(para) + len(para)
    
    # Don't forget the last chunk
    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunks.append(TranscriptChunk(
            lecture_id=lecture_id,
            chunk_id=f"{lecture_id}_C{chunk_idx:03d}",
            text=chunk_text,
            word_count=current_words,
            start_position=current_pos,
        ))
    
    return chunks
