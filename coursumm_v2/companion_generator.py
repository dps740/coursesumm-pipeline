"""
Companion Generator for CourseSumm v2 - Phase 3

Generates different types of course companions:
- Private Notes (lecture-by-lecture, detailed) - Phase 1
- Public V1: Lecture Companion (book format, sellable)
- Public V2: Going Deeper (post-course synthesis, thematic)
- Public V3: Complete Companion (V1 + V2 combined)
"""

import json
import os
from typing import List, Dict, Any
from pathlib import Path
from .generate import ContentGenerator


class CompanionGenerator:
    """Generate different types of course companions"""
    
    def __init__(self, content_generator: ContentGenerator):
        """
        Initialize companion generator
        
        Args:
            content_generator: Content generator instance
        """
        self.generator = content_generator
    
    def generate_public_v1_lecture(self, transcript: str, lecture_num: int) -> Dict[str, Any]:
        """
        Generate Public V1 companion content for a single lecture
        
        Public V1 is a sellable lecture-by-lecture companion - more accessible
        than private notes, focused on key insights and practical takeaways.
        
        Args:
            transcript: Lecture transcript
            lecture_num: Lecture number
            
        Returns:
            Dictionary with lecture content
        """
        prompt = f"""You are creating a PUBLIC course companion that will be sold as a study guide.
This is lecture {lecture_num} of a university course.

Based on this lecture transcript, create comprehensive but accessible lecture notes.

Format your response as a JSON object with these fields:

{{
    "title": "Clear, engaging lecture title (no 'Lecture X' prefix)",
    "introduction": "2-3 sentence overview of what this lecture covers",
    "main_points": [
        {{"point": "Main point 1", "explanation": "Clear 2-3 sentence explanation"}},
        {{"point": "Main point 2", "explanation": "Clear 2-3 sentence explanation"}},
        ...5-7 main points total
    ],
    "key_concepts": [
        {{"concept": "Concept name", "definition": "Clear, accessible definition"}},
        ...3-5 concepts
    ],
    "practical_applications": [
        {{"application": "How this applies to real life or further study"}},
        ...2-3 applications
    ],
    "discussion_questions": [
        "Thought-provoking question 1",
        "Thought-provoking question 2",
        ...3-5 questions
    ],
    "further_exploration": [
        "Suggestion for deeper learning or related topics",
        ...2-3 suggestions
    ]
}}

Make it engaging, clear, and valuable for students. Focus on understanding, not just memorization.

Transcript:
{transcript[:15000]}
"""
        
        # Split prompt into system and user parts
        system_prompt = "You are creating a PUBLIC course companion that will be sold as a study guide."
        response = self.generator.generate(system_prompt, prompt)
        
        try:
            # Try to parse JSON
            data = json.loads(response)
            return data
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code block
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
                return json.loads(json_str)
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
                return json.loads(json_str)
            else:
                raise
    
    def generate_public_v2_synthesis(self, all_transcripts: List[str], 
                                     all_titles: List[str],
                                     course_title: str) -> Dict[str, Any]:
        """
        Generate Public V2 "Going Deeper" companion content
        
        This is a post-course synthesis that reorganizes content thematically,
        explores deeper implications, and makes connections beyond the lectures.
        
        Args:
            all_transcripts: List of all lecture transcripts
            all_titles: List of all lecture titles
            course_title: Course title
            
        Returns:
            Dictionary with synthesis content
        """
        # Create a course overview from all lectures
        course_overview = "\n\n".join([
            f"Lecture {i+1}: {title}\n(Excerpt): {transcript[:1000]}"
            for i, (title, transcript) in enumerate(zip(all_titles, all_transcripts))
        ])
        
        prompt = f"""You are creating a "GOING DEEPER" companion for the course: {course_title}

This is NOT lecture-by-lecture notes. This is a post-course synthesis that:
1. Identifies major themes across the entire course
2. Explores deeper implications and connections
3. Relates the course to broader intellectual contexts
4. Suggests further thinking and exploration

Based on all the lectures, create a thematic deep-dive companion.

Format your response as a JSON object:

{{
    "introduction": "Overview of what this course explored and why it matters (3-4 paragraphs)",
    "major_themes": [
        {{
            "theme": "Theme name",
            "description": "Deep exploration of this theme across the course (3-4 paragraphs)",
            "key_lectures": "Which lectures addressed this (e.g., 'Lectures 1, 5, 8-10')",
            "connections": "How this theme connects to other fields or ideas"
        }},
        ...4-6 major themes
    ],
    "deeper_questions": [
        {{
            "question": "Profound question the course raises",
            "exploration": "2-3 paragraphs exploring this question",
            "further_reading": "Suggestions for deeper exploration"
        }},
        ...3-5 questions
    ],
    "intellectual_connections": {{
        "related_fields": ["Field 1", "Field 2", ...],
        "key_thinkers": ["Thinker 1", "Thinker 2", ...],
        "modern_relevance": "How this course relates to contemporary issues (2-3 paragraphs)"
    }},
    "synthesis": "Final synthesis bringing it all together (3-4 paragraphs)"
}}

Think deeply. Make connections. Go beyond the lectures.

Course overview:
{course_overview[:20000]}
"""
        
        # For synthesis, we need more tokens
        old_max_tokens = self.generator.max_tokens
        self.generator.max_tokens = 4000
        
        system_prompt = f'You are creating a "GOING DEEPER" companion for the course: {course_title}'
        response = self.generator.generate(system_prompt, prompt)
        
        # Restore original max_tokens
        self.generator.max_tokens = old_max_tokens
        
        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code block
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
                return json.loads(json_str)
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
                return json.loads(json_str)
            else:
                raise
    
    def generate_public_v1_for_course(self, transcripts_dir: str, 
                                      output_dir: str) -> List[Dict]:
        """
        Generate Public V1 content for all lectures in a course
        
        Args:
            transcripts_dir: Directory containing transcript files
            output_dir: Output directory for JSON files
            
        Returns:
            List of lecture data dictionaries
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all transcript files
        transcript_files = sorted(Path(transcripts_dir).glob('*.txt'))
        
        all_lectures = []
        
        for i, transcript_file in enumerate(transcript_files, 1):
            print(f"Generating Public V1 for lecture {i}/{len(transcript_files)}: {transcript_file.name}")
            
            # Read transcript
            with open(transcript_file, 'r', encoding='utf-8') as f:
                transcript = f.read()
            
            # Generate content
            lecture_data = self.generate_public_v1_lecture(transcript, i)
            
            # Save JSON
            output_file = os.path.join(output_dir, f'lecture_{i:02d}_public_v1.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(lecture_data, f, indent=2, ensure_ascii=False)
            
            all_lectures.append(lecture_data)
        
        return all_lectures
    
    def generate_public_v2_for_course(self, transcripts_dir: str,
                                      titles: List[str],
                                      course_title: str,
                                      output_path: str) -> Dict:
        """
        Generate Public V2 "Going Deeper" content for entire course
        
        Args:
            transcripts_dir: Directory containing transcript files
            titles: List of lecture titles
            course_title: Course title
            output_path: Output JSON file path
            
        Returns:
            Synthesis data dictionary
        """
        print(f"Generating Public V2 'Going Deeper' synthesis for {course_title}")
        
        # Read all transcripts
        transcript_files = sorted(Path(transcripts_dir).glob('*.txt'))
        all_transcripts = []
        
        for transcript_file in transcript_files:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                all_transcripts.append(f.read())
        
        # Generate synthesis
        synthesis_data = self.generate_public_v2_synthesis(
            all_transcripts, titles, course_title
        )
        
        # Save JSON
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(synthesis_data, f, indent=2, ensure_ascii=False)
        
        return synthesis_data
    
    def create_public_v3_combined(self, v1_data: List[Dict], v2_data: Dict) -> Dict:
        """
        Combine V1 and V2 into V3 (premium product)
        
        Args:
            v1_data: List of V1 lecture data
            v2_data: V2 synthesis data
            
        Returns:
            Combined data structure
        """
        return {
            'lecture_companions': v1_data,
            'going_deeper': v2_data
        }


def generate_all_companions(transcripts_dir: str, output_base_dir: str,
                           course_title: str, content_generator: ContentGenerator) -> Dict[str, Any]:
    """
    Generate all companion types for a course
    
    Args:
        transcripts_dir: Directory with transcript files
        output_base_dir: Base output directory
        course_title: Course title
        content_generator: Content generator instance
        
    Returns:
        Dictionary with paths to all generated companions
    """
    companion_gen = CompanionGenerator(content_generator)
    
    results = {}
    
    # Public V1
    print("\n=== Generating Public V1: Lecture Companion ===")
    v1_dir = os.path.join(output_base_dir, 'public_v1')
    v1_data = companion_gen.generate_public_v1_for_course(
        transcripts_dir, v1_dir
    )
    results['public_v1'] = {
        'dir': v1_dir,
        'data': v1_data
    }
    
    # Extract titles from V1 data
    titles = [lecture.get('title', f'Lecture {i+1}') 
              for i, lecture in enumerate(v1_data)]
    
    # Public V2
    print("\n=== Generating Public V2: Going Deeper ===")
    v2_path = os.path.join(output_base_dir, 'public_v2', 'synthesis.json')
    v2_data = companion_gen.generate_public_v2_for_course(
        transcripts_dir, titles, course_title, v2_path
    )
    results['public_v2'] = {
        'path': v2_path,
        'data': v2_data
    }
    
    # Public V3 (combined)
    print("\n=== Creating Public V3: Complete Companion ===")
    v3_data = companion_gen.create_public_v3_combined(v1_data, v2_data)
    v3_path = os.path.join(output_base_dir, 'public_v3', 'complete.json')
    os.makedirs(os.path.dirname(v3_path), exist_ok=True)
    with open(v3_path, 'w', encoding='utf-8') as f:
        json.dump(v3_data, f, indent=2, ensure_ascii=False)
    
    results['public_v3'] = {
        'path': v3_path,
        'data': v3_data
    }
    
    return results
