"""
ContentBoost AI — Memory Manager

Integrates with mem0 to store and retrieve past product descriptions.
Provides memory-based learning by finding what worked before for similar products.
Falls back gracefully to empty context when MEM0_API_KEY is not set.
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class MemoryManager:
    """Manages persistent memory of past descriptions and feedback using mem0.
    
    Stores every generated description and user feedback. On each new request,
    retrieves the most relevant past improvements as context for the LLM.
    
    Attributes:
        client: mem0 MemoryClient instance (None if API key not set).
        user_id: Identifier for the mem0 user scope.
    """
    
    def __init__(self, user_id: str = "contentboost_default") -> None:
        """Initialize the MemoryManager.
        
        Args:
            user_id: User identifier for mem0 memory scoping.
        """
        self.user_id = user_id
        self.client = None
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the mem0 client if API key is available."""
        api_key = os.getenv("MEM0_API_KEY")
        if api_key and api_key != "your-mem0-api-key":
            try:
                from mem0 import MemoryClient
                self.client = MemoryClient(api_key=api_key)
            except Exception as e:
                print(f"mem0 initialization failed: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if mem0 is configured and available.
        
        Returns:
            bool: True if mem0 client is initialized.
        """
        return self.client is not None
    
    def store_description(
        self,
        product_name: str,
        category: str,
        variant_type: str,
        description: str,
        score: int
    ) -> bool:
        """Store a generated description in mem0 for future reference.
        
        Args:
            product_name: Name of the product.
            category: Product category.
            variant_type: Type of variant (seo/conversion/brand).
            description: The generated description text.
            score: SEO score of the variant.
            
        Returns:
            bool: True if successfully stored, False otherwise.
        """
        if not self.is_available():
            return False
        
        try:
            memory_content = [
                {
                    "role": "user",
                    "content": f"Product: {product_name} | Category: {category}"
                },
                {
                    "role": "assistant",
                    "content": (
                        f"Generated {variant_type} variant (SEO Score: {score}/100):\n"
                        f"{description}"
                    )
                }
            ]
            self.client.add(
                memory_content,
                user_id=self.user_id,
                metadata={
                    "product_name": product_name,
                    "category": category,
                    "variant_type": variant_type,
                    "seo_score": score,
                    "type": "generated_description"
                }
            )
            return True
        except Exception as e:
            print(f"Failed to store memory: {e}")
            return False
    
    def store_feedback(self, product_name: str, feedback_text: str) -> bool:
        """Store user feedback about a description.
        
        Args:
            product_name: Name of the product.
            feedback_text: User's feedback text.
            
        Returns:
            bool: True if successfully stored, False otherwise.
        """
        if not self.is_available():
            return False
        
        try:
            memory_content = [
                {
                    "role": "user",
                    "content": (
                        f"Feedback for {product_name}: {feedback_text}"
                    )
                },
                {
                    "role": "assistant", 
                    "content": f"Noted feedback for {product_name}: {feedback_text}"
                }
            ]
            self.client.add(
                memory_content,
                user_id=self.user_id,
                metadata={
                    "product_name": product_name,
                    "type": "user_feedback"
                }
            )
            return True
        except Exception as e:
            print(f"Failed to store feedback: {e}")
            return False
    
    def get_relevant_context(
        self,
        product_name: str,
        category: str,
        limit: int = 3
    ) -> list[dict]:
        """Retrieve the most relevant past improvements for a product.
        
        Args:
            product_name: Name of the product being optimized.
            category: Product category.
            limit: Maximum number of memories to retrieve.
            
        Returns:
            list[dict]: List of relevant memory entries.
        """
        if not self.is_available():
            return []
        
        try:
            query = f"Best product descriptions for {product_name} in {category}"
            results = self.client.search(
                query,
                user_id=self.user_id,
                limit=limit
            )
            
            # Normalize results
            memories = []
            if hasattr(results, "results"):
                raw = results.results
            elif isinstance(results, list):
                raw = results
            else:
                raw = []
            
            for item in raw:
                if isinstance(item, dict):
                    memories.append({
                        "memory": item.get("memory", item.get("text", "")),
                        "metadata": item.get("metadata", {})
                    })
                elif hasattr(item, "memory"):
                    memories.append({
                        "memory": item.memory,
                        "metadata": getattr(item, "metadata", {})
                    })
            
            return memories[:limit]
        except Exception as e:
            print(f"Failed to retrieve memory context: {e}")
            return []
    
    def format_context_for_prompt(self, memories: list[dict]) -> str:
        """Format retrieved memories into a string for LLM prompt injection.
        
        Args:
            memories: List of memory entries from get_relevant_context.
            
        Returns:
            str: Formatted context string.
        """
        if not memories:
            return "No previous optimization history available for this product type."
        
        lines = []
        for i, mem in enumerate(memories, 1):
            lines.append(f"--- Past Result #{i} ---")
            lines.append(mem.get("memory", ""))
            metadata = mem.get("metadata", {})
            if metadata:
                if metadata.get("seo_score"):
                    lines.append(f"SEO Score: {metadata['seo_score']}/100")
                if metadata.get("variant_type"):
                    lines.append(f"Variant Type: {metadata['variant_type']}")
            lines.append("")
        
        return "\n".join(lines)
