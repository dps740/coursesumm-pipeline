"""Data models for CourSumm pipeline."""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from enum import Enum


class ValidationStatus(str, Enum):
    """Status of public safety validation."""
    PASS = "pass"
    FAIL = "fail"
    NEEDS_MANUAL_REWRITE = "needs_manual_rewrite"


# ============== Transcript Parsing ==============

class TranscriptChunk(BaseModel):
    """A chunk of transcript text with stable ID."""
    lecture_id: str  # e.g., "L01"
    chunk_id: str    # e.g., "L01_C001"
    text: str
    word_count: int
    start_position: int  # Character position in original


# ============== Argument Primitives ==============

class Claim(BaseModel):
    """A philosophical claim or thesis."""
    id: str
    text: str
    source_chunk_id: str


class Premise(BaseModel):
    """A premise supporting a claim."""
    id: str
    text: str
    supports_claim_id: Optional[str] = None
    source_chunk_id: str


class Definition(BaseModel):
    """A key definition or distinction."""
    id: str
    term: str
    definition: str
    source_chunk_id: str


class Objection(BaseModel):
    """An objection to a claim."""
    id: str
    text: str
    targets_claim_id: Optional[str] = None
    source_chunk_id: str


class Example(BaseModel):
    """A thought experiment or example."""
    id: str
    name: str  # Generic label, not verbatim
    description: str
    illustrates: str  # What point it illustrates
    source_chunk_id: str


class LecturePrimitives(BaseModel):
    """All primitives extracted from a lecture."""
    lecture_id: str
    claims: List[Claim] = []
    premises: List[Premise] = []
    definitions: List[Definition] = []
    objections: List[Objection] = []
    examples: List[Example] = []


# ============== Topic Clustering ==============

class TopicCluster(BaseModel):
    """A cluster of primitives around a topic."""
    topic_id: str  # e.g., "free_will"
    topic_name: str  # Human-readable name
    linked_primitives: List[str]  # Primitive IDs
    linked_lectures: List[str]  # Lecture IDs that contribute
    importance_score: float  # 0-1


class TopicMap(BaseModel):
    """Map of all topics and their linked primitives."""
    clusters: List[TopicCluster]


# ============== Private Notes ==============

class PrivateLectureNotes(BaseModel):
    """Private notes for a single lecture."""
    lecture_id: str
    lecture_title: str
    summary_bullets: List[str]
    summary_narrative: str
    key_arguments: List[Dict[str, Any]]  # Structured argument info
    key_definitions: List[Dict[str, str]]
    quick_quiz: List[Dict[str, str]]  # Question/answer pairs


# ============== Public Companion ==============

class ArgumentMap(BaseModel):
    """Visual argument map for a chapter."""
    central_claim: str
    premises: List[str]
    objections: List[Dict[str, str]]  # objection -> reply
    assumptions: List[str]


class ChapterExercises(BaseModel):
    """Exercises for a public chapter."""
    retrieval_questions: List[Dict[str, str]]  # question -> answer
    position_building_prompts: List[str]
    argument_reconstruction: List[str]
    counterexample_generation: List[str]


class PublicChapter(BaseModel):
    """A chapter in the public companion."""
    chapter_id: str
    title: str
    topic_id: str
    
    # Content sections
    landscape: str  # Overview of positions
    strongest_arguments: List[Dict[str, str]]
    strongest_objections: List[Dict[str, str]]
    decision_framework: str
    
    # Required elements
    argument_map: ArgumentMap
    exercises: ChapterExercises
    synthesis_links: List[str]  # Links to other topics
    
    # Validation
    validation_status: ValidationStatus = ValidationStatus.PASS
    validation_issues: List[str] = []


class PublicCompanion(BaseModel):
    """The complete public companion book."""
    title: str
    part1_orientation: str
    chapters: List[PublicChapter]
    part3_synthesis: str
    appendix_glossary: Dict[str, str]
    appendix_argument_patterns: List[str]
    appendix_reading_list: List[str]


# ============== Validation ==============

class ChunkSimilarity(BaseModel):
    """Similarity between generated text and a transcript chunk."""
    chunk_id: str
    similarity_score: float
    ngram_overlap: float


class SectionValidation(BaseModel):
    """Validation result for a public section."""
    section_id: str
    status: ValidationStatus
    max_similarity: float
    max_ngram_overlap: float
    top_matching_chunks: List[str]  # IDs only
    forbidden_strings_found: List[str]
    issues: List[str]


class TraceReport(BaseModel):
    """Trace report for public output audit."""
    generated_at: str
    config_hash: str
    section_validations: List[SectionValidation]
    overall_status: ValidationStatus
    sections_passed: int
    sections_failed: int
    sections_manual: int
