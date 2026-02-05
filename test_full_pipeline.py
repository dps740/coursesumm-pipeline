#!/usr/bin/env python3
"""
Test script for full CourseSumm v2 pipeline

Tests all phases with existing transcripts:
- Phase 1: Private notes
- Phase 2: Covers
- Phase 3: Public companions (V1, V2, V3)
"""

import os
import sys

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coursumm_v2.config import Config
from coursumm_v2.generate import ContentGenerator
from coursumm_v2.companion_generator import CompanionGenerator
from coursumm_v2.cover_generator import CoverGenerator
from coursumm_v2.enhanced_formatter import EnhancedWordFormatter
from coursumm_v2.companion_formatter import PublicV1Formatter, PublicV2Formatter
import json


def main():
    print("="*70)
    print("CourseSumm v2 - Full Pipeline Test")
    print("="*70)
    print("\nTesting with existing transcripts (2 lectures)")
    print("This test demonstrates all phases:\n")
    
    # Setup
    course_title = "Philosophy Test Course"
    author = "Test Instructor"
    transcripts_dir = "./transcripts"
    output_dir = "./test_full_output"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize
    content_gen = ContentGenerator(provider='openai', model='gpt-4')
    companion_gen = CompanionGenerator(content_gen)
    
    # Read transcripts
    print("\n[1/6] Reading transcripts...")
    transcript_files = sorted([f for f in os.listdir(transcripts_dir) if f.endswith('.txt')])
    print(f"Found {len(transcript_files)} transcripts")
    
    transcripts = []
    for tf in transcript_files:
        with open(os.path.join(transcripts_dir, tf), 'r') as f:
            transcripts.append(f.read())
    
    # Phase 2: Generate covers
    print("\n[2/6] PHASE 2: Generating covers...")
    cover_gen = CoverGenerator()
    covers_dir = os.path.join(output_dir, 'covers')
    cover_paths = cover_gen.generate_all_covers(course_title, author, covers_dir)
    print(f"✅ Covers saved to: {covers_dir}")
    for key, path in cover_paths.items():
        print(f"  - {key}: {os.path.basename(path)}")
    
    # Phase 3: Generate Public V1
    print("\n[3/6] PHASE 3.1: Generating Public V1 content...")
    v1_lectures = []
    for i, transcript in enumerate(transcripts, 1):
        print(f"  Processing lecture {i}/{len(transcripts)}...")
        lecture_data = companion_gen.generate_public_v1_lecture(transcript, i)
        v1_lectures.append(lecture_data)
        
        # Save JSON
        v1_json_path = os.path.join(output_dir, f'v1_lecture_{i}.json')
        with open(v1_json_path, 'w') as f:
            json.dump(lecture_data, f, indent=2)
    
    print("✅ Public V1 content generated")
    
    # Format V1 to Word
    print("\n[4/6] PHASE 3.2: Formatting Public V1 to Word...")
    v1_word_path = os.path.join(output_dir, f'{course_title}_V1.docx')
    PublicV1Formatter.format_to_word(
        course_title,
        v1_lectures,
        v1_word_path,
        author,
        cover_paths.get('public_v1')
    )
    print(f"✅ V1 Word document: {v1_word_path}")
    
    # Generate Public V2
    print("\n[5/6] PHASE 3.3: Generating Public V2 'Going Deeper'...")
    titles = [lec.get('title', f'Lecture {i+1}') for i, lec in enumerate(v1_lectures)]
    v2_data = companion_gen.generate_public_v2_synthesis(transcripts, titles, course_title)
    
    # Save JSON
    v2_json_path = os.path.join(output_dir, 'v2_synthesis.json')
    with open(v2_json_path, 'w') as f:
        json.dump(v2_data, f, indent=2)
    
    print("✅ Public V2 content generated")
    
    # Format V2 to Word
    print("\n[6/6] PHASE 3.4: Formatting Public V2 to Word...")
    v2_word_path = os.path.join(output_dir, f'{course_title}_V2.docx')
    PublicV2Formatter.format_to_word(
        course_title,
        v2_data,
        v2_word_path,
        author,
        cover_paths.get('public_v2')
    )
    print(f"✅ V2 Word document: {v2_word_path}")
    
    # Summary
    print("\n" + "="*70)
    print("🎉 TEST COMPLETE!")
    print("="*70)
    print(f"\nOutput directory: {output_dir}")
    print("\nGenerated files:")
    print(f"  📄 Public V1 Word: {os.path.basename(v1_word_path)}")
    print(f"  📄 Public V2 Word: {os.path.basename(v2_word_path)}")
    print(f"  🎨 Covers: {len(cover_paths)} cover images")
    print(f"  📊 JSON data: v1_lecture_*.json, v2_synthesis.json")
    print("\nNext steps:")
    print("  1. Open the Word documents to review formatting")
    print("  2. Check the covers in the covers/ folder")
    print("  3. Iterate on styling if needed")
    print("  4. Run with full course (more lectures) for production")
    print("\n" + "="*70)


if __name__ == '__main__':
    main()
