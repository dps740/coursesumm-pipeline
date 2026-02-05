#!/usr/bin/env python3
"""
CourseSumm v2 - Phase 1 MVP Runner

Usage:
    python run_phase1.py <input_folder> <output_folder> --title "Course Title"
    
Example:
    python run_phase1.py ~/transcripts ~/output --title "Philosophy"
"""

import sys
import argparse
import logging
from pathlib import Path

from coursumm_v2.config import Config, set_config
from coursumm_v2.pipeline import run_pipeline


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('coursumm_v2.log', mode='w')
        ]
    )


def main():
    parser = argparse.ArgumentParser(
        description="CourseSumm v2 - Phase 1 MVP Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process audio/video files
  python run_phase1.py ./audio ./output --title "Philosophy"
  
  # Process existing transcripts
  python run_phase1.py ./transcripts ./output --title "Philosophy" --skip-audio --skip-transcription
  
  # Use GPT-3.5 (faster, cheaper)
  python run_phase1.py ./audio ./output --title "Philosophy" --model gpt-3.5-turbo
        """
    )
    
    parser.add_argument(
        'input_folder',
        type=Path,
        help='Input folder (audio/video files or transcripts)'
    )
    
    parser.add_argument(
        'output_folder',
        type=Path,
        help='Output folder for all generated content'
    )
    
    parser.add_argument(
        '--title',
        type=str,
        default='Course Summary',
        help='Course title (default: "Course Summary")'
    )
    
    parser.add_argument(
        '--provider',
        type=str,
        choices=['openai', 'anthropic'],
        default='openai',
        help='LLM provider (default: openai)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4',
        help='LLM model (default: gpt-4)'
    )
    
    parser.add_argument(
        '--whisper-model',
        type=str,
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='medium',
        help='Whisper model size (default: medium)'
    )
    
    parser.add_argument(
        '--skip-audio',
        action='store_true',
        help='Skip audio extraction (use existing MP3s)'
    )
    
    parser.add_argument(
        '--skip-transcription',
        action='store_true',
        help='Skip transcription (use existing transcripts)'
    )
    
    parser.add_argument(
        '--skip-generation',
        action='store_true',
        help='Skip generation (use existing notes data)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate paths
    if not args.input_folder.exists():
        print(f"Error: Input folder not found: {args.input_folder}")
        sys.exit(1)
    
    # Create config
    config = Config()
    config.llm_provider = args.provider
    config.llm_model = args.model
    config.whisper_model = args.whisper_model
    set_config(config)
    
    # Run pipeline
    try:
        run_pipeline(
            input_folder=args.input_folder,
            output_folder=args.output_folder,
            config=config,
            course_title=args.title,
            skip_audio=args.skip_audio,
            skip_transcription=args.skip_transcription,
            skip_generation=args.skip_generation
        )
        print("\n✅ Pipeline completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logging.exception("Pipeline failed")
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
