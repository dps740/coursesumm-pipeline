"""Argument primitive extraction using LLM."""

import json
from typing import List
import uuid

from coursumm.models import (
    TranscriptChunk, LecturePrimitives,
    Claim, Premise, Definition, Objection, Example
)
from coursumm.utils.llm import call_llm, parse_json_response


EXTRACTION_PROMPT = """You are analyzing a philosophy course transcript to extract "argument primitives" - the abstract building blocks of the philosophical discussion.

For this chunk of transcript, extract:

1. **Claims**: Main philosophical positions or theses being stated
2. **Premises**: Reasons given to support claims
3. **Definitions**: Key terms being defined or distinguished
4. **Objections**: Counterarguments or challenges to positions
5. **Examples**: Thought experiments or examples (give a generic label, NOT the verbatim text)

Important:
- Extract the ABSTRACT idea, not the exact wording
- For examples, give a short descriptive name, not the full story
- Each primitive should be a standalone concept
- Include source references so we can trace back

Return JSON:
{{
    "claims": [
        {{"text": "abstract statement of the claim", "source_hint": "what they were discussing"}}
    ],
    "premises": [
        {{"text": "abstract statement of premise", "supports": "which claim it supports (if clear)"}}
    ],
    "definitions": [
        {{"term": "the term", "definition": "the definition"}}
    ],
    "objections": [
        {{"text": "the objection", "targets": "what it objects to (if clear)"}}
    ],
    "examples": [
        {{"name": "short name like 'Twin Earth' or 'Chinese Room'", "description": "1 sentence description", "illustrates": "what point it makes"}}
    ]
}}

TRANSCRIPT CHUNK:
{chunk_text}

Return ONLY valid JSON."""


async def extract_primitives_from_chunk(chunk: TranscriptChunk) -> dict:
    """Extract argument primitives from a single chunk."""
    response = await call_llm(
        EXTRACTION_PROMPT.format(chunk_text=chunk.text),
        json_response=True,
        temperature=0.2,
    )
    
    return parse_json_response(response)


async def extract_lecture_primitives(chunks: List[TranscriptChunk]) -> LecturePrimitives:
    """
    Extract all primitives from chunks belonging to one lecture.
    
    Args:
        chunks: All chunks from a single lecture
        
    Returns:
        LecturePrimitives containing all extracted primitives
    """
    if not chunks:
        raise ValueError("No chunks provided")
    
    lecture_id = chunks[0].lecture_id
    
    all_claims = []
    all_premises = []
    all_definitions = []
    all_objections = []
    all_examples = []
    
    for chunk in chunks:
        try:
            extracted = await extract_primitives_from_chunk(chunk)
            
            # Process claims
            for c in extracted.get("claims", []):
                all_claims.append(Claim(
                    id=f"{chunk.chunk_id}_claim_{uuid.uuid4().hex[:8]}",
                    text=c.get("text", ""),
                    source_chunk_id=chunk.chunk_id,
                ))
            
            # Process premises
            for p in extracted.get("premises", []):
                all_premises.append(Premise(
                    id=f"{chunk.chunk_id}_premise_{uuid.uuid4().hex[:8]}",
                    text=p.get("text", ""),
                    supports_claim_id=p.get("supports"),
                    source_chunk_id=chunk.chunk_id,
                ))
            
            # Process definitions
            for d in extracted.get("definitions", []):
                all_definitions.append(Definition(
                    id=f"{chunk.chunk_id}_def_{uuid.uuid4().hex[:8]}",
                    term=d.get("term", ""),
                    definition=d.get("definition", ""),
                    source_chunk_id=chunk.chunk_id,
                ))
            
            # Process objections
            for o in extracted.get("objections", []):
                all_objections.append(Objection(
                    id=f"{chunk.chunk_id}_obj_{uuid.uuid4().hex[:8]}",
                    text=o.get("text", ""),
                    targets_claim_id=o.get("targets"),
                    source_chunk_id=chunk.chunk_id,
                ))
            
            # Process examples
            for e in extracted.get("examples", []):
                all_examples.append(Example(
                    id=f"{chunk.chunk_id}_ex_{uuid.uuid4().hex[:8]}",
                    name=e.get("name", ""),
                    description=e.get("description", ""),
                    illustrates=e.get("illustrates", ""),
                    source_chunk_id=chunk.chunk_id,
                ))
                
        except Exception as e:
            print(f"Warning: Failed to extract from {chunk.chunk_id}: {e}")
            continue
    
    return LecturePrimitives(
        lecture_id=lecture_id,
        claims=all_claims,
        premises=all_premises,
        definitions=all_definitions,
        objections=all_objections,
        examples=all_examples,
    )
