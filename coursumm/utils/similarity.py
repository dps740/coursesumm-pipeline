"""Similarity checking utilities for public safety validation."""

from typing import List, Tuple, Set
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def get_ngrams(text: str, n: int) -> Set[str]:
    """Extract n-grams from text."""
    # Normalize text
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    
    if len(words) < n:
        return set()
    
    ngrams = set()
    for i in range(len(words) - n + 1):
        ngram = " ".join(words[i:i + n])
        ngrams.add(ngram)
    
    return ngrams


def calculate_ngram_overlap(
    generated_text: str,
    source_texts: List[str],
    n: int = 3,
) -> float:
    """
    Calculate n-gram overlap between generated text and source texts.
    
    Returns:
        Overlap rate (0-1): fraction of generated n-grams found in source
    """
    generated_ngrams = get_ngrams(generated_text, n)
    
    if not generated_ngrams:
        return 0.0
    
    # Collect all source n-grams
    source_ngrams = set()
    for source in source_texts:
        source_ngrams.update(get_ngrams(source, n))
    
    # Calculate overlap
    overlap = generated_ngrams.intersection(source_ngrams)
    return len(overlap) / len(generated_ngrams)


def find_longest_common_sequence(
    generated_text: str,
    source_texts: List[str],
) -> Tuple[int, str]:
    """
    Find the longest sequence of consecutive words shared with source.
    
    Returns:
        (length, sequence) of longest match
    """
    # Normalize
    gen_words = generated_text.lower().split()
    
    longest_length = 0
    longest_seq = ""
    
    for source in source_texts:
        source_words = source.lower().split()
        source_set = set()
        
        # Build set of all word sequences in source
        for length in range(1, min(len(source_words), 20) + 1):
            for i in range(len(source_words) - length + 1):
                seq = " ".join(source_words[i:i + length])
                source_set.add(seq)
        
        # Check generated sequences against source
        for length in range(len(gen_words), 0, -1):
            for i in range(len(gen_words) - length + 1):
                seq = " ".join(gen_words[i:i + length])
                if seq in source_set and length > longest_length:
                    longest_length = length
                    longest_seq = seq
                    break
            if longest_length > 0:
                break
    
    return longest_length, longest_seq


def calculate_cosine_similarity(
    generated_text: str,
    source_texts: List[str],
) -> Tuple[float, int]:
    """
    Calculate max cosine similarity between generated text and source texts.
    
    Uses TF-IDF vectorization.
    
    Returns:
        (max_similarity, index_of_most_similar_source)
    """
    if not source_texts:
        return 0.0, -1
    
    # Combine all texts
    all_texts = [generated_text] + source_texts
    
    # Vectorize
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words='english',
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
    except ValueError:
        # Empty vocabulary (e.g., all stop words)
        return 0.0, -1
    
    # Calculate similarity of generated (index 0) against all sources
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    max_sim = float(np.max(similarities))
    max_idx = int(np.argmax(similarities))
    
    return max_sim, max_idx


def check_forbidden_strings(
    text: str,
    forbidden: List[str],
) -> List[str]:
    """
    Check for forbidden strings in text.
    
    Returns:
        List of forbidden strings found
    """
    found = []
    text_lower = text.lower()
    
    for forbidden_str in forbidden:
        if forbidden_str.lower() in text_lower:
            found.append(forbidden_str)
    
    return found


class SafetyChecker:
    """Comprehensive safety checker for public content."""
    
    def __init__(
        self,
        source_chunks: List[str],
        lecture_titles: List[str] = None,
        max_ngram_overlap: float = 0.02,
        max_cosine_similarity: float = 0.80,
        max_consecutive_words: int = 8,
    ):
        self.source_chunks = source_chunks
        self.lecture_titles = lecture_titles or []
        self.max_ngram_overlap = max_ngram_overlap
        self.max_cosine_similarity = max_cosine_similarity
        self.max_consecutive_words = max_consecutive_words
        
        # Build forbidden strings
        self.forbidden = ["Lecture", "lecture"]
        for i in range(1, 100):
            self.forbidden.append(f"L{i:02d}")
            self.forbidden.append(f"Lecture {i}")
        self.forbidden.extend(self.lecture_titles)
    
    def check(self, text: str) -> dict:
        """
        Run all safety checks on generated text.
        
        Returns:
            {
                "passed": bool,
                "issues": List[str],
                "ngram_overlap": float,
                "cosine_similarity": float,
                "longest_sequence": int,
                "forbidden_found": List[str],
                "most_similar_chunk_idx": int,
            }
        """
        issues = []
        
        # Check forbidden strings
        forbidden_found = check_forbidden_strings(text, self.forbidden)
        if forbidden_found:
            issues.append(f"Forbidden strings found: {forbidden_found}")
        
        # Check n-gram overlap
        ngram_overlap = calculate_ngram_overlap(text, self.source_chunks, n=3)
        if ngram_overlap > self.max_ngram_overlap:
            issues.append(f"3-gram overlap {ngram_overlap:.1%} exceeds {self.max_ngram_overlap:.1%}")
        
        # Check cosine similarity
        cos_sim, most_similar_idx = calculate_cosine_similarity(text, self.source_chunks)
        if cos_sim > self.max_cosine_similarity:
            issues.append(f"Cosine similarity {cos_sim:.2f} exceeds {self.max_cosine_similarity:.2f}")
        
        # Check longest consecutive sequence
        seq_len, seq_text = find_longest_common_sequence(text, self.source_chunks)
        if seq_len > self.max_consecutive_words:
            issues.append(f"Consecutive sequence of {seq_len} words found: '{seq_text[:50]}...'")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "ngram_overlap": ngram_overlap,
            "cosine_similarity": cos_sim,
            "longest_sequence": seq_len,
            "forbidden_found": forbidden_found,
            "most_similar_chunk_idx": most_similar_idx,
        }
