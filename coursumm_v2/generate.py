"""Content generation using LLM (GPT/Claude)."""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generate course content using LLM."""
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize content generator.
        
        Args:
            provider: "openai" or "anthropic"
            model: Model name (gpt-4, gpt-3.5-turbo, claude-3-opus, etc.)
            api_key: API key (uses env var if None)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
        """
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate content using the configured LLM."""
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.choices[0].message.content.strip()
                
            else:  # anthropic
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                return response.content[0].text.strip()
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def generate_private_notes(self, transcript: str, lecture_title: str = "") -> Dict[str, any]:
        """
        Generate private lecture notes from transcript.
        
        Returns a structured dictionary with sections.
        """
        system_prompt = """You are an expert educational content writer.
Produce comprehensive lecture notes with these sections:

Title: <Title based on content, or use provided title>

Quote:
"<A memorable quote from the content>"

Summary:
<3-5 paragraphs (300-500 words total).
No mention of 'lecture' - present knowledge directly.
Separated by blank lines.>

Key Themes:
- <Theme 1 (3 sentences)>
- <Theme 2 (3 sentences)>
- <Theme 3 (3 sentences)>
- <Theme 4 (3 sentences)>
- <Theme 5 (3 sentences)>

Key Takeaways:
- <Takeaway 1>
  Example: <Specific example>
- <Takeaway 2>
  Example: <Specific example>
(3-5 main points with examples)

Knowledge Check Questions:
1) <Question 1>
2) <Question 2>
3) <Question 3>

Knowledge Check Answers:
1) <Answer 1>
2) <Answer 2>
3) <Answer 3>

Requirements:
- Summary must be 300-500 words
- No references to 'lecture' or 'in this lecture'
- Quote with no attribution
- 5 themes with ~3 sentences each
- Takeaways with Example sub-bullets
- 3 Q&A pairs"""

        user_prompt = f"Lecture title: {lecture_title}\n\nTranscript:\n{transcript}"
        
        logger.info(f"Generating private notes for: {lecture_title}")
        response = self.generate(system_prompt, user_prompt)
        
        # Parse the structured response
        parsed = self._parse_structured_output(response, transcript, lecture_title)
        
        # Check summary word count
        summary_text = " ".join(parsed["summary_paragraphs"])
        word_count = len(summary_text.split())
        
        if word_count < 300:
            logger.info(f"Summary too short ({word_count} words), expanding...")
            parsed = self._expand_summary(parsed, transcript)
        
        return parsed
    
    def _expand_summary(self, parsed_data: Dict, transcript: str) -> Dict:
        """Expand a too-short summary."""
        current_summary = " ".join(parsed_data["summary_paragraphs"])
        
        expansion_prompt = f"""The following summary is too short ({len(current_summary.split())} words).
Expand it to at least 300 words in 3-5 paragraphs (blank line between each).
Keep the same content, just elaborate more. No mention of 'lecture'.

Current summary:
{current_summary}

Original content for context:
{transcript[:3000]}"""

        system_prompt = "You are expanding educational content. Keep it detailed and informative."
        
        expanded = self.generate(system_prompt, expansion_prompt)
        
        # Update summary paragraphs
        paragraphs = [p.strip() for p in expanded.split("\n\n") if p.strip()]
        parsed_data["summary_paragraphs"] = paragraphs
        
        return parsed_data
    
    def _parse_structured_output(
        self,
        response: str,
        transcript: str,
        fallback_title: str
    ) -> Dict:
        """Parse the structured LLM response into sections."""
        sections = {
            "title": [],
            "quote": [],
            "summary": [],
            "themes": [],
            "key_takeaways": [],
            "knowledge_check_q": [],
            "knowledge_check_a": []
        }
        
        headers = {
            "title": "title",
            "quote": "quote",
            "summary": "summary",
            "key themes": "themes",
            "themes": "themes",
            "key takeaways": "key_takeaways",
            "knowledge check questions": "knowledge_check_q",
            "knowledge check answers": "knowledge_check_a"
        }
        
        current_section = None
        
        for line in response.splitlines():
            line_stripped = line.strip()
            lower_line = line_stripped.lower()
            
            # Check for section headers
            matched = False
            for header_key, section_key in headers.items():
                if lower_line.startswith(header_key):
                    current_section = section_key
                    matched = True
                    break
            
            if not matched and current_section and line_stripped:
                sections[current_section].append(line_stripped)
        
        # Convert summary to paragraphs
        summary_paragraphs = []
        buffer = []
        for line in sections["summary"]:
            if not line.strip():
                if buffer:
                    summary_paragraphs.append(" ".join(buffer))
                    buffer = []
            else:
                buffer.append(line.strip())
        if buffer:
            summary_paragraphs.append(" ".join(buffer))
        
        # Remove 'lecture' references
        summary_paragraphs = [
            re.sub(r'\blecture\b', '', p, flags=re.IGNORECASE)
            for p in summary_paragraphs
        ]
        
        # Clean quote (remove attribution if present)
        quote_text = " ".join(sections["quote"]).strip()
        if " - " in quote_text:
            quote_text = quote_text.split(" - ")[0].strip()
        quote_text = quote_text.strip('"')
        
        # Get title
        title = " ".join(sections["title"]).strip()
        if not title or title.lower() == "untitled":
            title = fallback_title
        
        return {
            "title": title,
            "quote": quote_text,
            "summary_paragraphs": summary_paragraphs,
            "themes": sections["themes"],
            "key_takeaways": sections["key_takeaways"],
            "knowledge_check_q": sections["knowledge_check_q"],
            "knowledge_check_a": sections["knowledge_check_a"]
        }


def generate_notes_batch(
    transcript_files: List[Path],
    output_folder: Path,
    provider: str = "openai",
    model: str = "gpt-4",
    api_key: Optional[str] = None
) -> List[Dict]:
    """
    Generate private notes for multiple transcript files.
    
    Returns:
        List of (filename, parsed_data) tuples
    """
    generator = ContentGenerator(provider=provider, model=model, api_key=api_key)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for transcript_path in transcript_files:
        logger.info(f"\nProcessing: {transcript_path.name}")
        
        # Read transcript
        transcript = transcript_path.read_text(encoding="utf-8")
        
        # Extract title from filename (e.g., "Lect01 Introduction.txt" -> "Introduction")
        title = transcript_path.stem
        match = re.match(r'^(Lect\d+\s+)(.*)', title, re.IGNORECASE)
        if match:
            title = match.group(2).strip()
        
        # Generate notes
        try:
            notes_data = generator.generate_private_notes(transcript, title)
            results.append((transcript_path.name, notes_data))
            
            # Save intermediate JSON for debugging
            import json
            json_path = output_folder / f"{transcript_path.stem}_notes.json"
            with open(json_path, "w") as f:
                json.dump(notes_data, f, indent=2)
            
            logger.info(f"  ✓ Generated notes for: {title}")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to generate notes for {transcript_path.name}: {e}")
            continue
    
    return results
