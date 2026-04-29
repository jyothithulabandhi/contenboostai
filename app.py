"""
ContentBoost AI — Streamlit Dashboard

Main application UI with 3-column layout for product description optimization.
Features: input form, variant display with SEO scores, competitor insights,
memory history, optimization history, and demo mode support.
"""


import os
import json
import streamlit as st
from dotenv import load_dotenv

from db import save_optimization, get_history, mark_as_best, get_best_variants, save_competitor_analysis
from memory_manager import MemoryManager
from firecrawl_scraper import CompetitorScraper
from optimizer import ProductOptimizer
from utils import (
    calculate_seo_score, format_variant_for_display, format_variant_as_json,
    get_score_color, get_score_label,
)


load_dotenv()

# ─── Landing Page Logic ─────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "landing"

def show_landing():
    st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:80vh;">
            <h1 style="font-size:3rem;margin-bottom:0.5rem;">ContentBoost AI</h1>
            <p style="font-size:1.2rem;color:#64748b;max-width:500px;text-align:center;">
                Supercharge your product descriptions with AI-powered optimization, competitor analysis, and SEO insights.<br><br>
                <b>Welcome to ContentBoost AI.</b>
            </p>
            <img src="https://img.icons8.com/ios-filled/100/4F46E5/artificial-intelligence.png" width="100" style="margin:2rem 0;"/>
            <form>
                <button style="background:#4F46E5;color:white;padding:0.8rem 2.5rem;border:none;border-radius:8px;font-size:1.1rem;cursor:pointer;" type="submit">Enter App</button>
            </form>
        </div>
    """, unsafe_allow_html=True)
    if st.form_submit_button("Enter App", use_container_width=True):
        st.session_state.page = "main"

if st.session_state.page == "landing":

/* Global */
        st.markdown("""
            <div style=\"display:flex;flex-direction:column;align-items:center;justify-content:center;height:80vh;\">
                <h1 style=\"font-size:3rem;margin-bottom:0.5rem;\">ContentBoost AI</h1>
                <p style=\"font-size:1.2rem;color:#64748b;max-width:500px;text-align:center;\">
                    Supercharge your product descriptions with AI-powered optimization, competitor analysis, and SEO insights.<br><br>
                    <b>Welcome to ContentBoost AI.</b>
                </p>
                <img src=\"https://img.icons8.com/ios-filled/100/4F46E5/artificial-intelligence.png\" width=\"100\" style=\"margin:2rem 0;\"/>
            </div>
        """, unsafe_allow_html=True)
        with st.form("landing_form"):
            submitted = st.form_submit_button("Enter App", use_container_width=True)
            if submitted:
                st.session_state.page = "main"

    # All CSS must be inside a string passed to st.markdown, not as raw code
    background: linear-gradient(145deg, #1e1b4b, #1a1a2e);
    border-radius: 14px; padding: 1.5rem; margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.06);
    transition: transform 0.2s, box-shadow 0.2s;
}
.variant-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.3); }

/* Score badge */
.score-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 1rem;
}

/* Variant type pills */
.variant-type {
    display: inline-block; padding: 3px 12px; border-radius: 10px;
    font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
}
.type-seo { background: rgba(16,185,129,0.15); color: #34d399; }
.type-conversion { background: rgba(59,130,246,0.15); color: #60a5fa; }
.type-brand { background: rgba(168,85,247,0.15); color: #c084fc; }

/* Insight card */
.insight-card {
    background: rgba(30,27,75,0.5); border-radius: 10px; padding: 1rem;
    border: 1px solid rgba(255,255,255,0.05); margin-bottom: 0.75rem;
}
.insight-card h4 { color: #a5b4fc; margin: 0 0 0.5rem 0; font-size: 0.85rem; }
.insight-card p, .insight-card li { color: #cbd5e1; font-size: 0.82rem; }

/* Section headers */
.section-title {
    color: #a5b4fc; font-size: 0.85rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.8rem;
}

/* Bullet points in variants */
.bullet-item {
    color: #e2e8f0; font-size: 0.85rem; padding: 4px 0; padding-left: 16px;
    position: relative; line-height: 1.5;
}
.bullet-item::before {
    content: "•"; position: absolute; left: 0; color: #818cf8;
}

/* History table */
.history-row {
    background: rgba(30,27,75,0.3); border-radius: 8px; padding: 0.8rem 1rem;
    margin-bottom: 0.5rem; border: 1px solid rgba(255,255,255,0.04);
}
</style>
""", unsafe_allow_html=True)


# ─── Initialize Services ───────────────────────────────
@st.cache_resource
def init_services():
    """Initialize all service instances (cached across reruns)."""
    return {
        "memory": MemoryManager(),
        "scraper": CompetitorScraper(),
        "optimizer": ProductOptimizer(),
    }

services = init_services()
memory_mgr = services["memory"]
scraper = services["scraper"]
optimizer = services["optimizer"]

# Determine mode
is_live = optimizer.is_available()
mode_label = "LIVE" if is_live else "DEMO"
mode_class = "mode-live" if is_live else "mode-demo"

# ─── Session State Defaults ─────────────────────────────
defaults = {
    "variants": [], "competitor_analysis": {}, "memory_context": "",
    "scores": [], "processing": False, "current_product": "",
    "competitor_data": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Header ─────────────────────────────────────────────
def render_header():
    """Render the application header with mode indicator and API status."""
    api_pills = ""
    for name, check in [("Claude", optimizer.is_available()), ("Firecrawl", scraper.is_available()), ("mem0", memory_mgr.is_available())]:
        cls = "api-on" if check else "api-off"
        icon = "*" if check else "o"
        api_pills += f'<span class="api-pill {cls}">{icon} {name}</span>'

    st.markdown(f"""
    <div class="app-header">
        <h1>ContentBoost AI <span class="mode-badge {mode_class}">{mode_label}</span></h1>
        <p>Product Description Optimization Engine — powered by AI competitor analysis & memory learning</p>
        <div class="api-status">{api_pills}</div>
    </div>
    """, unsafe_allow_html=True)

render_header()


# ─── Tabs ────────────────────────────────────────────────
tab_optimizer, tab_history = st.tabs(["Optimizer", "History"])


# ═══════════════════════════════════════════════════════
#  TAB 1: OPTIMIZER
# ═══════════════════════════════════════════════════════
with tab_optimizer:
    col_left, col_center, col_right = st.columns([1, 2, 1], gap="medium")

    # ─── Left Panel: Input Form ──────────────────────
    with col_left:
        st.markdown('<p class="section-title">Product Input</p>', unsafe_allow_html=True)

        with st.form("product_form", clear_on_submit=False):
            product_name = st.text_input("Product Name", placeholder="e.g., ProSound Elite Wireless Headphones")
            category = st.selectbox("Category", [
                "Electronics - Audio", "Electronics - Wearables", "Electronics - Accessories",
                "Sports & Fitness - Footwear", "Sports & Fitness - Equipment",
                "Home & Kitchen", "Beauty & Personal Care", "Fashion - Clothing",
                "Fashion - Accessories", "Health & Wellness", "Toys & Games", "Other"
            ])
            current_desc = st.text_area("Current Description", height=120, placeholder="Paste your current product description...")
            target_kw = st.text_input("Target Keywords", placeholder="wireless headphones, noise cancelling, bluetooth")
            
            st.markdown("**Competitor URLs** (up to 5)")
            urls = []
            for i in range(3):
                u = st.text_input(f"URL {i+1}", key=f"url_{i}", placeholder=f"https://competitor{i+1}.com/product", label_visibility="collapsed")
                if u.strip():
                    urls.append(u.strip())

            submitted = st.form_submit_button("Optimize", use_container_width=True, type="primary")

        if submitted and product_name:
            st.session_state.processing = True
            st.session_state.current_product = product_name
            keywords = [k.strip() for k in target_kw.split(",") if k.strip()] if target_kw else []

            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(pct: int, msg: str):
                progress_bar.progress(min(pct, 100))
                status_text.markdown(f"*{msg}*")

            try:
                # Step 1: Scrape competitors
                update_progress(5, "Scraping competitor pages...")
                comp_data = scraper.scrape_competitors(urls) if urls else scraper._get_demo_competitor_data()
                st.session_state.competitor_data = comp_data

                # Steps 2-4: Run optimization pipeline
                result = optimizer.optimize(
                    product_name=product_name,
                    category=category,
                    current_description=current_desc,
                    target_keywords=keywords,
                    competitor_data=comp_data,
                    memory_manager=memory_mgr,
                    progress_callback=update_progress,
                )

                # Recalculate scores with user keywords
                for v in result["variants"]:
                    v["seo_score"] = calculate_seo_score(v, keywords)

                st.session_state.variants = result["variants"]
                st.session_state.competitor_analysis = result["competitor_analysis"]
                st.session_state.memory_context = result["memory_context"]
                st.session_state.scores = [v["seo_score"] for v in result["variants"]]

            except Exception as e:
                st.error(f"Optimization failed: {str(e)}")
            finally:
                st.session_state.processing = False
                progress_bar.empty()
                status_text.empty()

        elif submitted and not product_name:
            st.warning("Please enter a product name.")

        # Demo data loader
        if not st.session_state.variants:
            st.markdown("---")
            st.markdown("**Quick Demo**")
            if st.button("Load Sample Data", use_container_width=True):
                try:
                    fixtures_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_products.json")
                    with open(fixtures_path, "r", encoding="utf-8") as f:
                        fixtures = json.load(f)
                    sample = fixtures[0]
                    keywords = sample.get("target_keywords", [])
                    demo_variants = sample.get("demo_variants", [])
                    for v in demo_variants:
                        v["seo_score"] = calculate_seo_score(v, keywords)
                    st.session_state.variants = demo_variants
                    st.session_state.competitor_analysis = sample.get("demo_competitor_analysis", {})
                    st.session_state.competitor_data = sample.get("competitor_data", [])
                    st.session_state.memory_context = "Demo mode — no memory history available."
                    st.session_state.current_product = sample["product_name"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load demo data: {e}")

    # ─── Center Panel: Generated Variants ────────────
    with col_center:
        st.markdown('<p class="section-title">Generated Variants</p>', unsafe_allow_html=True)

        if not st.session_state.variants:
            st.markdown("""
            <div class="variant-card" style="text-align:center; padding: 3rem;">
                <p style="color: #a5b4fc; font-size: 1.1rem; font-weight: 600;">Ready to Optimize</p>
                <p style="color: #64748b; font-size: 0.85rem;">Fill in the product form and click Optimize,<br>or load sample data to see a demo.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            type_styles = {
                "seo": ("SEO-Focused", "type-seo"),
                "conversion": ("Conversion-Focused", "type-conversion"),
                "brand": ("Brand-Differentiated", "type-brand"),
            }

            for idx, variant in enumerate(st.session_state.variants):
                vtype = variant.get("variant_type", "seo")
                label, css_class = type_styles.get(vtype, ("Variant", "type-seo"))
                score = variant.get("seo_score", 0)
                score_color = get_score_color(score)
                score_label = get_score_label(score)

                st.markdown(f"""
                <div class="variant-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                        <span class="variant-type {css_class}">{label}</span>
                        <span class="score-badge" style="background:rgba({','.join(str(int(score_color.lstrip('#')[i:i+2],16)) for i in (0,2,4))},0.15); color:{score_color}; border:1px solid {score_color}40;">
                            {score}/100 · {score_label}
                        </span>
                    </div>
                    <h3 style="color:#e2e8f0; font-size:1.05rem; margin-bottom:0.75rem;">{variant.get('title','')}</h3>
                    <p style="color:#94a3b8; font-size:0.85rem; font-style:italic; margin-bottom:1rem;">{variant.get('short_description','')}</p>
                    <p style="color:#cbd5e1; font-size:0.84rem; line-height:1.7; margin-bottom:1rem;">{variant.get('long_description','')[:600]}{'...' if len(variant.get('long_description',''))>600 else ''}</p>
                </div>
                """, unsafe_allow_html=True)

                # Bullet points
                bullets = variant.get("bullet_points", [])
                if bullets:
                    with st.expander(f"Bullet Points ({len(bullets)})"):
                        for bp in bullets:
                            st.markdown(f"- {bp}")

                # Meta & Keywords
                with st.expander("SEO Details"):
                    st.markdown(f"**Meta Description:** {variant.get('meta_description', 'N/A')}")
                    kws = variant.get("seo_keywords", [])
                    if kws:
                        st.markdown(f"**Keywords:** {', '.join(kws)}")

                # Action buttons
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button(f"Copy Text", key=f"copy_{idx}", use_container_width=True):
                        copy_text = format_variant_for_display(variant)
                        st.code(copy_text, language=None)
                with bcol2:
                    if st.button(f"Save Best", key=f"save_{idx}", use_container_width=True):
                        try:
                            row_id = save_optimization(
                                product_name=st.session_state.current_product,
                                category="",
                                original_description="",
                                variant_type=vtype,
                                generated_title=variant.get("title", ""),
                                short_description=variant.get("short_description", ""),
                                long_description=variant.get("long_description", ""),
                                bullet_points=variant.get("bullet_points", []),
                                meta_description=variant.get("meta_description", ""),
                                seo_keywords=variant.get("seo_keywords", []),
                                seo_score=score,
                                is_best=True,
                            )
                            memory_mgr.store_description(
                                st.session_state.current_product, "", vtype,
                                variant.get("long_description", ""), score
                            )
                            st.success(f"Saved as best variant! (ID: {row_id})")
                        except Exception as e:
                            st.error(f"Failed to save: {e}")

                st.markdown("---")

    # ─── Right Panel: Insights ───────────────────────
    with col_right:
        # Competitor Insights
        st.markdown('<p class="section-title">Competitor Insights</p>', unsafe_allow_html=True)
        analysis = st.session_state.competitor_analysis
        if analysis:
            if analysis.get("tone"):
                st.markdown(f"""<div class="insight-card"><h4>Tone & Voice</h4><p>{analysis['tone']}</p></div>""", unsafe_allow_html=True)
            
            usps = analysis.get("usps", [])
            if usps:
                usp_html = "".join(f"<li>{u}</li>" for u in usps[:5])
                st.markdown(f"""<div class="insight-card"><h4>Key USPs</h4><ul>{usp_html}</ul></div>""", unsafe_allow_html=True)
            
            gaps = analysis.get("gaps", [])
            if gaps:
                gap_html = "".join(f"<li>{g}</li>" for g in gaps[:4])
                st.markdown(f"""<div class="insight-card"><h4>Opportunity Gaps</h4><ul>{gap_html}</ul></div>""", unsafe_allow_html=True)

            kw_patterns = analysis.get("keyword_patterns", [])
            if kw_patterns:
                kw_html = ", ".join(f"<code>{k}</code>" for k in kw_patterns[:8])
                st.markdown(f"""<div class="insight-card"><h4>Keyword Patterns</h4><p>{kw_html}</p></div>""", unsafe_allow_html=True)
        else:
            st.info("Run an optimization to see competitor insights.")

        # Competitor raw data
        comp_data = st.session_state.competitor_data
        if comp_data:
            st.markdown('<p class="section-title" style="margin-top:1.5rem;">Scraped Competitors</p>', unsafe_allow_html=True)
            for cd in comp_data[:5]:
                with st.expander(cd.get("title", "Competitor")[:40]):
                    st.markdown(f"**URL:** {cd.get('url', 'N/A')}")
                    st.markdown(f"{cd.get('description', '')[:200]}...")

        # Memory History
        st.markdown('<p class="section-title" style="margin-top:1.5rem;">Memory Context</p>', unsafe_allow_html=True)
        mem_ctx = st.session_state.memory_context
        if mem_ctx and mem_ctx != "No previous optimization history available for this product type.":
            st.markdown(f"""<div class="insight-card"><p>{mem_ctx[:500]}</p></div>""", unsafe_allow_html=True)
        else:
            st.info("Memory context builds over time as you save best variants.")


# ═══════════════════════════════════════════════════════
#  TAB 2: HISTORY
# ═══════════════════════════════════════════════════════
with tab_history:
    st.markdown('<p class="section-title">Optimization History</p>', unsafe_allow_html=True)

    hcol1, hcol2 = st.columns([2, 1])

    with hcol1:
        st.markdown("### All Past Optimizations")
        history = get_history(limit=30)
        if history:
            for record in history:
                best_icon = "*" if record.get("is_best") else ""
                score = record.get("seo_score", 0)
                sc = get_score_color(score)
                st.markdown(f"""
                <div class="history-row">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong style="color:#e2e8f0;">{best_icon}{record.get('product_name','')}</strong>
                            <span class="variant-type type-{record.get('variant_type','seo')}" style="margin-left:8px;">
                                {record.get('variant_type','').upper()}
                            </span>
                        </div>
                        <span class="score-badge" style="background:rgba(99,102,241,0.12); color:{sc}; font-size:0.8rem;">
                            {score}/100
                        </span>
                    </div>
                    <p style="color:#94a3b8; font-size:0.78rem; margin:0.3rem 0 0 0;">
                        {record.get('generated_title','')[:80]}
                    </p>
                    <p style="color:#64748b; font-size:0.7rem; margin:0.2rem 0 0 0;">
                        {record.get('created_at','')[:19]}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No optimization history yet. Generate and save variants to build your history.")

    with hcol2:
        st.markdown("### Best Variants")
        best = get_best_variants(limit=10)
        if best:
            for record in best:
                score = record.get("seo_score", 0)
                st.markdown(f"""
                <div class="insight-card">
                    <h4>{record.get('product_name','')}</h4>
                    <p><strong>{record.get('generated_title','')[:60]}</strong></p>
                    <p>Score: {score}/100 | Type: {record.get('variant_type','').upper()}</p>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("View Details"):
                    st.write(record.get("long_description", ""))
                    bps = record.get("bullet_points", [])
                    if bps:
                        for bp in bps:
                            st.markdown(f"• {bp}")
        else:
            st.info("Save your best variants to see them here.")


# ─── Footer ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#475569; font-size:0.75rem;">'
    'ContentBoost AI v1.0 — Built with Streamlit, Claude, Firecrawl & mem0'
    '</p>',
    unsafe_allow_html=True,
)
