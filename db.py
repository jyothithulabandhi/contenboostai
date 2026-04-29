"""
ContentBoost AI — SQLite Database Layer

Manages persistent storage for optimization history using SQLite.
Stores generated variants, SEO scores, and user selections.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional


DB_PATH = "contentboost.db"


def get_connection() -> sqlite3.Connection:
    """Get a SQLite database connection with row factory enabled.
    
    Returns:
        sqlite3.Connection: Database connection with Row factory.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database schema. Creates tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            original_description TEXT,
            variant_type TEXT NOT NULL CHECK(variant_type IN ('seo', 'conversion', 'brand')),
            generated_title TEXT NOT NULL,
            short_description TEXT,
            long_description TEXT,
            bullet_points TEXT,
            meta_description TEXT,
            seo_keywords TEXT,
            seo_score INTEGER DEFAULT 0,
            is_best INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitor_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            analysis_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_optimization(
    product_name: str,
    category: str,
    original_description: str,
    variant_type: str,
    generated_title: str,
    short_description: str,
    long_description: str,
    bullet_points: list[str],
    meta_description: str,
    seo_keywords: list[str],
    seo_score: int,
    is_best: bool = False
) -> int:
    """Save a generated variant to the database.
    
    Args:
        product_name: Name of the product.
        category: Product category.
        original_description: Original product description.
        variant_type: Type of variant ('seo', 'conversion', or 'brand').
        generated_title: Generated optimized title.
        short_description: Short product description.
        long_description: Long product description.
        bullet_points: List of bullet point strings.
        meta_description: SEO meta description.
        seo_keywords: List of SEO keywords.
        seo_score: SEO score (0-100).
        is_best: Whether this is marked as the best variant.
        
    Returns:
        int: The row ID of the inserted record.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO optimizations 
        (product_name, category, original_description, variant_type, generated_title,
         short_description, long_description, bullet_points, meta_description, 
         seo_keywords, seo_score, is_best, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product_name, category, original_description, variant_type, generated_title,
        short_description, long_description, json.dumps(bullet_points),
        meta_description, json.dumps(seo_keywords), seo_score,
        1 if is_best else 0, datetime.now().isoformat()
    ))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_history(limit: int = 50) -> list[dict]:
    """Retrieve optimization history ordered by most recent.
    
    Args:
        limit: Maximum number of records to return.
        
    Returns:
        list[dict]: List of optimization records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM optimizations ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        record = dict(row)
        # Parse JSON fields
        if record.get("bullet_points"):
            try:
                record["bullet_points"] = json.loads(record["bullet_points"])
            except json.JSONDecodeError:
                record["bullet_points"] = []
        if record.get("seo_keywords"):
            try:
                record["seo_keywords"] = json.loads(record["seo_keywords"])
            except json.JSONDecodeError:
                record["seo_keywords"] = []
        results.append(record)
    return results


def mark_as_best(optimization_id: int) -> None:
    """Mark an optimization as the best variant.
    
    Args:
        optimization_id: The ID of the optimization record.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE optimizations SET is_best = 1 WHERE id = ?
    """, (optimization_id,))
    conn.commit()
    conn.close()


def get_best_variants(limit: int = 20) -> list[dict]:
    """Retrieve variants marked as best.
    
    Args:
        limit: Maximum number of records to return.
        
    Returns:
        list[dict]: List of best variant records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM optimizations WHERE is_best = 1 
        ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        record = dict(row)
        if record.get("bullet_points"):
            try:
                record["bullet_points"] = json.loads(record["bullet_points"])
            except json.JSONDecodeError:
                record["bullet_points"] = []
        if record.get("seo_keywords"):
            try:
                record["seo_keywords"] = json.loads(record["seo_keywords"])
            except json.JSONDecodeError:
                record["seo_keywords"] = []
        results.append(record)
    return results


def save_competitor_analysis(product_name: str, analysis: dict) -> int:
    """Save a competitor analysis to the database.
    
    Args:
        product_name: Name of the product analyzed.
        analysis: Competitor analysis data.
        
    Returns:
        int: The row ID of the inserted record.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO competitor_analyses (product_name, analysis_json, created_at)
        VALUES (?, ?, ?)
    """, (product_name, json.dumps(analysis), datetime.now().isoformat()))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


# Initialize database on module import
init_db()
