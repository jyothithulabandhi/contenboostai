"""
ContentBoost AI — Utility Functions

SEO scoring engine and formatting helpers.
Scores product description variants on keyword match, length, readability, and power words.
"""

import re
import json
from typing import Optional


# Curated list of power/action words that boost conversions
POWER_WORDS = [
    "exclusive", "proven", "guaranteed", "transform", "revolutionary", "breakthrough",
    "premium", "ultimate", "powerful", "instant", "effortless", "remarkable",
    "stunning", "exceptional", "unmatched", "superior", "innovative", "advanced",
    "professional", "essential", "incredible", "phenomenal", "extraordinary",
    "free", "limited", "save", "discover", "unlock", "boost", "maximize",
    "elevate", "dominate", "crush", "skyrocket", "explode", "unleash",
    "certified", "authentic", "handcrafted", "precision", "engineered",
    "award-winning", "best-selling", "top-rated", "trusted", "recommended",
    "luxurious", "sleek", "elegant", "sophisticated", "cutting-edge",
    "risk-free", "money-back", "lifetime", "warranty", "guarantee",
    "fast", "quick", "rapid", "immediate", "seamless", "smooth",
    "comfortable", "lightweight", "durable", "versatile", "portable",
]


def calculate_seo_score(variant: dict, target_keywords: list[str]) -> int:
    """Calculate SEO score for a product description variant (0-100).
    
    Scoring breakdown:
    - Keyword match (40%): Percentage of target keywords found in content
    - Optimal length (20%): Long description word count in 150-300 range
    - Readability (20%): Average sentence length between 15-20 words
    - Power words (20%): Presence of conversion-boosting power words
    
    Args:
        variant: Dictionary with title, short_description, long_description,
                 bullet_points, meta_description, seo_keywords.
        target_keywords: List of target SEO keywords to check against.
        
    Returns:
        int: SEO score between 0 and 100.
    """
    score = 0.0
    
    # --- Keyword Match (40 points) ---
    keyword_score = _score_keyword_match(variant, target_keywords)
    score += keyword_score * 0.4
    
    # --- Optimal Length (20 points) ---
    length_score = _score_length(variant)
    score += length_score * 0.2
    
    # --- Readability (20 points) ---
    readability_score = _score_readability(variant)
    score += readability_score * 0.2
    
    # --- Power Words (20 points) ---
    power_score = _score_power_words(variant)
    score += power_score * 0.2
    
    return max(0, min(100, round(score)))


def _score_keyword_match(variant: dict, target_keywords: list[str]) -> float:
    """Score keyword presence across all variant fields (0-100).
    
    Args:
        variant: The variant dictionary.
        target_keywords: Keywords to look for.
        
    Returns:
        float: Score between 0 and 100.
    """
    if not target_keywords:
        return 50.0  # Neutral score when no keywords specified
    
    # Combine all text content
    all_text = " ".join([
        variant.get("title", ""),
        variant.get("short_description", ""),
        variant.get("long_description", ""),
        " ".join(variant.get("bullet_points", [])),
        variant.get("meta_description", ""),
        " ".join(variant.get("seo_keywords", []))
    ]).lower()
    
    matches = sum(1 for kw in target_keywords if kw.lower() in all_text)
    match_ratio = matches / len(target_keywords)
    
    return match_ratio * 100


def _score_length(variant: dict) -> float:
    """Score the long description length (0-100). Optimal: 150-300 words.
    
    Args:
        variant: The variant dictionary.
        
    Returns:
        float: Score between 0 and 100.
    """
    long_desc = variant.get("long_description", "")
    word_count = len(long_desc.split())
    
    if 150 <= word_count <= 300:
        return 100.0
    elif word_count < 150:
        # Scale from 0 at 0 words to 100 at 150 words
        return max(0, (word_count / 150) * 100)
    else:
        # Scale down from 100 at 300 words to 50 at 500+ words
        penalty = min(50, ((word_count - 300) / 200) * 50)
        return max(50, 100 - penalty)


def _score_readability(variant: dict) -> float:
    """Score readability based on sentence length (0-100). Ideal: 15-20 words/sentence.
    
    Args:
        variant: The variant dictionary.
        
    Returns:
        float: Score between 0 and 100.
    """
    long_desc = variant.get("long_description", "")
    if not long_desc:
        return 0.0
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', long_desc)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return 0.0
    
    avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
    
    # Ideal range: 15-20 words per sentence
    if 15 <= avg_words <= 20:
        return 100.0
    elif avg_words < 15:
        # Short sentences are okay but not ideal
        return max(50, 100 - (15 - avg_words) * 5)
    else:
        # Long sentences hurt readability
        return max(30, 100 - (avg_words - 20) * 4)


def _score_power_words(variant: dict) -> float:
    """Score presence of conversion power words (0-100).
    
    Args:
        variant: The variant dictionary.
        
    Returns:
        float: Score between 0 and 100.
    """
    all_text = " ".join([
        variant.get("title", ""),
        variant.get("short_description", ""),
        variant.get("long_description", ""),
        " ".join(variant.get("bullet_points", [])),
    ]).lower()
    
    found = sum(1 for word in POWER_WORDS if word in all_text)
    
    # Expect 5-15 power words for a good score
    if found >= 15:
        return 100.0
    elif found >= 10:
        return 85.0 + (found - 10) * 3
    elif found >= 5:
        return 60.0 + (found - 5) * 5
    else:
        return found * 12


def format_variant_for_display(variant: dict) -> str:
    """Format a variant as readable text for clipboard copy.
    
    Args:
        variant: The variant dictionary.
        
    Returns:
        str: Formatted text representation.
    """
    lines = []
    lines.append(f"📌 {variant.get('title', 'Untitled')}")
    lines.append("")
    lines.append(f"Short Description: {variant.get('short_description', '')}")
    lines.append("")
    lines.append("Description:")
    lines.append(variant.get("long_description", ""))
    lines.append("")
    lines.append("Key Features:")
    for bp in variant.get("bullet_points", []):
        lines.append(f"  • {bp}")
    lines.append("")
    lines.append(f"Meta Description: {variant.get('meta_description', '')}")
    lines.append("")
    lines.append(f"SEO Keywords: {', '.join(variant.get('seo_keywords', []))}")
    return "\n".join(lines)


def format_variant_as_json(variant: dict) -> str:
    """Format a variant as pretty-printed JSON for export.
    
    Args:
        variant: The variant dictionary.
        
    Returns:
        str: JSON string representation.
    """
    return json.dumps(variant, indent=2, ensure_ascii=False)


def get_score_color(score: int) -> str:
    """Get a color code based on SEO score for UI display.
    
    Args:
        score: SEO score (0-100).
        
    Returns:
        str: Hex color code.
    """
    if score >= 80:
        return "#10B981"  # Green
    elif score >= 60:
        return "#F59E0B"  # Amber
    elif score >= 40:
        return "#F97316"  # Orange
    else:
        return "#EF4444"  # Red


def get_score_label(score: int) -> str:
    """Get a human-readable label for an SEO score.
    
    Args:
        score: SEO score (0-100).
        
    Returns:
        str: Score label.
    """
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Very Good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 50:
        return "Needs Work"
    else:
        return "Poor"
