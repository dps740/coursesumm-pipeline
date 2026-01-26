"""Public companion chapter generation from primitives."""

from typing import List, Dict
import uuid

from coursumm.models import (
    LecturePrimitives, TopicCluster, TopicMap,
    PublicChapter, ArgumentMap, ChapterExercises,
    ValidationStatus
)
from coursumm.utils.llm import call_llm, parse_json_response


# CRITICAL: This prompt receives ONLY primitives, not raw transcript
PUBLIC_CHAPTER_PROMPT = """You are writing a chapter for an independent philosophy workbook.

IMPORTANT RULES:
1. Do NOT follow any lecture structure
2. Do NOT mention lectures or lecture numbers
3. Do NOT quote source material directly
4. Write as an ORIGINAL educational workbook chapter
5. Use ONLY the philosophical concepts provided below

TOPIC: {topic_name}

PHILOSOPHICAL CONCEPTS FOR THIS TOPIC:
(These are abstract ideas extracted from various sources)

CLAIMS/THESES:
{claims}

SUPPORTING ARGUMENTS:
{premises}

KEY DEFINITIONS:
{definitions}

OBJECTIONS/COUNTERARGUMENTS:
{objections}

EXAMPLES/THOUGHT EXPERIMENTS:
{examples}

Write a comprehensive workbook chapter with:

1. **Landscape**: Overview of the different positions on this topic (2-3 paragraphs)

2. **Strongest Arguments**: Present 2-3 strongest arguments for major positions
   - Each should have clear premises and conclusions
   - Explain in your own words

3. **Strongest Objections**: Present 2-3 strongest objections
   - Explain the challenge clearly
   - Consider possible responses

4. **Decision Framework**: How should a reader think about this topic?
   - What are the key questions to ask?
   - What would you need to believe to accept each position?

5. **Argument Map**: A structured map of the central claim, premises, objections, and replies

6. **Exercises**:
   - 10 retrieval questions (with answer keys)
   - 3 position-building prompts ("What would you have to give up to believe X?")
   - 2 argument reconstruction exercises
   - 2 counterexample challenges

7. **Synthesis**: How does this topic connect to other philosophical questions?

Return JSON:
{{
    "landscape": "text...",
    "strongest_arguments": [
        {{"position": "name", "argument": "explanation", "premises": ["p1", "p2"], "conclusion": "c"}}
    ],
    "strongest_objections": [
        {{"objection": "name", "challenge": "explanation", "possible_response": "response"}}
    ],
    "decision_framework": "text...",
    "argument_map": {{
        "central_claim": "claim",
        "premises": ["p1", "p2"],
        "objections": [{{"objection": "obj", "reply": "reply"}}],
        "assumptions": ["a1", "a2"]
    }},
    "exercises": {{
        "retrieval_questions": [{{"question": "Q?", "answer": "A"}}],
        "position_building": ["prompt1", "prompt2", "prompt3"],
        "argument_reconstruction": ["exercise1", "exercise2"],
        "counterexample_challenges": ["challenge1", "challenge2"]
    }},
    "synthesis_links": ["topic1", "topic2"]
}}

Write ORIGINAL explanations. Do not paraphrase any source. 
Return ONLY valid JSON."""


async def generate_public_chapter(
    topic_cluster: TopicCluster,
    all_primitives: List[LecturePrimitives],
) -> PublicChapter:
    """
    Generate a public chapter from primitives only.
    
    CRITICAL: This function receives only abstract primitives,
    not raw transcript text. This ensures the output is transformative.
    """
    # Collect primitives for this topic
    linked_ids = set(topic_cluster.linked_primitives)
    
    claims = []
    premises = []
    definitions = []
    objections = []
    examples = []
    
    for lp in all_primitives:
        for c in lp.claims:
            if c.id in linked_ids:
                claims.append(c.text)
        for p in lp.premises:
            if p.id in linked_ids:
                premises.append(p.text)
        for d in lp.definitions:
            if d.id in linked_ids:
                definitions.append(f"{d.term}: {d.definition}")
        for o in lp.objections:
            if o.id in linked_ids:
                objections.append(o.text)
        for e in lp.examples:
            if e.id in linked_ids:
                examples.append(f"{e.name}: {e.illustrates}")
    
    # Format for prompt
    claims_text = "\n".join([f"- {c}" for c in claims]) or "No specific claims"
    premises_text = "\n".join([f"- {p}" for p in premises]) or "No specific premises"
    definitions_text = "\n".join([f"- {d}" for d in definitions]) or "No specific definitions"
    objections_text = "\n".join([f"- {o}" for o in objections]) or "No specific objections"
    examples_text = "\n".join([f"- {e}" for e in examples]) or "No specific examples"
    
    response = await call_llm(
        PUBLIC_CHAPTER_PROMPT.format(
            topic_name=topic_cluster.topic_name,
            claims=claims_text,
            premises=premises_text,
            definitions=definitions_text,
            objections=objections_text,
            examples=examples_text,
        ),
        json_response=True,
        temperature=0.4,  # Slightly more creative for original writing
    )
    
    result = parse_json_response(response)
    
    # Build ArgumentMap
    arg_map_data = result.get("argument_map", {})
    argument_map = ArgumentMap(
        central_claim=arg_map_data.get("central_claim", ""),
        premises=arg_map_data.get("premises", []),
        objections=[
            {"objection": o.get("objection", ""), "reply": o.get("reply", "")}
            for o in arg_map_data.get("objections", [])
        ],
        assumptions=arg_map_data.get("assumptions", []),
    )
    
    # Build ChapterExercises
    ex_data = result.get("exercises", {})
    exercises = ChapterExercises(
        retrieval_questions=[
            {"question": q.get("question", ""), "answer": q.get("answer", "")}
            for q in ex_data.get("retrieval_questions", [])
        ],
        position_building_prompts=ex_data.get("position_building", []),
        argument_reconstruction=ex_data.get("argument_reconstruction", []),
        counterexample_generation=ex_data.get("counterexample_challenges", []),
    )
    
    return PublicChapter(
        chapter_id=f"ch_{topic_cluster.topic_id}",
        title=topic_cluster.topic_name,
        topic_id=topic_cluster.topic_id,
        landscape=result.get("landscape", ""),
        strongest_arguments=result.get("strongest_arguments", []),
        strongest_objections=result.get("strongest_objections", []),
        decision_framework=result.get("decision_framework", ""),
        argument_map=argument_map,
        exercises=exercises,
        synthesis_links=result.get("synthesis_links", []),
        validation_status=ValidationStatus.PASS,  # Will be updated by validator
    )


def format_public_chapter_md(chapter: PublicChapter) -> str:
    """Format public chapter as Markdown."""
    lines = [
        f"# {chapter.title}",
        "",
        "## The Landscape",
        "",
        chapter.landscape,
        "",
        "## Strongest Arguments",
        "",
    ]
    
    for arg in chapter.strongest_arguments:
        lines.append(f"### {arg.get('position', 'Position')}")
        lines.append("")
        lines.append(arg.get('argument', ''))
        lines.append("")
        if arg.get('premises'):
            lines.append("**Premises:**")
            for p in arg['premises']:
                lines.append(f"- {p}")
            lines.append("")
        if arg.get('conclusion'):
            lines.append(f"**Conclusion:** {arg['conclusion']}")
            lines.append("")
    
    lines.extend(["## Strongest Objections", ""])
    for obj in chapter.strongest_objections:
        lines.append(f"### {obj.get('objection', 'Objection')}")
        lines.append("")
        lines.append(obj.get('challenge', ''))
        lines.append("")
        if obj.get('possible_response'):
            lines.append(f"**Possible Response:** {obj['possible_response']}")
            lines.append("")
    
    lines.extend([
        "## Decision Framework",
        "",
        chapter.decision_framework,
        "",
        "## Argument Map",
        "",
        f"**Central Claim:** {chapter.argument_map.central_claim}",
        "",
        "**Premises:**",
    ])
    for p in chapter.argument_map.premises:
        lines.append(f"- {p}")
    
    lines.extend(["", "**Objections and Replies:**"])
    for obj in chapter.argument_map.objections:
        lines.append(f"- *Objection:* {obj.get('objection', '')}")
        lines.append(f"  - *Reply:* {obj.get('reply', '')}")
    
    lines.extend(["", "**Assumptions:**"])
    for a in chapter.argument_map.assumptions:
        lines.append(f"- {a}")
    
    lines.extend(["", "## Exercises", "", "### Retrieval Questions", ""])
    for i, q in enumerate(chapter.exercises.retrieval_questions, 1):
        lines.append(f"**{i}.** {q.get('question', '')}")
        lines.append("")
        lines.append(f"<details><summary>Answer</summary>{q.get('answer', '')}</details>")
        lines.append("")
    
    lines.extend(["### Position-Building Prompts", ""])
    for prompt in chapter.exercises.position_building_prompts:
        lines.append(f"- {prompt}")
    
    lines.extend(["", "### Argument Reconstruction", ""])
    for ex in chapter.exercises.argument_reconstruction:
        lines.append(f"- {ex}")
    
    lines.extend(["", "### Counterexample Challenges", ""])
    for ch in chapter.exercises.counterexample_generation:
        lines.append(f"- {ch}")
    
    lines.extend(["", "## Connections to Other Topics", ""])
    for link in chapter.synthesis_links:
        lines.append(f"- {link}")
    
    return "\n".join(lines)
