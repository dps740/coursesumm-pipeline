"""Topic clustering across lectures."""

from typing import List, Dict
from collections import defaultdict

from coursumm.models import LecturePrimitives, TopicCluster, TopicMap
from coursumm.config import get_config
from coursumm.utils.llm import call_llm, parse_json_response


CLUSTERING_PROMPT = """You are organizing philosophical concepts into topic clusters.

Given these philosophical topics and a list of primitives (claims, definitions, objections, examples), assign each primitive to the most relevant topic.

TOPICS:
{topics}

PRIMITIVES TO ASSIGN:
{primitives}

For each primitive, assign it to ONE topic. Return JSON:
{{
    "assignments": [
        {{"primitive_id": "id", "topic": "topic_name"}}
    ]
}}

If a primitive doesn't fit any topic well, assign it to the closest match.
Return ONLY valid JSON."""


async def cluster_primitives(
    all_primitives: List[LecturePrimitives],
) -> TopicMap:
    """
    Cluster primitives from all lectures into topic clusters.
    
    Args:
        all_primitives: Primitives from all lectures
        
    Returns:
        TopicMap with clusters
    """
    config = get_config()
    topics = config.topics
    
    # Collect all primitives with their info
    primitive_list = []
    primitive_lookup = {}
    
    for lp in all_primitives:
        for claim in lp.claims:
            primitive_list.append({
                "id": claim.id,
                "type": "claim",
                "text": claim.text,
                "lecture": lp.lecture_id,
            })
            primitive_lookup[claim.id] = lp.lecture_id
        
        for premise in lp.premises:
            primitive_list.append({
                "id": premise.id,
                "type": "premise", 
                "text": premise.text,
                "lecture": lp.lecture_id,
            })
            primitive_lookup[premise.id] = lp.lecture_id
        
        for defn in lp.definitions:
            primitive_list.append({
                "id": defn.id,
                "type": "definition",
                "text": f"{defn.term}: {defn.definition}",
                "lecture": lp.lecture_id,
            })
            primitive_lookup[defn.id] = lp.lecture_id
        
        for obj in lp.objections:
            primitive_list.append({
                "id": obj.id,
                "type": "objection",
                "text": obj.text,
                "lecture": lp.lecture_id,
            })
            primitive_lookup[obj.id] = lp.lecture_id
        
        for ex in lp.examples:
            primitive_list.append({
                "id": ex.id,
                "type": "example",
                "text": f"{ex.name}: {ex.illustrates}",
                "lecture": lp.lecture_id,
            })
            primitive_lookup[ex.id] = lp.lecture_id
    
    # Batch into manageable chunks for LLM
    assignments = {}
    batch_size = 50
    
    for i in range(0, len(primitive_list), batch_size):
        batch = primitive_list[i:i + batch_size]
        
        # Format primitives for prompt
        primitives_text = "\n".join([
            f"- ID: {p['id']}, Type: {p['type']}, Text: {p['text'][:200]}"
            for p in batch
        ])
        
        topics_text = "\n".join([f"- {t}" for t in topics])
        
        response = await call_llm(
            CLUSTERING_PROMPT.format(
                topics=topics_text,
                primitives=primitives_text,
            ),
            json_response=True,
            temperature=0.2,
        )
        
        result = parse_json_response(response)
        
        for assignment in result.get("assignments", []):
            pid = assignment.get("primitive_id")
            topic = assignment.get("topic")
            if pid and topic:
                assignments[pid] = topic
    
    # Build clusters
    cluster_data = defaultdict(lambda: {"primitives": [], "lectures": set()})
    
    for pid, topic in assignments.items():
        if topic in topics:
            cluster_data[topic]["primitives"].append(pid)
            if pid in primitive_lookup:
                cluster_data[topic]["lectures"].add(primitive_lookup[pid])
    
    # Create TopicCluster objects
    clusters = []
    for topic in topics:
        data = cluster_data.get(topic, {"primitives": [], "lectures": set()})
        
        # Calculate importance based on number of primitives
        total_primitives = sum(len(c["primitives"]) for c in cluster_data.values())
        importance = len(data["primitives"]) / total_primitives if total_primitives > 0 else 0
        
        clusters.append(TopicCluster(
            topic_id=topic,
            topic_name=topic.replace("_", " ").title(),
            linked_primitives=data["primitives"],
            linked_lectures=list(data["lectures"]),
            importance_score=importance,
        ))
    
    return TopicMap(clusters=clusters)
