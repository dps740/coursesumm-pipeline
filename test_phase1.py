#!/usr/bin/env python3
"""
Quick test script for Phase 1 MVP.
Tests with the 2 existing transcripts (skips audio and transcription).
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from coursumm_v2.config import Config, set_config
from coursumm_v2.pipeline import run_pipeline
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def main():
    print("=" * 60)
    print("CourseSumm v2 - Phase 1 Quick Test")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: OPENAI_API_KEY not set!")
        print("Set it with: export OPENAI_API_KEY='sk-...'")
        sys.exit(1)
    
    # Paths
    project_dir = Path(__file__).parent
    transcripts_dir = project_dir / "transcripts"
    output_dir = project_dir / "test_output"
    
    print(f"\nTranscripts: {transcripts_dir}")
    print(f"Output: {output_dir}")
    
    # Check transcripts exist
    transcript_files = list(transcripts_dir.glob("*.txt"))
    if not transcript_files:
        print(f"\n❌ ERROR: No transcripts found in {transcripts_dir}")
        sys.exit(1)
    
    print(f"Found {len(transcript_files)} transcripts")
    
    # Create config
    config = Config()
    config.llm_provider = "openai"
    config.llm_model = "gpt-3.5-turbo"  # Use cheaper model for testing
    config.whisper_model = "medium"
    set_config(config)
    
    print(f"\nLLM: {config.llm_model}")
    print("\nStarting pipeline...\n")
    
    # Run pipeline (skip audio and transcription)
    try:
        run_pipeline(
            input_folder=transcripts_dir,
            output_folder=output_dir,
            config=config,
            course_title="Philosophy Test",
            skip_audio=True,
            skip_transcription=True,
            skip_generation=False
        )
        
        print("\n" + "=" * 60)
        print("✅ TEST PASSED!")
        print("=" * 60)
        print(f"\nCheck output in: {output_dir}")
        print("  - notes/ - Generated JSON notes")
        print("  - documents/Philosophy_Test_Complete.docx - Compiled document")
        print("  - documents/chapters/ - Individual chapters")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
