from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
from db import save_optimization, get_history, mark_as_best, get_best_variants, save_competitor_analysis
from memory_manager import MemoryManager
from firecrawl_scraper import CompetitorScraper
from optimizer import ProductOptimizer
from utils import calculate_seo_score

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize Services
memory_mgr = MemoryManager()
scraper = CompetitorScraper()
optimizer = ProductOptimizer()

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "claude": optimizer.is_available(),
        "firecrawl": scraper.is_available(),
        "mem0": memory_mgr.is_available(),
        "mode": "LIVE" if optimizer.is_available() else "DEMO"
    })

@app.route('/api/optimize', methods=['POST'])
def optimize_product():
    data = request.json
    product_name = data.get('product_name')
    category = data.get('category', 'Other')
    current_desc = data.get('current_description', '')
    target_kw = data.get('target_keywords', '')
    urls = data.get('competitor_urls', [])

    if not product_name:
        return jsonify({"error": "Product name is required"}), 400

    keywords = [k.strip() for k in target_kw.split(",") if k.strip()] if target_kw else []

    try:
        # Step 1: Scrape competitors
        comp_data = scraper.scrape_competitors(urls) if urls else scraper._get_demo_competitor_data()

        # Run optimization pipeline
        result = optimizer.optimize(
            product_name=product_name,
            category=category,
            current_description=current_desc,
            target_keywords=keywords,
            competitor_data=comp_data,
            memory_manager=memory_mgr,
            progress_callback=None
        )

        # Recalculate scores with user keywords
        for v in result["variants"]:
            v["seo_score"] = calculate_seo_score(v, keywords)

        return jsonify({
            "variants": result["variants"],
            "competitor_analysis": result["competitor_analysis"],
            "memory_context": result["memory_context"],
            "competitor_data": comp_data
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_optimization_history():
    limit = request.args.get('limit', default=30, type=int)
    history = get_history(limit=limit)
    return jsonify(history)

@app.route('/api/best-variants', methods=['GET'])
def get_best():
    limit = request.args.get('limit', default=10, type=int)
    best = get_best_variants(limit=limit)
    return jsonify(best)

@app.route('/api/save-best', methods=['POST'])
def save_best_variant():
    data = request.json
    variant = data.get('variant')
    product_name = data.get('product_name')
    
    if not variant or not product_name:
        return jsonify({"error": "Variant and product name are required"}), 400

    try:
        row_id = save_optimization(
            product_name=product_name,
            category=data.get('category', ''),
            original_description=data.get('original_description', ''),
            variant_type=variant.get('variant_type', 'seo'),
            generated_title=variant.get('title', ''),
            short_description=variant.get('short_description', ''),
            long_description=variant.get('long_description', ''),
            bullet_points=variant.get('bullet_points', []),
            meta_description=variant.get('meta_description', ''),
            seo_keywords=variant.get('seo_keywords', []),
            seo_score=variant.get('seo_score', 0),
            is_best=True,
        )
        
        memory_mgr.store_description(
            product_name, "", variant.get('variant_type', 'seo'),
            variant.get('long_description', ''), variant.get('seo_score', 0)
        )
        
        return jsonify({"success": True, "id": row_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
