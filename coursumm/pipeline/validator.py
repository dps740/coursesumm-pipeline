"""Public safety validator."""

import json
from datetime import datetime
from typing import List, Dict
import hashlib

from coursumm.models import (
    TranscriptChunk, PublicChapter, 
    ValidationStatus, SectionValidation, TraceReport
)
from coursumm.utils.similarity import SafetyChecker
from coursumm.config import get_config


def validate_public_chapter(
    chapter: PublicChapter,
    source_chunks: List[TranscriptChunk],
    lecture_titles: List[str],
) -> SectionValidation:
    """
    Validate a public chapter against source material.
    
    Checks:
    1. No forbidden strings (lecture references)
    2. N-gram overlap below threshold
    3. Cosine similarity below threshold
    4. No long consecutive word sequences
    """
    config = get_config()
    safety_config = config.public_safety
    
    # Create safety checker
    chunk_texts = [c.text for c in source_chunks]
    checker = SafetyChecker(
        source_chunks=chunk_texts,
        lecture_titles=lecture_titles,
        max_ngram_overlap=safety_config.max_ngram_overlap,
        max_cosine_similarity=safety_config.max_cosine_similarity,
        max_consecutive_words=safety_config.max_consecutive_words,
    )
    
    # Collect all text from the chapter
    chapter_text = _extract_chapter_text(chapter)
    
    # Run safety check
    result = checker.check(chapter_text)
    
    # Map chunk indices to IDs
    top_chunks = []
    if result["most_similar_chunk_idx"] >= 0 and result["most_similar_chunk_idx"] < len(source_chunks):
        top_chunks.append(source_chunks[result["most_similar_chunk_idx"]].chunk_id)
    
    # Determine status
    if result["passed"]:
        status = ValidationStatus.PASS
    else:
        status = ValidationStatus.FAIL
    
    return SectionValidation(
        section_id=chapter.chapter_id,
        status=status,
        max_similarity=result["cosine_similarity"],
        max_ngram_overlap=result["ngram_overlap"],
        top_matching_chunks=top_chunks,
        forbidden_strings_found=result["forbidden_found"],
        issues=result["issues"],
    )


def _extract_chapter_text(chapter: PublicChapter) -> str:
    """Extract all text content from a chapter for validation."""
    parts = [
        chapter.title,
        chapter.landscape,
        chapter.decision_framework,
    ]
    
    # Add arguments
    for arg in chapter.strongest_arguments:
        parts.append(arg.get("argument", ""))
        parts.extend(arg.get("premises", []))
        parts.append(arg.get("conclusion", ""))
    
    # Add objections
    for obj in chapter.strongest_objections:
        parts.append(obj.get("challenge", ""))
        parts.append(obj.get("possible_response", ""))
    
    # Add argument map
    parts.append(chapter.argument_map.central_claim)
    parts.extend(chapter.argument_map.premises)
    parts.extend(chapter.argument_map.assumptions)
    for obj in chapter.argument_map.objections:
        parts.append(obj.get("objection", ""))
        parts.append(obj.get("reply", ""))
    
    # Add exercises
    for q in chapter.exercises.retrieval_questions:
        parts.append(q.get("question", ""))
        parts.append(q.get("answer", ""))
    parts.extend(chapter.exercises.position_building_prompts)
    parts.extend(chapter.exercises.argument_reconstruction)
    parts.extend(chapter.exercises.counterexample_generation)
    
    return "\n".join([p for p in parts if p])


def generate_trace_report(
    chapters: List[PublicChapter],
    validations: List[SectionValidation],
    config_dict: Dict,
) -> TraceReport:
    """
    Generate a trace report for the public output.
    
    This provides an audit trail for verification.
    """
    # Calculate config hash
    config_str = json.dumps(config_dict, sort_keys=True)
    config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    # Count statuses
    passed = sum(1 for v in validations if v.status == ValidationStatus.PASS)
    failed = sum(1 for v in validations if v.status == ValidationStatus.FAIL)
    manual = sum(1 for v in validations if v.status == ValidationStatus.NEEDS_MANUAL_REWRITE)
    
    # Overall status
    if failed > 0:
        overall = ValidationStatus.FAIL
    elif manual > 0:
        overall = ValidationStatus.NEEDS_MANUAL_REWRITE
    else:
        overall = ValidationStatus.PASS
    
    return TraceReport(
        generated_at=datetime.utcnow().isoformat(),
        config_hash=config_hash,
        section_validations=validations,
        overall_status=overall,
        sections_passed=passed,
        sections_failed=failed,
        sections_manual=manual,
    )


def format_trace_report_json(report: TraceReport) -> str:
    """Format trace report as JSON."""
    return report.model_dump_json(indent=2)
