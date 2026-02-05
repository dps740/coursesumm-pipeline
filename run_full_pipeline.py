#!/usr/bin/env python3
"""
CourseSumm v2 - Full Pipeline Runner

Runs the complete pipeline with all phases:
- Phase 1: Audio → Transcripts → Private Notes
- Phase 2: Professional formatting with covers
- Phase 3: Public companions (V1, V2, V3)
- Phase 4: Available via Gradio UI (run gradio_app.py)
"""

import argparse
import os
import sys
from pathlib import Path
import logging

# Add coursumm_v2 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coursumm_v2.config import Config
from coursumm_v2.pipeline import Pipeline
from coursumm_v2.generate import ContentGenerator
from coursumm_v2.companion_generator import generate_all_companions
from coursumm_v2.companion_formatter import format_all_companions_to_word
from coursumm_v2.cover_generator import CoverGenerator
from coursumm_v2.enhanced_formatter import format_enhanced_document


def setup_logging(verbose=False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('coursumm_full.log'),
            logging.StreamHandler()
        ]
    )


def main():
    parser = argparse.ArgumentParser(
        description='CourseSumm v2 - Complete Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process audio files to all outputs
  python run_full_pipeline.py ./audio ./output \\
      --title "Philosophy Course" \\
      --author "Prof. David Johnson" \\
      --companions all
  
  # Process existing transcripts only
  python run_full_pipeline.py ./transcripts ./output \\
      --title "Philosophy" \\
      --skip-audio --skip-transcription \\
      --companions v1,v2
  
  # Private notes only (Phase 1)
  python run_full_pipeline.py ./audio ./output \\
      --title "Philosophy" \\
      --companions private
        """
    )
    
    # Required arguments
    parser.add_argument('input_folder', help='Input folder (audio/video or transcripts)')
    parser.add_argument('output_folder', help='Output folder')
    
    # Course metadata
    parser.add_argument('--title', default='Course Summary', help='Course title')
    parser.add_argument('--author', help='Author/instructor name')
    
    # Companion types
    parser.add_argument('--companions', default='private',
                       help='Companion types: private,v1,v2,v3,all (comma-separated)')
    
    # LLM options
    parser.add_argument('--provider', choices=['openai', 'anthropic'],
                       default='openai', help='LLM provider')
    parser.add_argument('--model', default='gpt-4', help='LLM model')
    
    # Whisper options
    parser.add_argument('--whisper-model', 
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       default='medium', help='Whisper model size')
    
    # Processing options
    parser.add_argument('--skip-audio', action='store_true',
                       help='Skip audio extraction')
    parser.add_argument('--skip-transcription', action='store_true',
                       help='Skip transcription')
    parser.add_argument('--skip-generation', action='store_true',
                       help='Skip LLM generation')
    
    # Cover options
    parser.add_argument('--cover-style',
                       choices=['blue_gradient', 'purple_elegant', 'green_modern', 
                               'red_bold', 'teal_professional'],
                       default='blue_gradient',
                       help='Cover design style')
    
    # Output options
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Parse companion types
    companions_str = args.companions.lower()
    if companions_str == 'all':
        companions = {'private', 'v1', 'v2', 'v3'}
    else:
        companions = set(companions_str.split(','))
    
    logger.info(f"Starting CourseSumm v2 pipeline")
    logger.info(f"Input: {args.input_folder}")
    logger.info(f"Output: {args.output_folder}")
    logger.info(f"Companions: {companions}")
    
    # Validate inputs
    if not os.path.exists(args.input_folder):
        logger.error(f"Input folder does not exist: {args.input_folder}")
        sys.exit(1)
    
    # Create output folder
    os.makedirs(args.output_folder, exist_ok=True)
    
    # Initialize config
    config = Config()
    config.provider = args.provider
    config.model = args.model
    config.whisper_model = args.whisper_model
    
    # Initialize content generator
    content_generator = ContentGenerator(provider=args.provider, model=args.model)
    
    # Phase 1: Core Pipeline (if private notes requested)
    if 'private' in companions:
        logger.info("\n" + "="*60)
        logger.info("PHASE 1: Core Pipeline - Private Notes")
        logger.info("="*60)
        
        pipeline = Pipeline(config, args.input_folder, args.output_folder, args.title)
        
        if not args.skip_audio:
            logger.info("Step 1: Extracting audio...")
            pipeline.process_audio()
        
        if not args.skip_transcription:
            logger.info("Step 2: Transcribing (this may take a while)...")
            pipeline.process_transcription()
        
        if not args.skip_generation:
            logger.info("Step 3: Generating private notes...")
            pipeline.process_generation()
        
        logger.info("Step 4: Formatting Word documents...")
        pipeline.process_word_formatting()
        
        logger.info("✅ Phase 1 complete: Private notes generated")
    
    # Phase 2: Professional Formatting with Covers
    logger.info("\n" + "="*60)
    logger.info("PHASE 2: Professional Formatting & Covers")
    logger.info("="*60)
    
    logger.info("Generating book covers...")
    cover_gen = CoverGenerator()
    covers_dir = os.path.join(args.output_folder, 'covers')
    cover_paths = cover_gen.generate_all_covers(
        args.title,
        args.author,
        covers_dir
    )
    
    logger.info(f"✅ Phase 2 complete: Covers generated in {covers_dir}")
    
    # Phase 3: Public Companions
    if any(comp in companions for comp in ['v1', 'v2', 'v3']):
        logger.info("\n" + "="*60)
        logger.info("PHASE 3: Public Companions")
        logger.info("="*60)
        
        transcripts_dir = os.path.join(args.output_folder, 'transcripts')
        
        if not os.path.exists(transcripts_dir):
            logger.error(f"Transcripts directory not found: {transcripts_dir}")
            logger.error("Run without --skip-transcription first")
            sys.exit(1)
        
        companions_dir = os.path.join(args.output_folder, 'companions')
        
        logger.info("Generating companion content (this may take a while)...")
        companions_data = generate_all_companions(
            transcripts_dir,
            companions_dir,
            args.title,
            content_generator
        )
        
        logger.info("Formatting companions to Word documents...")
        docs_dir = os.path.join(args.output_folder, 'documents')
        
        word_docs = format_all_companions_to_word(
            companions_data,
            args.title,
            docs_dir,
            args.author,
            cover_paths
        )
        
        logger.info(f"✅ Phase 3 complete: Public companions generated")
        for comp_type, doc_path in word_docs.items():
            logger.info(f"  - {comp_type}: {doc_path}")
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("🎉 PIPELINE COMPLETE!")
    logger.info("="*60)
    logger.info(f"Output directory: {args.output_folder}")
    logger.info(f"\nGenerated companions: {', '.join(companions)}")
    logger.info(f"\nNext steps:")
    logger.info(f"  1. Review Word documents in {os.path.join(args.output_folder, 'documents')}")
    logger.info(f"  2. Check covers in {covers_dir}")
    logger.info(f"  3. Convert to ebook format if needed")


if __name__ == '__main__':
    main()
