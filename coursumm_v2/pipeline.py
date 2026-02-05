"""Main pipeline orchestration."""

import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .audio import extract_audio_batch
from .transcribe import transcribe_batch
from .generate import generate_notes_batch
from .format_word import create_compiled_document, create_individual_documents
from .config import Config

logger = logging.getLogger(__name__)


class Pipeline:
    """Main CourseSumm v2 pipeline."""
    
    def __init__(self, config: Config):
        self.config = config
        self.stats = {
            "start_time": None,
            "end_time": None,
            "files_processed": 0,
            "audio_extracted": 0,
            "transcripts_created": 0,
            "notes_generated": 0,
            "documents_created": 0
        }
    
    def run(
        self,
        input_folder: Path,
        output_folder: Path,
        course_title: str = "Course Summary",
        skip_audio: bool = False,
        skip_transcription: bool = False,
        skip_generation: bool = False
    ):
        """
        Run the complete pipeline.
        
        Args:
            input_folder: Folder with video/audio files or transcripts
            output_folder: Output folder for all generated content
            course_title: Title of the course
            skip_audio: Skip audio extraction (use existing MP3s)
            skip_transcription: Skip transcription (use existing transcripts)
            skip_generation: Skip generation (use existing notes data)
        """
        self.stats["start_time"] = datetime.now()
        
        logger.info("=" * 60)
        logger.info("CourseSumm v2 Pipeline - Phase 1 MVP")
        logger.info("=" * 60)
        logger.info(f"Input: {input_folder}")
        logger.info(f"Output: {output_folder}")
        logger.info(f"Course: {course_title}")
        logger.info("=" * 60)
        
        # Create output structure
        audio_folder = output_folder / "audio"
        transcripts_folder = output_folder / "transcripts"
        notes_folder = output_folder / "notes"
        docs_folder = output_folder / "documents"
        chapters_folder = docs_folder / "chapters"
        
        for folder in [audio_folder, transcripts_folder, notes_folder, docs_folder, chapters_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Audio Extraction (if needed)
        audio_files = []
        if not skip_audio:
            logger.info("\n[STEP 1] Audio Extraction")
            logger.info("-" * 60)
            audio_files = extract_audio_batch(input_folder, audio_folder)
            self.stats["audio_extracted"] = len(audio_files)
            logger.info(f"✓ Extracted/found {len(audio_files)} audio files")
        else:
            logger.info("\n[STEP 1] Skipping audio extraction")
            # Use existing audio files
            audio_files = sorted([
                f for f in audio_folder.iterdir()
                if f.suffix.lower() in {".mp3", ".wav", ".m4a"}
            ])
            logger.info(f"Found {len(audio_files)} existing audio files")
        
        # Step 2: Transcription
        transcript_files = []
        if not skip_transcription:
            logger.info("\n[STEP 2] Transcription")
            logger.info("-" * 60)
            transcript_files = transcribe_batch(
                audio_folder,
                transcripts_folder,
                model_size=self.config.whisper_model,
                audio_files=audio_files if audio_files else None
            )
            self.stats["transcripts_created"] = len(transcript_files)
            logger.info(f"✓ Created {len(transcript_files)} transcripts")
        else:
            logger.info("\n[STEP 2] Skipping transcription")
            # Use existing transcripts
            transcript_files = sorted([
                f for f in transcripts_folder.iterdir()
                if f.suffix.lower() == ".txt"
            ])
            logger.info(f"Found {len(transcript_files)} existing transcripts")
        
        if not transcript_files:
            logger.error("No transcripts available. Cannot proceed.")
            return
        
        # Step 3: Content Generation
        notes_list = []
        if not skip_generation:
            logger.info("\n[STEP 3] Content Generation")
            logger.info("-" * 60)
            notes_list = generate_notes_batch(
                transcript_files,
                notes_folder,
                provider=self.config.llm_provider,
                model=self.config.llm_model,
                api_key=self.config.openai_api_key if self.config.llm_provider == "openai" 
                       else self.config.anthropic_api_key
            )
            self.stats["notes_generated"] = len(notes_list)
            logger.info(f"✓ Generated notes for {len(notes_list)} lectures")
        else:
            logger.info("\n[STEP 3] Skipping generation")
            # Load existing notes
            import json
            notes_list = []
            for json_file in sorted(notes_folder.glob("*_notes.json")):
                with open(json_file) as f:
                    notes_data = json.load(f)
                # Find corresponding transcript filename
                base_name = json_file.stem.replace("_notes", "")
                filename = f"{base_name}.txt"
                notes_list.append((filename, notes_data))
            logger.info(f"Loaded {len(notes_list)} existing note sets")
        
        if not notes_list:
            logger.error("No notes data available. Cannot create documents.")
            return
        
        # Step 4: Document Formatting
        logger.info("\n[STEP 4] Document Formatting")
        logger.info("-" * 60)
        
        # Create compiled document
        compiled_path = docs_folder / f"{course_title.replace(' ', '_')}_Complete.docx"
        create_compiled_document(
            notes_list,
            compiled_path,
            course_title=course_title,
            subtitle="Private Study Notes",
            author="CourseSumm v2",
            include_cover=True,
            include_toc=False  # Will add in Phase 2
        )
        logger.info(f"✓ Created compiled document: {compiled_path.name}")
        
        # Create individual chapter documents
        individual_paths = create_individual_documents(
            notes_list,
            chapters_folder,
            course_title=course_title
        )
        logger.info(f"✓ Created {len(individual_paths)} individual chapter documents")
        
        self.stats["documents_created"] = 1 + len(individual_paths)
        
        # Summary
        self.stats["end_time"] = datetime.now()
        duration = self.stats["end_time"] - self.stats["start_time"]
        
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Duration: {duration}")
        logger.info(f"Audio files: {self.stats['audio_extracted']}")
        logger.info(f"Transcripts: {self.stats['transcripts_created']}")
        logger.info(f"Notes generated: {self.stats['notes_generated']}")
        logger.info(f"Documents created: {self.stats['documents_created']}")
        logger.info("\nOutput locations:")
        logger.info(f"  Transcripts: {transcripts_folder}")
        logger.info(f"  Notes: {notes_folder}")
        logger.info(f"  Compiled: {compiled_path}")
        logger.info(f"  Chapters: {chapters_folder}")
        logger.info("=" * 60)


def run_pipeline(
    input_folder: Path,
    output_folder: Path,
    config: Optional[Config] = None,
    course_title: str = "Course Summary",
    **kwargs
) -> Pipeline:
    """
    Convenience function to run the pipeline.
    
    Args:
        input_folder: Folder with source files
        output_folder: Output folder
        config: Configuration object (creates default if None)
        course_title: Course title
        **kwargs: Additional arguments for pipeline.run()
        
    Returns:
        Pipeline instance with stats
    """
    if config is None:
        from .config import get_config
        config = get_config()
    
    pipeline = Pipeline(config)
    pipeline.run(input_folder, output_folder, course_title, **kwargs)
    return pipeline
