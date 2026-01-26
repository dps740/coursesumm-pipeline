"""Private lecture notes generation."""

from typing import List, Dict

from coursumm.models import TranscriptChunk, LecturePrimitives, PrivateLectureNotes
from coursumm.utils.llm import call_llm, parse_json_response


PRIVATE_NOTES_PROMPT = """You are creating detailed lecture notes for a philosophy course.

Generate comprehensive notes for this lecture based on the transcript and extracted concepts.

LECTURE: {lecture_title}

TRANSCRIPT CHUNKS:
{transcript}

EXTRACTED CONCEPTS:
Claims: {claims}
Definitions: {definitions}
Arguments/Premises: {premises}
Objections: {objections}
Examples: {examples}

Create notes with:
1. Summary bullets (5-10 key points)
2. Summary narrative (2-3 paragraphs)
3. Key arguments (structured with premises and conclusions)
4. Key definitions (term -> definition)
5. Quick quiz (5-10 questions with answers)

Return JSON:
{{
    "summary_bullets": ["point 1", "point 2", ...],
    "summary_narrative": "paragraph text...",
    "key_arguments": [
        {{"name": "argument name", "premises": ["p1", "p2"], "conclusion": "conclusion"}}
    ],
    "key_definitions": [
        {{"term": "term", "definition": "definition"}}
    ],
    "quick_quiz": [
        {{"question": "Q?", "answer": "A"}}
    ]
}}

You may closely follow the transcript since this is for PRIVATE use only.
Return ONLY valid JSON."""


async def generate_private_notes(
    lecture_id: str,
    lecture_title: str,
    chunks: List[TranscriptChunk],
    primitives: LecturePrimitives,
) -> PrivateLectureNotes:
    """
    Generate private lecture notes.
    
    Private notes can closely follow the transcript structure
    since they are for personal use only.
    """
    # Prepare transcript text
    transcript_text = "\n\n---\n\n".join([c.text for c in chunks])
    
    # Prepare primitives
    claims_text = "\n".join([f"- {c.text}" for c in primitives.claims]) or "None extracted"
    definitions_text = "\n".join([f"- {d.term}: {d.definition}" for d in primitives.definitions]) or "None extracted"
    premises_text = "\n".join([f"- {p.text}" for p in primitives.premises]) or "None extracted"
    objections_text = "\n".join([f"- {o.text}" for o in primitives.objections]) or "None extracted"
    examples_text = "\n".join([f"- {e.name}: {e.description}" for e in primitives.examples]) or "None extracted"
    
    response = await call_llm(
        PRIVATE_NOTES_PROMPT.format(
            lecture_title=lecture_title,
            transcript=transcript_text[:15000],  # Limit length
            claims=claims_text,
            definitions=definitions_text,
            premises=premises_text,
            objections=objections_text,
            examples=examples_text,
        ),
        json_response=True,
        temperature=0.3,
    )
    
    result = parse_json_response(response)
    
    return PrivateLectureNotes(
        lecture_id=lecture_id,
        lecture_title=lecture_title,
        summary_bullets=result.get("summary_bullets", []),
        summary_narrative=result.get("summary_narrative", ""),
        key_arguments=result.get("key_arguments", []),
        key_definitions=result.get("key_definitions", []),
        quick_quiz=result.get("quick_quiz", []),
    )


def format_private_notes_md(notes: PrivateLectureNotes) -> str:
    """Format private notes as Markdown."""
    lines = [
        f"# {notes.lecture_id}: {notes.lecture_title}",
        "",
        "## Summary",
        "",
    ]
    
    # Bullets
    for bullet in notes.summary_bullets:
        lines.append(f"- {bullet}")
    
    lines.extend(["", "### Narrative", "", notes.summary_narrative, ""])
    
    # Key Arguments
    lines.extend(["## Key Arguments", ""])
    for arg in notes.key_arguments:
        lines.append(f"### {arg.get('name', 'Argument')}")
        lines.append("")
        lines.append("**Premises:**")
        for p in arg.get("premises", []):
            lines.append(f"- {p}")
        lines.append("")
        lines.append(f"**Conclusion:** {arg.get('conclusion', '')}")
        lines.append("")
    
    # Key Definitions
    lines.extend(["## Key Definitions", ""])
    for defn in notes.key_definitions:
        lines.append(f"- **{defn.get('term', '')}**: {defn.get('definition', '')}")
    lines.append("")
    
    # Quick Quiz
    lines.extend(["## Quick Quiz", ""])
    for i, qa in enumerate(notes.quick_quiz, 1):
        lines.append(f"**Q{i}:** {qa.get('question', '')}")
        lines.append("")
        lines.append(f"<details><summary>Answer</summary>{qa.get('answer', '')}</details>")
        lines.append("")
    
    return "\n".join(lines)
