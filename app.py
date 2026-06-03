"""DeepResearch — Autonomous Literature Review Agent"""
import streamlit as st
import uuid, json, os, time, threading
from datetime import datetime

st.set_page_config(page_title="DeepResearch Agent", page_icon="🔬",
                   layout="wide", initial_sidebar_state="collapsed")

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:8]
if "results" not in st.session_state:
    st.session_state.results = None
if "run_count" not in st.session_state:
    st.session_state.run_count = 0

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#F0F4F8;}
[data-testid="collapsedControl"]{display:none!important;}
section[data-testid="stSidebar"]{display:none!important;}
.topnav{background:linear-gradient(135deg,#0F2744,#1A3A5C);border-radius:14px;padding:1.2rem 2rem;display:flex;align-items:center;justify-content:space-between;margin-bottom:1.5rem;box-shadow:0 4px 20px rgba(15,39,68,0.3);}
.topnav-title{font-family:'DM Serif Display',serif;font-size:1.8rem;color:white;margin:0;}
.topnav-sub{color:#7BAFD4;font-size:0.8rem;margin-top:2px;}
.nbadge{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.18);color:#A8D4F0;border-radius:20px;padding:0.18rem 0.65rem;font-size:0.7rem;font-weight:500;}
.card{background:white;border-radius:14px;padding:1.5rem 1.75rem;box-shadow:0 1px 4px rgba(0,0,0,0.06);margin-bottom:1rem;}
.card-title{font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#1A3A5C;margin-bottom:0.9rem;padding-bottom:0.6rem;border-bottom:2px solid #EFF3F7;}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stSelectbox>div>div{background:#F8FAFC!important;border:1.5px solid #E2E8F0!important;border-radius:9px!important;font-size:0.9rem!important;color:#1E293B!important;}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:#1A3A5C!important;box-shadow:0 0 0 3px rgba(26,58,92,0.08)!important;}
label{font-size:0.78rem!important;font-weight:600!important;color:#475569!important;text-transform:uppercase!important;letter-spacing:0.05em!important;}
.stButton>button{background:linear-gradient(135deg,#1A3A5C,#0F2744)!important;color:white!important;border:none!important;border-radius:11px!important;font-size:1rem!important;font-weight:600!important;padding:0.75rem 2rem!important;transition:all 0.2s!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 20px rgba(15,39,68,0.3)!important;}
.metric-strip{display:flex;gap:0.75rem;margin-bottom:1.2rem;flex-wrap:wrap;}
.mbox{background:white;border-radius:11px;padding:0.9rem 1.2rem;flex:1;min-width:110px;box-shadow:0 1px 3px rgba(0,0,0,0.06);border-top:3px solid #1A3A5C;}
.mval{font-size:1.5rem;font-weight:700;color:#1A3A5C;line-height:1;}
.mlbl{font-size:0.68rem;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;margin-top:3px;}
.score-bar{height:8px;border-radius:4px;background:#E2E8F0;margin-top:6px;}
.score-fill{height:8px;border-radius:4px;background:linear-gradient(90deg,#1A3A5C,#3B82F6);}
.gap-card{border-radius:10px;padding:1rem 1.2rem;margin-bottom:0.6rem;border-left:4px solid #1A3A5C;}
.gap-high{background:#FEF2F2;border-left-color:#DC2626;}
.gap-medium{background:#FFFBEB;border-left-color:#D97706;}
.gap-low{background:#F0FDF4;border-left-color:#16A34A;}
.paper-card{background:#F8FAFC;border-radius:10px;padding:0.8rem 1rem;margin-bottom:0.5rem;border:0.5px solid #E2E8F0;}
.cluster-badge{display:inline-block;background:#EBF5FB;color:#1A5276;border:1px solid #AED6F1;border-radius:20px;padding:0.15rem 0.6rem;font-size:0.7rem;font-weight:500;margin-right:4px;}
.disclaimer{background:#FFFBEB;border:1px solid #FCD34D;border-radius:10px;padding:0.8rem 1.1rem;font-size:0.82rem;color:#92400E;margin-top:1rem;}
.stTabs [data-baseweb="tab-list"]{background:#F1F5F9;border-radius:10px;padding:4px;gap:2px;}
.stTabs [data-baseweb="tab"]{border-radius:8px;font-weight:500;font-size:0.87rem;}
.stTabs [aria-selected="true"]{background:white!important;box-shadow:0 1px 4px rgba(0,0,0,0.1)!important;color:#1A3A5C!important;font-weight:600!important;}
.welcome{background:white;border-radius:16px;padding:3rem 2rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);}
.feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin-top:1.5rem;text-align:left;}
.feat{background:#F8FAFC;border-radius:10px;padding:0.85rem 1rem;border:1px solid #E2E8F0;font-size:0.83rem;color:#334155;}
.feat strong{color:#1A3A5C;display:block;margin-bottom:0.2rem;}
</style>
""", unsafe_allow_html=True)

# Top nav
st.markdown("""
<div class="topnav">
  <div>
    <div class="topnav-title">🔬 DeepResearch Agent</div>
    <div class="topnav-sub">Autonomous Literature Review · LangGraph + Multi-Source RAG</div>
  </div>
  <div style="display:flex;gap:0.4rem;flex-wrap:wrap">
    <span class="nbadge">📚 PubMed</span>
    <span class="nbadge">🧬 ArXiv</span>
    <span class="nbadge">🎓 Semantic Scholar</span>
    <span class="nbadge">🔗 CrossRef</span>
    <span class="nbadge">🌍 OpenAlex</span>
    <span class="nbadge">🔍 Gap Analysis</span>
    <span class="nbadge">🇵🇰 Urdu</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Input form
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔍 Research Topic</div>', unsafe_allow_html=True)
    topic = st.text_area("Enter your research topic",
        placeholder="e.g. Large Language Models in Clinical Decision Support\ne.g. Deep Learning for Urdu Natural Language Processing\ne.g. Autonomous Vehicles Safety in Urban Environments",
        height=120, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚙️ Configuration</div>', unsafe_allow_html=True)
    max_papers = st.slider("Max papers", 10, 40, 20, 5)
    language = st.selectbox("Language", ["English only", "Bilingual (English + Urdu)"])
    lang_code = "bilingual" if "Urdu" in language else "english"
    efficient_mode = st.toggle("⚡ Token-efficient mode", value=True,
        help="ON: 1 LLM call (~3K tokens/run, 30+ runs/day)\nOFF: Per-section (~15K tokens, 6 runs/day)")
    if efficient_mode:
        st.markdown('<div style="font-size:0.75rem;color:#16A34A">⚡ ~3,000 tokens/run · 30+ runs/day</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:0.75rem;color:#D97706">🔋 ~15,000 tokens/run · 6 runs/day</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Sources</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.82rem;font-weight:600;color:#1A3A5C;margin-bottom:0.4rem">5 sources active:</div>', unsafe_allow_html=True)
    st.markdown("""
    - 📚 PubMed (NCBI)
    - 🧬 ArXiv
    - 🎓 Semantic Scholar
    - 🔗 CrossRef
    - 🌍 OpenAlex
    """)
    st.markdown('<div style="font-size:0.75rem;color:#16A34A;margin-top:0.3rem">✓ All free — no API keys needed</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

col_btn, col_clr = st.columns([6, 1])
with col_btn:
    run_btn = st.button("🔬 Generate Literature Review", type="primary", use_container_width=True)
with col_clr:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.results = None
        st.rerun()

# Run pipeline
if run_btn:
    if not topic.strip():
        st.warning("⚠️ Please enter a research topic.")
    else:
        _sid = st.session_state.get("session_id", "default")
        result_holder, error_holder = {}, {}

        def _run():
            try:
                from graph import run_deepresearch
                # Apply efficient mode to settings
                import os
                os.environ["EFFICIENT_MODE"] = "true" if efficient_mode else "false"
                os.environ["MAX_PAPERS"] = str(max_papers)
                # Clear settings cache so new values take effect
                from utils.config import get_settings
                get_settings.cache_clear()
                result_holder["state"] = run_deepresearch(
                    topic=topic.strip(), language=lang_code,
                    max_papers=max_papers, session_id=_sid,
                )
            except Exception as e:
                import traceback
                error_holder["err"] = e
                error_holder["tb"] = traceback.format_exc()

        steps = [
            (10, "🔍 Expanding search queries..."),
            (25, "📚 Searching PubMed..."),
            (40, "🧬 Searching ArXiv..."),
            (52, "🎓 Searching Semantic Scholar..."),
            (65, "🔗 Clustering papers by theme..."),
            (75, "🕳 Detecting research gaps..."),
            (83, "✍️ Writing literature review sections..."),
            (93, "🔎 Critic reviewing quality..."),
        ]
        progress = st.progress(0, text="🚀 Starting DeepResearch pipeline...")
        t = threading.Thread(target=_run)
        t.start()
        for pct, msg in steps:
            time.sleep(3.5)
            if not t.is_alive():
                break
            progress.progress(pct, text=msg)
        t.join(timeout=300)
        progress.progress(100, text="✅ Literature review complete!")
        time.sleep(0.4)
        progress.empty()

        if error_holder:
            err_str = str(error_holder['err'])
            if "429" in err_str or "rate_limit" in err_str.lower():
                st.error("⏱️ Groq rate limit reached. Options:")
                st.markdown("""
                - **Wait 20 minutes** then try again (free daily limit resets)
                - **Switch model**: add `GROQ_MODEL=llama-3.1-8b-instant` to your `.env`
                - **Reduce papers**: use the slider above (try 10 papers)
                - **Enable ⚡ Token-efficient mode** (toggle above)
                """)
            else:
                st.error(f"Pipeline error: {error_holder['err']}")
                st.code(error_holder.get("tb", ""))
        else:
            st.session_state.results = result_holder["state"]
            st.session_state.run_count += 1
            st.rerun()

# Results
if st.session_state.results:
    state = st.session_state.results
    papers = state.get("filtered_papers", [])
    gaps = state.get("research_gaps", [])
    clusters = state.get("clusters", {})
    sections = state.get("sections", [])
    score = state.get("critic_score", 0)
    directions = state.get("future_directions", [])

    # Metric strip
    score_color = "#16A34A" if score >= 7.5 else "#D97706" if score >= 6 else "#DC2626"
    st.markdown(f"""
    <div class="metric-strip">
      <div class="mbox"><div class="mval">{len(papers)}</div><div class="mlbl">Papers analyzed</div></div>
      <div class="mbox"><div class="mval">{len(clusters)}</div><div class="mlbl">Themes found</div></div>
      <div class="mbox"><div class="mval">{len(gaps)}</div><div class="mlbl">Research gaps</div></div>
      <div class="mbox"><div class="mval">{len(sections)}</div><div class="mlbl">Sections written</div></div>
      <div class="mbox" style="border-top-color:{score_color}">
        <div class="mval" style="color:{score_color}">{score:.1f}/10</div>
        <div class="mlbl">Quality score</div>
        <div class="score-bar"><div class="score-fill" style="width:{score*10}%"></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tabs = st.tabs(["📋 Full Review", "📄 Sections", "🕳 Gaps & Themes",
                    "📚 Papers", "🔗 Citation Network", "📊 Debug"])

    with tabs[0]:
        # Download buttons at top for easy access
        dl1, dl2, dl3 = st.columns(3)
        with dl1:
            try:
                from utils.report_exporter import export_docx
                st.download_button("📥 Download .docx", data=export_docx(state),
                    file_name=f"deepresearch_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True)
            except Exception as e:
                st.warning(f"Export error: {e}")
        with dl2:
            st.download_button("📥 Download JSON",
                data=json.dumps({k:v for k,v in state.items() if k != "messages"}, indent=2, default=str),
                file_name=f"deepresearch_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json", use_container_width=True)
        with dl3:
            if st.button("🔄 New Research", use_container_width=True):
                st.session_state.results = None
                st.rerun()

        st.markdown("---")

        review = state.get("final_review", "")
        if not papers:
            st.warning("⚠️ No papers retrieved. Check the **Papers** and **Debug** tabs.")
        if review:
            st.markdown(review)
        else:
            st.info("No review generated yet.")

        st.markdown("---")
        st.markdown('<div class="disclaimer">⚕️ <strong>Disclaimer:</strong> AI-generated literature review. Verify all citations and claims before academic submission.</div>', unsafe_allow_html=True)

    with tabs[1]:
        if sections:
            for sec in sections:
                with st.expander(f"📄 {sec['title']}", expanded=False):
                    st.markdown(sec["content"])
                    if sec.get("urdu_summary"):
                        st.markdown(f'<div style="background:#F0F9FF;border-left:3px solid #0EA5E9;border-radius:8px;padding:0.75rem 1rem;margin-top:0.5rem"><strong>اردو خلاصہ:</strong> {sec["urdu_summary"]}</div>', unsafe_allow_html=True)
                    if sec.get("papers_cited"):
                        st.markdown("**Papers cited:** " + " · ".join(sec["papers_cited"][:5]))
        else:
            st.info("No sections generated.")

    with tabs[2]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🕳 Research Gaps")
            if gaps:
                for g in gaps:
                    priority = g.get("priority", "medium")
                    icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
                    st.markdown(f'<div class="gap-card gap-{priority}"><strong>{icon} {g["gap"]}</strong><br><small style="color:#475569">{g.get("evidence","")}</small><br><em style="color:#64748B;font-size:0.82rem">Opportunity: {g.get("opportunity","")}</em></div>', unsafe_allow_html=True)
            else:
                st.info("No gaps detected.")
        with c2:
            st.markdown("### 🔮 Future Directions")
            if directions:
                for i, d in enumerate(directions, 1):
                    st.markdown(f'<div style="background:#F8FAFC;border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.5rem;border-left:3px solid #1A3A5C"><strong>{i}.</strong> {d}</div>', unsafe_allow_html=True)
            themes = state.get("themes", [])
            if themes:
                st.markdown("### 🏷 Key Themes")
                for t in themes:
                    st.markdown(f'<span style="display:inline-block;background:#EBF5FB;color:#1A5276;border:1px solid #AED6F1;border-radius:20px;padding:0.25rem 0.75rem;font-size:0.82rem;margin:3px">{t}</span>', unsafe_allow_html=True)

    with tabs[3]:
        st.markdown(f"### 📚 {len(papers)} Papers Analyzed")
        if not papers:
            st.error("No papers found. Check the Debug tab for details — your NCBI_EMAIL may be missing from .env, or the APIs may be temporarily unavailable.")
        sources = {"pubmed": 0, "arxiv": 0, "semantic_scholar": 0, "crossref": 0, "openalex": 0}
        for p in papers:
            s = p.get("source", "")
            if s in sources:
                sources[s] += 1
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        sc1.metric("PubMed", sources["pubmed"])
        sc2.metric("ArXiv", sources["arxiv"])
        sc3.metric("Semantic Scholar", sources["semantic_scholar"])
        sc4.metric("CrossRef", sources["crossref"])
        sc5.metric("OpenAlex", sources["openalex"])

        for cluster_name, indices in clusters.items():
            with st.expander(f"🗂 {cluster_name} ({len(indices)} papers)"):
                for idx_str in indices:
                    try:
                        idx = int(idx_str)
                        if idx < len(papers):
                            p = papers[idx]
                            st.markdown(
                                f'<div class="paper-card">'
                                f'<strong>{p["title"]}</strong><br>'
                                f'<small style="color:#64748B">{", ".join(p["authors"][:3])} · {p["year"]} · '
                                f'{p["source"].upper()} · ⭐ {p.get("citations",0)} citations</small><br>'
                                f'<small>{p["abstract"][:200]}...</small>'
                                f'{"<br><a href=" + repr(p["url"]) + " target=_blank style=color:#2563EB>↗ Open paper</a>" if p.get("url") else ""}'
                                f'</div>', unsafe_allow_html=True)
                    except (ValueError, TypeError):
                        pass

    with tabs[4]:
        st.markdown("### 🔗 Citation Network")
        network = state.get("citation_network", {})
        if network and papers:
            try:
                import plotly.graph_objects as go
                import networkx as nx
                G = nx.Graph()
                for i, p in enumerate(papers[:20]):
                    G.add_node(str(i), title=p["title"][:40], source=p["source"], year=p.get("year",0))
                for node, neighbors in network.items():
                    for nb in neighbors:
                        if nb != node:
                            G.add_edge(node, nb)
                pos = nx.spring_layout(G, seed=42)
                edge_x, edge_y = [], []
                for e in G.edges():
                    x0,y0 = pos[e[0]]; x1,y1 = pos[e[1]]
                    edge_x += [x0,x1,None]; edge_y += [y0,y1,None]
                node_x = [pos[n][0] for n in G.nodes()]
                node_y = [pos[n][1] for n in G.nodes()]
                labels = [G.nodes[n]["title"] for n in G.nodes()]
                colors_map = {"pubmed":"#3B82F6","arxiv":"#10B981","semantic_scholar":"#8B5CF6"}
                node_colors = [colors_map.get(G.nodes[n]["source"],"#94A3B8") for n in G.nodes()]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=edge_x,y=edge_y,mode="lines",
                    line=dict(width=0.8,color="#CBD5E1"),hoverinfo="none"))
                fig.add_trace(go.Scatter(x=node_x,y=node_y,mode="markers+text",
                    marker=dict(size=12,color=node_colors,line=dict(width=1,color="white")),
                    text=labels,textposition="top center",textfont=dict(size=9),
                    hovertext=labels,hoverinfo="text"))
                fig.update_layout(showlegend=False,
                    plot_bgcolor="white",paper_bgcolor="white",
                    margin=dict(l=20,r=20,t=20,b=20),height=450,
                    xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
                    yaxis=dict(showgrid=False,zeroline=False,showticklabels=False))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('<small style="color:#64748B">🔵 PubMed · 🟢 ArXiv · 🟣 Semantic Scholar · Lines = shared keywords</small>', unsafe_allow_html=True)
            except Exception as e:
                st.info(f"Network visualization unavailable: {e}")
        else:
            st.info("No citation network data.")

    with tabs[5]:
        st.markdown("**Search queries used:**")
        for q in state.get("search_queries", []):
            st.code(q)
        st.markdown("**Source breakdown:**")
        src_counts = {}
        for p in papers:
            s = p.get("source","?")
            src_counts[s] = src_counts.get(s,0) + 1
        st.json(src_counts)
        st.markdown("**Quality assessment:**")
        st.info(state.get("critic_feedback", "No feedback."))
        st.markdown("**Raw state (debug):**")
        st.json({k:v for k,v in state.items() if k not in ("messages","final_review","sections")})

elif not run_btn:
    st.markdown("""
    <div class="welcome">
      <div style="font-size:3.5rem">🔬</div>
      <h3 style="font-family:'DM Serif Display',serif;color:#1A3A5C;font-size:1.6rem;margin:0.75rem 0 0.4rem">Autonomous Literature Review</h3>
      <p style="color:#64748B">Enter a research topic above and DeepResearch will autonomously search academic databases, cluster papers, detect gaps, and write a complete literature review.</p>
      <div class="feat-grid">
        <div class="feat"><strong>📚 5-source search</strong>PubMed · ArXiv · Semantic Scholar · CrossRef · OpenAlex</div>
        <div class="feat"><strong>🔗 Smart clustering</strong>Groups papers into themes automatically</div>
        <div class="feat"><strong>🕳 Gap detection</strong>Finds what hasn't been studied yet</div>
        <div class="feat"><strong>✍️ Academic writing</strong>Full prose, not bullet points</div>
        <div class="feat"><strong>🔎 Critic review</strong>Self-evaluates and revises if needed</div>
        <div class="feat"><strong>🇵🇰 Urdu support</strong>Bilingual summaries for every section</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
