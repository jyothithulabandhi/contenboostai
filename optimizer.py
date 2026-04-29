"""
ContentBoost AI — LLM Optimization Engine

Implements a 3-stage chain using Anthropic Claude API:
  Stage 1: Analyze competitor descriptions
  Stage 2: Load memory context from past optimizations
  Stage 3: Generate 3 optimized product description variants

Falls back to fixture data in demo mode when ANTHROPIC_API_KEY is not set.
"""

import os
import json
from typing import Optional, Callable
from dotenv import load_dotenv

from prompts import (
    COMPETITOR_ANALYSIS_PROMPT,
    MEMORY_CONTEXT_PROMPT,
    VARIANT_GENERATION_PROMPT,
)
from memory_manager import MemoryManager
from utils import calculate_seo_score

load_dotenv()

# Path to fixture data
FIXTURES_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "sample_products.json")


class ProductOptimizer:
    """3-stage LLM chain for product description optimization.
    
    Stage 1: Analyzes competitor descriptions to extract tone, USPs, keywords.
    Stage 2: Loads memory context from past successful descriptions.
    Stage 3: Generates 3 optimized variants (SEO, Conversion, Brand).
    
    Attributes:
        client: Anthropic client instance (None if API key not set).
        model: Claude model identifier to use.
    """
    
    def __init__(self) -> None:
        """Initialize the ProductOptimizer."""
        self.client = None
        self.model = "claude-sonnet-4-20250514"
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the Anthropic client if API key is available."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key and api_key != "your-anthropic-api-key":
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=api_key)
            except Exception as e:
                print(f"ANTHROPIC initialization failed: {e}")
    
    def is_available(self) -> bool:
        """Check if the Anthropic API is configured and available.
        
        Returns:
            bool: True if the client is initialized.
        """
        return self.client is not None
    
    def _call_claude(self, prompt: str, max_tokens: int = 4096) -> str:
        """Make a Claude API call with error handling.
        
        Args:
            prompt: The user prompt to send.
            max_tokens: Maximum tokens in the response.
            
        Returns:
            str: Claude's response text.
            
        Raises:
            RuntimeError: If the API call fails.
        """
        if not self.client:
            raise RuntimeError("Anthropic API not configured")
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Claude API call failed: {e}")
    
    def _parse_json_response(self, response_text: str) -> dict:
        """Extract and parse JSON from Claude's response.
        
        Args:
            response_text: Raw response text from Claude.
            
        Returns:
            dict: Parsed JSON data.
            
        Raises:
            ValueError: If no valid JSON found in response.
        """
        # Try direct parse first
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try extracting JSON block
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            try:
                return json.loads(response_text[json_start:json_end])
            except json.JSONDecodeError:
                pass
        
        raise ValueError("Could not parse JSON from Claude response")
    
    # ─── Stage 1: Competitor Analysis ────────────────────────
    
    def analyze_competitors(self, competitor_data: list[dict], product_name: str, category: str) -> dict:
        """Stage 1: Analyze competitor descriptions for insights.
        
        Args:
            competitor_data: List of competitor product data dictionaries.
            product_name: Name of the product being optimized.
            category: Product category.
            
        Returns:
            dict: Competitor analysis with tone, USPs, keywords, gaps.
        """
        if not self.is_available():
            return self._get_demo_analysis(competitor_data, product_name, category)
        
        try:
            prompt = COMPETITOR_ANALYSIS_PROMPT.format(
                category=category,
                product_name=product_name,
                competitor_json=json.dumps(competitor_data, indent=2)
            )
            response = self._call_claude(prompt, max_tokens=2048)
            return self._parse_json_response(response)
        except Exception as e:
            print(f"Competitor analysis failed: {e}")
            return self._get_demo_analysis(competitor_data, product_name, category)
    
    # ─── Stage 2: Memory Context ────────────────────────────
    
    def load_memory_context(
        self,
        product_name: str,
        category: str,
        memory_manager: MemoryManager
    ) -> str:
        """Stage 2: Retrieve and format past context from mem0.
        
        Args:
            product_name: Name of the product being optimized.
            category: Product category.
            memory_manager: MemoryManager instance.
            
        Returns:
            str: Formatted memory context for prompt injection.
        """
        memories = memory_manager.get_relevant_context(product_name, category)
        return memory_manager.format_context_for_prompt(memories)
    
    # ─── Stage 3: Variant Generation ────────────────────────
    
    def generate_variants(
        self,
        product_name: str,
        category: str,
        current_description: str,
        target_keywords: list[str],
        competitor_analysis: dict,
        memory_context: str
    ) -> list[dict]:
        """Stage 3: Generate 3 optimized product description variants.
        
        Args:
            product_name: Name of the product.
            category: Product category.
            current_description: Current/original product description.
            target_keywords: List of target SEO keywords.
            competitor_analysis: Output from Stage 1.
            memory_context: Output from Stage 2.
            
        Returns:
            list[dict]: List of 3 variant dictionaries.
        """
        if not self.is_available():
            return self._get_demo_variants(product_name, category, current_description, target_keywords)
        
        try:
            prompt = VARIANT_GENERATION_PROMPT.format(
                product_name=product_name,
                category=category,
                current_description=current_description,
                target_keywords=", ".join(target_keywords),
                competitor_analysis=json.dumps(competitor_analysis, indent=2),
                memory_context=memory_context
            )
            response = self._call_claude(prompt, max_tokens=4096)
            data = self._parse_json_response(response)
            
            variants = data.get("variants", [])
            if not variants:
                raise ValueError("No variants in response")
            
            return variants
            
        except Exception as e:
            print(f"Variant generation failed: {e}")
            return self._get_demo_variants(product_name, category, current_description, target_keywords)
    
    # ─── Full Pipeline Orchestration ────────────────────────
    
    def optimize(
        self,
        product_name: str,
        category: str,
        current_description: str,
        target_keywords: list[str],
        competitor_data: list[dict],
        memory_manager: MemoryManager,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> dict:
        """Run the full 3-stage optimization pipeline.
        
        Args:
            product_name: Name of the product.
            category: Product category.
            current_description: Current product description.
            target_keywords: List of target SEO keywords.
            competitor_data: List of scraped competitor data.
            memory_manager: MemoryManager instance.
            progress_callback: Optional callback(progress_pct, status_message).
            
        Returns:
            dict: Contains 'variants' (list), 'competitor_analysis' (dict),
                  'memory_context' (str), and 'scores' (list).
        """
        if progress_callback:
            progress_callback(10, "🔍 Analyzing competitor descriptions...")
        
        # Stage 1: Competitor Analysis
        competitor_analysis = self.analyze_competitors(
            competitor_data, product_name, category
        )
        
        if progress_callback:
            progress_callback(35, "🧠 Loading memory context...")
        
        # Stage 2: Memory Context
        memory_context = self.load_memory_context(
            product_name, category, memory_manager
        )
        
        if progress_callback:
            progress_callback(55, "✨ Generating optimized variants...")
        
        # Stage 3: Generate Variants
        variants = self.generate_variants(
            product_name, category, current_description,
            target_keywords, competitor_analysis, memory_context
        )
        
        if progress_callback:
            progress_callback(80, "📊 Calculating SEO scores...")
        
        # Score each variant
        scores = []
        for variant in variants:
            score = calculate_seo_score(variant, target_keywords)
            variant["seo_score"] = score
            scores.append(score)
        
        if progress_callback:
            progress_callback(100, "✅ Optimization complete!")
        
        return {
            "variants": variants,
            "competitor_analysis": competitor_analysis,
            "memory_context": memory_context,
            "scores": scores
        }
    
    # ─── Demo Data (Input-Aware) ────────────────────────────
    
    def _get_demo_analysis(
        self,
        competitor_data: list[dict] = None,
        product_name: str = "",
        category: str = ""
    ) -> dict:
        """Generate a demo competitor analysis based on actual inputs.
        
        Args:
            competitor_data: Competitor data (used to extract titles).
            product_name: The user's product name.
            category: The user's category.
            
        Returns:
            dict: Context-aware competitor analysis.
        """
        # Extract real competitor info if available
        comp_titles = []
        comp_features = []
        if competitor_data:
            for cd in competitor_data:
                if cd.get("title"):
                    comp_titles.append(cd["title"])
                comp_features.extend(cd.get("features", [])[:3])
        
        cat_short = category.split(" - ")[-1] if category else "products"
        
        return {
            "tone": f"Professional and aspirational with technical credibility. Competitors in {cat_short} emphasize specs and performance while using emotional language around user experience.",
            "usps": (comp_features[:5] if comp_features else [
                f"Premium {cat_short.lower()} quality",
                "Advanced technology integration",
                "Superior user experience",
                "Competitive pricing and value",
                "Strong brand trust and reviews"
            ]),
            "keyword_patterns": [
                product_name.split()[0].lower() if product_name else "premium",
                cat_short.lower(),
                "best", "top-rated", "professional", "advanced", "premium"
            ],
            "gaps": [
                f"No competitor emphasizes sustainability for {cat_short.lower()}",
                "Limited focus on long-term durability and warranty",
                "No competitor leverages customer success stories effectively",
                f"Unique craftsmanship angle untapped in {cat_short.lower()} market"
            ]
        }
    
    def _get_demo_variants(
        self,
        product_name: str = "Demo Product",
        category: str = "General",
        current_description: str = "",
        target_keywords: list[str] = None
    ) -> list[dict]:
        """Generate demo variants personalized to the user's actual inputs.
        
        Args:
            product_name: The user's product name.
            category: The user's product category.
            current_description: The user's current description.
            target_keywords: The user's target keywords.
            
        Returns:
            list[dict]: 3 input-aware demo variants.
        """
        keywords = target_keywords or []
        kw_str = ", ".join(keywords[:5]) if keywords else category.lower()
        cat_short = category.split(" - ")[-1] if category else "products"
        
        # Build keyword-enriched content
        kw_mentions = " ".join(keywords[:3]) if keywords else product_name
        base_desc = current_description if current_description else f"A premium {cat_short.lower()} product designed for discerning customers."
        
        return [
            {
                "variant_type": "seo",
                "title": f"{product_name} — Premium {cat_short} | {' | '.join(keywords[:3]) if keywords else 'Top Rated'}",
                "short_description": f"Discover the {product_name} — engineered for exceptional performance in {cat_short.lower()}. Featuring advanced technology, premium build quality, and unmatched reliability for professionals and enthusiasts alike.",
                "long_description": (
                    f"Introducing the {product_name} — the ultimate {cat_short.lower()} solution designed to exceed expectations. "
                    f"Built with cutting-edge technology and premium materials, this product delivers outstanding performance "
                    f"that sets a new standard in the {category.lower()} market.\n\n"
                    f"Every detail has been meticulously engineered for maximum impact. From the precision-crafted components "
                    f"to the intuitive user experience, the {product_name} represents the pinnacle of modern {cat_short.lower()} design. "
                    f"Whether you're a seasoned professional or a passionate enthusiast, you'll appreciate the remarkable "
                    f"attention to detail that goes into every unit.\n\n"
                    f"Key advantages include industry-leading durability, seamless integration with your existing setup, "
                    f"and a design philosophy that prioritizes both form and function. The {product_name} isn't just another "
                    f"{cat_short.lower()} product — it's a statement of quality that delivers measurable results.\n\n"
                    f"Experience the difference that true premium engineering makes. Upgrade to {product_name} today and "
                    f"join thousands of satisfied customers who've made the switch to excellence."
                ),
                "bullet_points": [
                    f"Premium {cat_short.lower()} engineered for exceptional {kw_mentions} performance",
                    f"Advanced technology delivers industry-leading results in {category.lower()}",
                    "Precision-crafted with durable, high-quality materials built to last",
                    f"Seamless setup and intuitive design — perfect for {cat_short.lower()} enthusiasts",
                    f"Trusted by thousands — top-rated {cat_short.lower()} choice for professionals"
                ],
                "meta_description": f"{product_name} — premium {cat_short.lower()} with advanced features, exceptional durability, and top-rated performance. Shop now for the best in {kw_str}.",
                "seo_keywords": keywords[:8] if keywords else [product_name.lower(), cat_short.lower(), "premium", "best", "top-rated", "professional", "advanced", "high-quality"]
            },
            {
                "variant_type": "conversion",
                "title": f"{product_name} — The {cat_short} That Changes Everything",
                "short_description": f"Tired of {cat_short.lower()} products that overpromise and underdeliver? {product_name} is different — engineered from the ground up to solve the frustrations you've been putting up with. Your search for the perfect {cat_short.lower()} ends here.",
                "long_description": (
                    f"Let's be honest — finding the right {cat_short.lower()} shouldn't be this hard. You've probably tried "
                    f"products that looked great online but fell apart in weeks. Or ones that had impressive specs but felt "
                    f"cheap the moment you held them. We've been there too, and that's exactly why we created {product_name}.\n\n"
                    f"Here's what makes it different: we obsessed over the details that actually matter to you. Every feature "
                    f"was tested by real users in real conditions — not just in a lab. The result? A {cat_short.lower()} product "
                    f"that performs exactly as promised, every single time.\n\n"
                    f"But don't just take our word for it. Over 5,000 customers have rated {product_name} 4.8 out of 5 stars, "
                    f"and our return rate is under 2%. That's virtually unheard of in the {category.lower()} space. Why? "
                    f"Because when you build something right, people keep it.\n\n"
                    f"We're so confident you'll love {product_name} that we back every purchase with a 30-day satisfaction "
                    f"guarantee. If it doesn't exceed your expectations, send it back — no questions asked.\n\n"
                    f"Stop settling for mediocre. Upgrade to {product_name} and feel the difference from day one."
                ),
                "bullet_points": [
                    f"Solves the #1 frustration with {cat_short.lower()} products — guaranteed performance",
                    f"4.8/5 stars from 5,000+ verified customers who made the switch",
                    "Built and tested by real users, not just engineers in a lab",
                    f"30-day risk-free guarantee — love your {product_name} or return it free",
                    "Under 2% return rate — because quality speaks for itself"
                ],
                "meta_description": f"{product_name} — rated 4.8/5 by 5,000+ customers. Premium {cat_short.lower()} with 30-day money-back guarantee. Stop settling, start experiencing.",
                "seo_keywords": keywords[:5] + ["best " + cat_short.lower(), "top rated", "guaranteed"] if keywords else [product_name.lower(), "best " + cat_short.lower(), "top rated", "premium", "guaranteed", "reviews"]
            },
            {
                "variant_type": "brand",
                "title": f"{product_name} — Redefining What {cat_short} Can Be",
                "short_description": f"While others iterate, we innovate. {product_name} wasn't built to compete with existing {cat_short.lower()} products — it was built to make them obsolete. This is {cat_short.lower()}, reimagined from first principles.",
                "long_description": (
                    f"The {cat_short.lower()} market is crowded with products that all look the same, feel the same, and "
                    f"perform the same. Incremental improvements dressed up as innovation. At {product_name}, we asked a "
                    f"different question: what if we started from scratch?\n\n"
                    f"Three years of research. Hundreds of prototypes. Countless hours of user testing. The result is a "
                    f"{cat_short.lower()} product that doesn't just improve on what exists — it reimagines what's possible. "
                    f"Every component, every material, every design choice serves a purpose.\n\n"
                    f"Where competitors chase trends, we chase truth. The truth that great {cat_short.lower()} should be "
                    f"invisible — it should simply work, beautifully and reliably, so you can focus on what actually matters. "
                    f"That philosophy drives everything we do, from our sustainable sourcing practices to our lifetime "
                    f"customer support commitment.\n\n"
                    f"{product_name} isn't for everyone. It's for the discerning few who understand that true quality isn't "
                    f"about having the most features — it's about having the right ones, executed flawlessly.\n\n"
                    f"Experience the difference that genuine innovation makes."
                ),
                "bullet_points": [
                    f"3 years of R&D — {product_name} is innovation, not iteration",
                    f"First-principles design that reimagines {cat_short.lower()} from the ground up",
                    "Sustainably sourced materials with lifetime customer support",
                    f"Purpose-driven engineering — every feature exists for a reason",
                    f"For the discerning few who demand more from their {cat_short.lower()}"
                ],
                "meta_description": f"{product_name} — 3 years of R&D redefining {cat_short.lower()}. First-principles design, sustainable materials, lifetime support. This isn't incremental. This is new.",
                "seo_keywords": keywords[:4] + ["innovative " + cat_short.lower(), "premium design", "sustainable"] if keywords else [product_name.lower(), "innovative", "premium " + cat_short.lower(), "sustainable", "luxury", "designer"]
            }
        ]
