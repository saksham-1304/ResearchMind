# app.py
import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain, reviser_chain

# ── Page config ──
st.set_page_config(page_title="ResearchMind | Agentic AI", page_icon="🔬", layout="wide")

# ── Custom CSS (Ultra-Modern SaaS UI) ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@400;500;600&family=Syne:wght@700;800&display=swap');

/* Global Reset & Typography */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #f8fafc; }

/* Deep space background with glowing ambient orbs */
.stApp { 
    background-color: #09090b; 
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.08), transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.08), transparent 40%);
}

/* Hero Section */
.hero { padding: 1.5rem 0 2.5rem 0; text-align: center; }
.hero h1 { 
    font-family: 'Syne', sans-serif; 
    font-size: 4.5rem; 
    font-weight: 800; 
    color: #ffffff; 
    margin-bottom: 0;
    letter-spacing: -0.03em;
}
.hero h1 span { 
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub { color: #94a3b8; font-size: 1.15rem; font-weight: 400; margin-top: 0.5rem;}

/* Step Cards */
.step-card { 
    background: rgba(30, 41, 59, 0.3); 
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05); 
    border-radius: 12px; 
    padding: 1.25rem; 
    margin-bottom: 1rem; 
    border-left: 4px solid #334155;
    transition: all 0.3s ease;
}

/* Animations for Active Steps */
@keyframes pulse-border {
    0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
    100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}
@keyframes spin { 100% { transform: rotate(360deg); } }

.step-card.active { 
    border-left: 4px solid #3b82f6; 
    background: linear-gradient(90deg, rgba(59,130,246,0.1) 0%, rgba(0,0,0,0) 100%);
    border-right: 1px solid rgba(59, 130, 246, 0.2);
    border-top: 1px solid rgba(59, 130, 246, 0.2);
    border-bottom: 1px solid rgba(59, 130, 246, 0.2);
    animation: pulse-border 2s infinite;
}
.step-card.done { 
    border-left-color: #10b981; 
    background: rgba(16, 185, 129, 0.04); 
}

.step-title { color: #f1f5f9; font-size: 1.05rem; font-weight: 600; display: flex; align-items: center; gap: 8px;}
.step-desc { font-size: 0.85rem; color: #94a3b8; margin-top: 6px; display: block; }
.spinner {
    width: 16px; height: 16px;
    border: 2px solid rgba(59, 130, 246, 0.2);
    border-bottom-color: #3b82f6;
    border-radius: 50%;
    display: inline-block;
    animation: spin 1s linear infinite;
}

/* Live Execution Terminal */
.console-window {
    background-color: #020617;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1.25rem;
    font-family: 'Fira Code', monospace;
    font-size: 0.85rem;
    height: 330px;
    overflow-y: auto;
    box-shadow: inset 0 2px 15px rgba(0,0,0,0.5), 0 4px 20px rgba(0,0,0,0.2);
    display: flex;
    flex-direction: column;
}
.console-header {
    display: flex; gap: 6px; margin-bottom: 12px;
    padding-bottom: 12px; border-bottom: 1px solid #1e293b;
}
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot-red { background-color: #ef4444; }
.dot-yellow { background-color: #eab308; }
.dot-green { background-color: #22c55e; }
.log-entry { margin-bottom: 6px; line-height: 1.5; color: #38bdf8; }
.log-success { color: #34d399; }
.log-dim { color: #64748b; }
.log-warn { color: #fbbf24; }

/* Input Fields & Buttons */
.stTextInput > div > div > input {
    background-color: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-radius: 8px !important;
    font-size: 1.05rem !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #60a5fa !important;
    box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2) !important;
}
.stButton > button { 
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important; 
    color: #ffffff !important; 
    font-weight: 600 !important; 
    font-size: 1.05rem !important;
    border: none !important; 
    border-radius: 8px !important; 
    padding: 0.5rem 1.5rem !important;
    height: 48px !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important; 
}

/* 🌟 NEW: Light Document Paper Style for Outputs 🌟 */
.light-paper {
    background-color: #ffffff;
    padding: 3rem;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    margin-top: 1rem;
    font-family: 'Inter', sans-serif;
}
/* Force text colors inside the paper to be dark and readable */
.light-paper, .light-paper p, .light-paper li, .light-paper span {
    color: #334155 !important;
    font-size: 1.05rem;
    line-height: 1.7;
}
.light-paper h1, .light-paper h2, .light-paper h3, .light-paper h4 {
    color: #0f172a !important;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
}
.light-paper strong { color: #000000 !important; font-weight: 700; }
.light-paper a { color: #2563eb !important; text-decoration: none; }
.light-paper a:hover { text-decoration: underline; }
.light-paper table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
.light-paper th, .light-paper td { border: 1px solid #cbd5e1; padding: 0.75rem; text-align: left; }
.light-paper th { background-color: #f1f5f9; color: #0f172a !important; }
</style>
""", unsafe_allow_html=True)

# ── Helper HTML Components ──
def get_step_html(title, state, desc):
    cls = "done" if state == "done" else "active" if state == "running" else "waiting"
    icon = "✓" if state == "done" else "⚡" if state == "running" else "⏳"
    spinner_html = '<span class="spinner"></span>' if state == "running" else ''
    
    # Compressed HTML to prevent Streamlit from breaking it
    return f'<div class="step-card {cls}"><div style="display: flex; justify-content: space-between; align-items: center;"><span class="step-title">{icon} {title}</span>{spinner_html}</div><span class="step-desc">{desc}</span></div>'

def get_terminal_html(logs):
    log_str = "".join(logs)
    return f"""
    <div class="console-window" id="console">
        <div class="console-header">
            <div class="dot dot-red"></div>
            <div class="dot dot-yellow"></div>
            <div class="dot dot-green"></div>
            <span style="color:#64748b; font-size:0.75rem; margin-left:10px;">agent_execution.log</span>
        </div>
        <div style="flex-grow: 1; display:flex; flex-direction:column; justify-content:flex-end;">
            {log_str}
        </div>
    </div>
    <script>
        var objDiv = document.getElementById("console");
        objDiv.scrollTop = objDiv.scrollHeight;
    </script>
    """

# ── Initialization ──
if "results" not in st.session_state:
    st.session_state.results = None

# ── UI Layout ──
st.markdown('<div class="hero"><h1>Research<span>Mind</span></h1><p class="hero-sub">Autonomous AI Research System</p></div>', unsafe_allow_html=True)

# Main columns
col_left, col_right = st.columns([1.1, 1], gap="large")

with col_left:
    topic = st.text_input("What would you like to research?", placeholder="e.g. Breakthroughs in Quantum Error Correction 2026")
    run_btn = st.button("🚀 Initialize AI Agents", use_container_width=True)
    
    st.markdown("<h4 style='color: #e2e8f0; margin-top:2rem; font-weight:600;'>Live Execution Stream</h4>", unsafe_allow_html=True)
    terminal_placeholder = st.empty()
    terminal_placeholder.markdown(get_terminal_html(["<div class='log-entry log-dim'>Waiting for input... System ready.</div>"]), unsafe_allow_html=True)

with col_right:
    st.markdown("<h4 style='color: #e2e8f0; margin-bottom: 1.2rem; font-weight: 600;'>Agentic Pipeline</h4>", unsafe_allow_html=True)
    step1_ph = st.empty()
    step2_ph = st.empty()
    step3_ph = st.empty()
    step4_ph = st.empty()
    step5_ph = st.empty()

def update_steps(running_step=None, completed_steps=[]):
    def get_s(name): return "done" if name in completed_steps else "running" if name == running_step else "waiting"
    step1_ph.markdown(get_step_html("1. Search Agent", get_s("search"), "Traversing the web for reliable sources"), unsafe_allow_html=True)
    step2_ph.markdown(get_step_html("2. Reader Agent", get_s("reader"), "Scraping full-text context from URLs"), unsafe_allow_html=True)
    step3_ph.markdown(get_step_html("3. Writer Agent", get_s("writer"), "Drafting the initial academic report"), unsafe_allow_html=True)
    step4_ph.markdown(get_step_html("4. Critic Agent", get_s("critic"), "Evaluating draft for flaws and citations"), unsafe_allow_html=True)
    step5_ph.markdown(get_step_html("5. Reviser Agent", get_s("reviser"), "Applying feedback for the perfect final report"), unsafe_allow_html=True)

if not st.session_state.results:
    update_steps()

# ── Execution Logic ──
if run_btn and topic:
    r = {}
    completed = []
    logs = ["<div class='log-entry'>[SYSTEM] Booting agent network...</div>"]
    
    def log(msg, kind="normal"):
        cls = "log-success" if kind=="success" else "log-dim" if kind=="dim" else "log-warn" if kind=="warn" else "log-entry"
        logs.append(f"<div class='{cls}'>{msg}</div>")
        terminal_placeholder.markdown(get_terminal_html(logs[-12:]), unsafe_allow_html=True)

    # 1. SEARCH
    update_steps("search", completed)
    log(f"-> [Agent 1] Initializing Search Agent for '{topic}'")
    time.sleep(0.5) 
    log("-> [Agent 1] Querying Tavily Search API...")
    
    search_agent = build_search_agent()
    res = search_agent.invoke({"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]})
    r["search"] = res["messages"][-1].content
    
    log("✓ [Agent 1] Search complete. Data collected.", "success")
    completed.append("search")
    
    # 2. READ
    update_steps("reader", completed)
    log("-> [Agent 2] Reader Agent spinning up...")
    log("-> [Agent 2] Identifying primary source URLs...")
    
    reader_agent = build_reader_agent()
    res = reader_agent.invoke({"messages": [("user", f"Based on these results, scrape the best URL:\n{r['search'][:800]}")]})
    r["reader"] = res["messages"][-1].content
    
    log("✓ [Agent 2] Scraped raw textual context.", "success")
    completed.append("reader")
    
    # 3. WRITE
    update_steps("writer", completed)
    log("-> [Agent 3] Writer Agent synthesizing data...")
    log("-> [Agent 3] Formatting as Academic Markdown...", "dim")
    
    r["writer"] = writer_chain.invoke({"topic": topic, "research": f"SEARCH:\n{r['search']}\nSCRAPED:\n{r['reader']}"})
    
    log("✓ [Agent 3] Initial Draft Generated.", "success")
    completed.append("writer")
    
    # 4. CRITIQUE
    update_steps("critic", completed)
    log("-> [Agent 4] Critic Agent inspecting structural integrity...")
    log("-> [Agent 4] Checking for hallucinations and citations...", "warn")
    
    r["critic"] = critic_chain.invoke({"report": r["writer"]})
    
    log("✓ [Agent 4] Critique formulated.", "success")
    completed.append("critic")

    # 5. REVISE
    update_steps("reviser", completed)
    log("-> [Agent 5] Reviser Agent integrating feedback...")
    log("-> [Agent 5] Polishing final document...", "dim")
    
    r["reviser"] = reviser_chain.invoke({"topic": topic, "report": r["writer"], "feedback": r["critic"]})
    
    log("✓ [Agent 5] Final document ready.", "success")
    log("★ [SYSTEM] Pipeline successfully completed.", "success")
    completed.append("reviser")
    
    update_steps(None, completed)
    st.session_state.results = r

# ── Results Display ──
if st.session_state.results:
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 3rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; margin-bottom:2rem;'>📑 Final Research Hub</h2>", unsafe_allow_html=True)
    
    r = st.session_state.results
    
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
        .stTabs [data-baseweb="tab"] { font-weight: 600; color: #94a3b8; }
        .stTabs [aria-selected="true"] { color: #3b82f6 !important; }
        </style>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🌟 Final Polish", "🧐 Critic's Feedback", "📝 Initial Draft", "📚 Raw Context"])
    
    with tab1:
        col1, col2 = st.columns([8,2])
        with col2:
            st.download_button("📥 Download (.md)", data=r["reviser"], file_name="Final_Report.md", use_container_width=True)
        # Empty newlines (\n\n) inside the div are required so Streamlit renders Markdown correctly inside HTML
        st.markdown(f'<div class="light-paper">\n\n{r["reviser"]}\n\n</div>', unsafe_allow_html=True)
        
    with tab2:
        st.info("The Critic Agent evaluated the initial draft and provided this exact feedback to the Reviser Agent to fix.")
        st.markdown(f'<div class="light-paper" style="border-top: 5px solid #eab308;">\n\n{r["critic"]}\n\n</div>', unsafe_allow_html=True)
        
    with tab3:
        st.warning("This was the first draft before the AI criticized and corrected itself.")
        st.markdown(f'<div class="light-paper" style="opacity: 0.9;">\n\n{r["writer"]}\n\n</div>', unsafe_allow_html=True)
        
    with tab4:
        with st.expander("🔍 View Search Logs"):
            st.code(r["search"], language="text")
        with st.expander("📄 View Scraped Data"):
            st.code(r["reader"], language="text")