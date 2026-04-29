"""
ContentBoost AI — Prompt Templates

All prompt templates used in the 3-stage LLM optimization chain.
Each prompt is designed to produce structured JSON output.
"""


PRODUCT_EXTRACTION_PROMPT = """You are a product data extraction specialist. Given raw scraped content 
from a product page, extract the following structured information.

Raw Content:
{raw_content}

Return ONLY valid JSON in this exact format:
{{
    "title": "Product title",
    "description": "Full product description text",
    "bullet_points": ["bullet 1", "bullet 2", ...],
    "features": ["feature 1", "feature 2", ...]
}}

If a field cannot be determined, use an empty string or empty list. 
Extract the most relevant information only — ignore navigation, ads, and footer content."""


COMPETITOR_ANALYSIS_PROMPT = """You are an expert e-commerce analyst specializing in competitive intelligence.

Analyze the following competitor product descriptions and extract actionable insights.

Product Category: {category}
Target Product: {product_name}

Competitor Data:
{competitor_json}

Provide your analysis as valid JSON in this exact format:
{{
    "tone": "Description of the overall tone and voice used by competitors",
    "usps": ["USP 1", "USP 2", "USP 3", ...],
    "keyword_patterns": ["keyword 1", "keyword 2", ...],
    "gaps": ["Gap/opportunity 1", "Gap/opportunity 2", ...],
    "common_features": ["Feature competitors all mention"],
    "price_positioning": "How competitors position on value/premium scale",
    "emotional_triggers": ["Emotional trigger 1", "Emotional trigger 2", ...]
}}

Focus on:
1. TONE: What writing style do competitors use? (technical, emotional, aspirational, casual)
2. USPs: What unique selling propositions do competitors highlight?
3. KEYWORDS: What keywords and phrases appear repeatedly?
4. GAPS: What are competitors NOT talking about that could be an opportunity?
5. EMOTIONAL TRIGGERS: What emotions do competitors try to evoke?"""


MEMORY_CONTEXT_PROMPT = """Based on the following past successful product descriptions and user feedback, 
identify patterns of what worked well.

Product being optimized: {product_name}
Category: {category}

Past successful descriptions:
{memory_results}

Summarize the key patterns that made these descriptions successful:
1. What writing techniques worked?
2. What keywords drove engagement?
3. What structure/format was most effective?
4. What should be repeated or avoided?

Provide a concise summary (2-3 paragraphs) that can guide the generation of new descriptions."""


VARIANT_GENERATION_PROMPT = """You are a world-class e-commerce copywriter and SEO specialist.

Generate 3 optimized product description variants based on the following inputs.

## Product Information
- Name: {product_name}
- Category: {category}
- Current Description: {current_description}
- Target Keywords: {target_keywords}

## Competitor Analysis
{competitor_analysis}

## Memory Context (What Worked Before)
{memory_context}

## Instructions
Generate exactly 3 variants. Each must be unique in approach:

1. **SEO-focused**: Maximize keyword density naturally. Include target keywords in title, descriptions, 
   and bullet points. Write meta description under 160 characters. Long description should be 150-300 words.

2. **Conversion-focused**: Lead with benefits, not features. Use emotional triggers, social proof 
   language, and urgency. Address pain points directly. Include a call-to-action. Long description 
   should be 200-350 words.

3. **Brand-differentiated**: Find unique angles competitors miss. Create a distinctive brand voice. 
   Highlight what makes this product fundamentally different. Long description should be 150-300 words.

Return ONLY valid JSON in this exact format:
{{
    "variants": [
        {{
            "variant_type": "seo",
            "title": "SEO-optimized product title (include primary keywords)",
            "short_description": "Compelling 1-2 sentence summary (under 200 characters)",
            "long_description": "Full product description (150-300 words)",
            "bullet_points": ["5 benefit-driven bullet points"],
            "meta_description": "SEO meta description (under 160 characters)",
            "seo_keywords": ["8-12 relevant SEO keywords"]
        }},
        {{
            "variant_type": "conversion",
            "title": "Conversion-optimized title (benefit-focused)",
            "short_description": "Emotionally compelling summary",
            "long_description": "Persuasive description with social proof (200-350 words)",
            "bullet_points": ["5 benefit-driven bullet points with emotional hooks"],
            "meta_description": "Action-oriented meta description",
            "seo_keywords": ["relevant keywords"]
        }},
        {{
            "variant_type": "brand",
            "title": "Brand-differentiated title (unique positioning)",
            "short_description": "Distinctive brand voice summary",
            "long_description": "Description highlighting unique angles (150-300 words)",
            "bullet_points": ["5 differentiation-focused bullet points"],
            "meta_description": "Brand-focused meta description",
            "seo_keywords": ["brand-relevant keywords"]
        }}
    ]
}}

Make each variant genuinely different in approach, not just rewording of the same content.
Every description must be compelling, professional, and ready for a real product page."""
