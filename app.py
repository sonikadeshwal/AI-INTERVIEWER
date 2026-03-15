import streamlit as st
import groq
import json
import time
import re
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Interviewer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS / Animations ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #050810 !important;
    color: #e8eaf0 !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99,102,241,.18) 0%, transparent 70%),
                radial-gradient(ellipse 60% 40% at 80% 80%, rgba(16,185,129,.08) 0%, transparent 60%),
                #050810 !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { max-width: 1100px !important; padding: 2rem 2rem !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d0f18; }
::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 2px; }

/* ── HERO HEADER ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 2px;
    background: linear-gradient(90deg, transparent, #6366f1, #10b981, transparent);
    animation: scanline 3s ease-in-out infinite;
}
@keyframes scanline {
    0%, 100% { opacity: 0; }
    50% { opacity: 1; }
}
.hero-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: .72rem;
    letter-spacing: .2em;
    color: #10b981;
    border: 1px solid rgba(16,185,129,.35);
    padding: .3rem .9rem;
    border-radius: 2rem;
    margin-bottom: 1.4rem;
    background: rgba(16,185,129,.06);
    animation: fadeDown .6s ease both;
}
.hero h1 {
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -.03em;
    background: linear-gradient(135deg, #e8eaf0 20%, #6366f1 60%, #10b981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: fadeDown .7s .1s ease both;
}
.hero p {
    color: rgba(232,234,240,.45);
    font-size: 1rem;
    margin-top: .8rem;
    font-family: 'DM Mono', monospace;
    animation: fadeDown .7s .2s ease both;
}
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-18px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── GLASS CARDS ── */
.glass-card {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 16px;
    padding: 1.6rem;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
    transition: border-color .25s, transform .25s, box-shadow .25s;
    animation: riseIn .5s ease both;
}
.glass-card::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(99,102,241,.06) 0%, transparent 60%);
    pointer-events: none;
}
.glass-card:hover {
    border-color: rgba(99,102,241,.35);
    transform: translateY(-2px);
    box-shadow: 0 20px 60px rgba(99,102,241,.1);
}
@keyframes riseIn {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── SECTION LABELS ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: .68rem;
    letter-spacing: .2em;
    color: #6366f1;
    text-transform: uppercase;
    margin-bottom: .6rem;
}

/* ── METRIC GRID ── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.4rem 0;
}
.metric-box {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 12px;
    padding: 1.1rem 1rem;
    text-align: center;
    animation: riseIn .5s ease both;
    transition: transform .2s, border-color .2s;
}
.metric-box:hover { transform: scale(1.03); border-color: rgba(99,102,241,.4); }
.metric-val {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -.03em;
    line-height: 1;
}
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: .65rem;
    letter-spacing: .15em;
    color: rgba(232,234,240,.4);
    margin-top: .35rem;
    text-transform: uppercase;
}

/* ── SCORE RING ── */
.score-ring-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: .6rem;
    padding: 1.4rem 0;
}
.score-ring-wrap svg { overflow: visible; }

/* ── KEYWORD CHIP ── */
.chip-row { display: flex; flex-wrap: wrap; gap: .45rem; margin-top: .7rem; }
.chip {
    font-family: 'DM Mono', monospace;
    font-size: .7rem;
    padding: .22rem .65rem;
    border-radius: 3rem;
    border: 1px solid;
    letter-spacing: .04em;
    animation: popIn .3s ease both;
}
.chip-ok { background: rgba(16,185,129,.1); border-color: rgba(16,185,129,.4); color: #10b981; }
.chip-miss { background: rgba(239,68,68,.1); border-color: rgba(239,68,68,.3); color: #f87171; }
@keyframes popIn {
    from { opacity: 0; transform: scale(.8); }
    to   { opacity: 1; transform: scale(1); }
}

/* ── FEEDBACK BLOCK ── */
.fb-block {
    background: rgba(99,102,241,.06);
    border-left: 3px solid #6366f1;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    font-size: .92rem;
    line-height: 1.7;
    color: rgba(232,234,240,.85);
    margin-top: .8rem;
}

/* ── QUESTION BUBBLE ── */
.q-bubble {
    background: linear-gradient(135deg, rgba(99,102,241,.12), rgba(99,102,241,.04));
    border: 1px solid rgba(99,102,241,.25);
    border-radius: 0 14px 14px 14px;
    padding: 1.1rem 1.3rem;
    font-size: 1.05rem;
    line-height: 1.65;
    position: relative;
    animation: riseIn .4s ease both;
}
.q-bubble::before {
    content: 'Q';
    position: absolute;
    top: -1px; left: -1px;
    background: #6366f1;
    color: #fff;
    font-size: .7rem;
    font-weight: 700;
    padding: .15rem .35rem;
    border-radius: 4px 0 4px 0;
}

/* ── ANSWER BOX ── */
[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 12px !important;
    color: #e8eaf0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: .9rem !important;
    resize: vertical !important;
    transition: border-color .2s !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.15) !important;
    outline: none !important;
}

/* ── SELECTBOX & INPUTS ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: .9rem !important;
    letter-spacing: .03em !important;
    padding: .65rem 1.6rem !important;
    transition: all .2s !important;
    position: relative;
    overflow: hidden;
}
.stButton > button::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,.15), transparent);
    opacity: 0;
    transition: opacity .2s;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(99,102,241,.4) !important;
}
.stButton > button:hover::after { opacity: 1; }

/* ── PROGRESS ── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6366f1, #10b981) !important;
    border-radius: 4px !important;
    animation: progressGlow 2s ease infinite;
}
@keyframes progressGlow {
    0%, 100% { filter: brightness(1); }
    50% { filter: brightness(1.3); }
}

/* ── DIVIDER ── */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,.4), rgba(16,185,129,.3), transparent);
    margin: 1.5rem 0;
}

/* ── STEP TRACKER ── */
.steps {
    display: flex;
    justify-content: center;
    gap: 0;
    margin: 1.5rem 0 2rem;
    position: relative;
}
.steps::before {
    content: '';
    position: absolute;
    top: 14px; left: 15%; right: 15%;
    height: 1px;
    background: rgba(255,255,255,.08);
}
.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: .4rem;
    flex: 1;
    max-width: 160px;
    position: relative;
    z-index: 1;
}
.step-dot {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: .72rem;
    font-weight: 700;
    font-family: 'DM Mono', monospace;
    transition: all .3s;
}
.step-dot.active {
    background: #6366f1;
    box-shadow: 0 0 20px rgba(99,102,241,.6);
    animation: pulse 2s infinite;
}
.step-dot.done { background: #10b981; }
.step-dot.idle { background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12); color: rgba(232,234,240,.3); }
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(99,102,241,.6); }
    50% { box-shadow: 0 0 35px rgba(99,102,241,.9); }
}
.step-text {
    font-family: 'DM Mono', monospace;
    font-size: .62rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: rgba(232,234,240,.4);
}
.step-text.active { color: #6366f1; }
.step-text.done { color: #10b981; }

/* ── HISTORY ITEM ── */
.hist-item {
    border-left: 2px solid rgba(99,102,241,.3);
    padding: .7rem 1rem;
    margin-bottom: .8rem;
    transition: border-color .2s;
    animation: riseIn .4s ease both;
}
.hist-item:hover { border-color: #6366f1; }
.hist-q { font-size: .88rem; color: rgba(232,234,240,.6); margin-bottom: .3rem; }
.hist-score {
    font-family: 'DM Mono', monospace;
    font-size: .78rem;
    font-weight: 500;
}

/* ── TYPING INDICATOR ── */
.typing {
    display: flex;
    gap: 4px;
    align-items: center;
    padding: .5rem 0;
}
.typing span {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #6366f1;
    animation: bounce 1.2s ease infinite;
}
.typing span:nth-child(2) { animation-delay: .2s; }
.typing span:nth-child(3) { animation-delay: .4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-8px); }
}

/* alert overrides */
[data-testid="stAlert"] {
    background: rgba(99,102,241,.08) !important;
    border: 1px solid rgba(99,102,241,.25) !important;
    border-radius: 10px !important;
    color: rgba(232,234,240,.8) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "step": 0,           # 0=config, 1=interview, 2=results
    "questions": [],
    "current_q": 0,
    "answers": [],
    "evaluations": [],
    "groq_key": "",
    "role": "",
    "difficulty": "Medium",
    "num_q": 5,
    "domain": "Software Engineering",
    "interview_started": False,
    "loading": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Groq helpers ──────────────────────────────────────────────────────────────
def get_client():
    return groq.Groq(api_key=st.session_state.groq_key)

def llm(prompt: str, system: str = "", json_mode: bool = False) -> str:
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    kwargs = dict(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1800,
        temperature=0.7,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content.strip()

def generate_questions(role, domain, difficulty, num_q):
    system = (
        "You are a senior technical interviewer. Generate realistic interview questions. "
        "Always respond with valid JSON only, no extra text."
    )
    prompt = f"""Generate {num_q} {difficulty.lower()}-level interview questions for a {role} position in {domain}.
Return JSON: {{"questions": [{{"id":1,"question":"...","category":"...","reference_answer":"...","key_concepts":["..."]}}]}}
Each reference_answer should be 2-4 sentences. key_concepts should be 4-7 important terms/phrases."""
    raw = llm(prompt, system, json_mode=True)
    data = json.loads(raw)
    return data["questions"]

def evaluate_answer(question: dict, user_answer: str) -> dict:
    system = (
        "You are an expert technical interviewer evaluating candidate responses. "
        "Respond ONLY with valid JSON, no markdown, no extra text."
    )
    prompt = f"""Evaluate this interview answer strictly and fairly.

Question: {question['question']}
Reference Answer: {question['reference_answer']}
Key Concepts: {', '.join(question['key_concepts'])}
Candidate Answer: {user_answer}

Return JSON:
{{
  "confidence_score": <0-100 int>,
  "keyword_coverage": <0-100 int>,
  "accuracy_score": <0-100 int>,
  "overall_score": <0-100 int>,
  "covered_keywords": ["list of key concepts mentioned"],
  "missing_keywords": ["list of key concepts NOT mentioned"],
  "strengths": "1-2 sentence strength summary",
  "improvements": "1-2 sentence improvement suggestion",
  "detailed_feedback": "3-4 sentence detailed evaluation"
}}"""
    raw = llm(prompt, system, json_mode=True)
    return json.loads(raw)

def generate_summary(evaluations, role):
    scores = [e.get("overall_score", 0) for e in evaluations]
    avg = sum(scores) / len(scores) if scores else 0
    system = "You are a career coach writing concise interview performance summaries."
    prompt = f"""Role applied: {role}
Average score: {avg:.0f}/100
Individual scores: {scores}

Write a 3-sentence performance summary covering: overall performance, key strengths, and top area to improve.
Be specific and encouraging but honest."""
    return llm(prompt, system)

# ── Score color helper ─────────────────────────────────────────────────────────
def score_color(score):
    if score >= 80: return "#10b981"
    if score >= 60: return "#f59e0b"
    if score >= 40: return "#f97316"
    return "#ef4444"

def score_label(score):
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    if score >= 40: return "Fair"
    return "Needs Work"

# ── SVG ring ──────────────────────────────────────────────────────────────────
def score_ring_svg(score, size=120, label="Score"):
    r = 44
    circ = 2 * 3.14159 * r
    fill = (score / 100) * circ
    color = score_color(score)
    return f"""
<svg width="{size}" height="{size}" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="{r}" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="8"/>
  <circle cx="50" cy="50" r="{r}" fill="none" stroke="{color}" stroke-width="8"
    stroke-dasharray="{fill:.1f} {circ:.1f}" stroke-dashoffset="{circ/4:.1f}"
    stroke-linecap="round" style="filter:drop-shadow(0 0 6px {color}88)"/>
  <text x="50" y="46" text-anchor="middle" fill="{color}"
    font-family="Syne,sans-serif" font-size="18" font-weight="800">{score}</text>
  <text x="50" y="60" text-anchor="middle" fill="rgba(232,234,240,.4)"
    font-family="DM Mono,monospace" font-size="7" letter-spacing="1">{label.upper()}</text>
</svg>"""

# ── Step tracker ──────────────────────────────────────────────────────────────
def render_steps():
    step = st.session_state.step
    steps = ["Setup", "Interview", "Results"]
    dots, texts = "", ""
    for i, s in enumerate(steps):
        if i < step: cls = "done"; icon = "✓"
        elif i == step: cls = "active"; icon = str(i + 1)
        else: cls = "idle"; icon = str(i + 1)
        dots += f'<div class="step-item"><div class="step-dot {cls}">{icon}</div><span class="step-text {cls}">{s}</span></div>'
    st.markdown(f'<div class="steps">{dots}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 0 — CONFIG
# ══════════════════════════════════════════════════════════════════════════════
def page_config():
    render_steps()
    col1, col2 = st.columns([1.1, .9], gap="large")

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">⚙ Configuration</p>', unsafe_allow_html=True)
        st.markdown("#### Interview Setup")

        api_key = st.text_input("Groq API Key", type="password",
                                placeholder="gsk_...",
                                value=st.session_state.groq_key,
                                help="Get a free key at console.groq.com")
        st.session_state.groq_key = api_key

        role = st.text_input("Target Role", placeholder="e.g. Backend Engineer, Data Scientist",
                             value=st.session_state.role)
        st.session_state.role = role

        col_a, col_b = st.columns(2)
        with col_a:
            domain = st.selectbox("Domain", [
                "Software Engineering", "Data Science", "Machine Learning",
                "DevOps / Cloud", "Frontend Engineering",
                "Cybersecurity", "Product Management", "System Design"
            ], index=["Software Engineering","Data Science","Machine Learning",
                      "DevOps / Cloud","Frontend Engineering",
                      "Cybersecurity","Product Management","System Design"].index(st.session_state.domain)
                      if st.session_state.domain in ["Software Engineering","Data Science","Machine Learning",
                      "DevOps / Cloud","Frontend Engineering","Cybersecurity","Product Management","System Design"] else 0)
            st.session_state.domain = domain

        with col_b:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Expert"],
                                      index=["Easy","Medium","Hard","Expert"].index(st.session_state.difficulty))
            st.session_state.difficulty = difficulty

        num_q = st.slider("Number of Questions", 3, 10, st.session_state.num_q)
        st.session_state.num_q = num_q

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀  Generate Interview", use_container_width=True):
            if not api_key.strip():
                st.error("Please enter your Groq API key.")
            elif not role.strip():
                st.error("Please enter the target role.")
            else:
                with st.spinner(""):
                    st.markdown('<div class="typing"><span></span><span></span><span></span></div>',
                                unsafe_allow_html=True)
                    try:
                        qs = generate_questions(role, domain, difficulty, num_q)
                        st.session_state.questions = qs
                        st.session_state.current_q = 0
                        st.session_state.answers = []
                        st.session_state.evaluations = []
                        st.session_state.step = 1
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">ℹ How it works</p>', unsafe_allow_html=True)
        steps_info = [
            ("01", "Configure", "Set your role, domain & difficulty"),
            ("02", "Interview", "Answer AI-generated questions"),
            ("03", "Evaluate", "Get scored on accuracy & depth"),
            ("04", "Feedback", "Detailed review & improvement tips"),
        ]
        for n, title, desc in steps_info:
            st.markdown(f"""
<div style="display:flex;gap:.9rem;align-items:flex-start;margin-bottom:1.1rem">
  <span style="font-family:'DM Mono',monospace;font-size:.7rem;color:#6366f1;
        background:rgba(99,102,241,.12);border:1px solid rgba(99,102,241,.25);
        padding:.25rem .5rem;border-radius:6px;min-width:2.8rem;text-align:center">{n}</span>
  <div>
    <div style="font-weight:600;font-size:.9rem;margin-bottom:.15rem">{title}</div>
    <div style="font-family:'DM Mono',monospace;font-size:.72rem;color:rgba(232,234,240,.4)">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:.72rem;color:rgba(232,234,240,.35);line-height:1.8">
Powered by <span style="color:#6366f1">Groq LLaMA 3.3 70B</span><br>
Evaluates: accuracy · depth · keywords<br>
Provides: scores · feedback · gaps</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — INTERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_interview():
    render_steps()
    qs = st.session_state.questions
    idx = st.session_state.current_q
    total = len(qs)

    # Progress bar
    prog_pct = idx / total
    st.progress(prog_pct)
    st.markdown(f"""
<div style="font-family:'DM Mono',monospace;font-size:.72rem;color:rgba(232,234,240,.4);
     text-align:right;margin-top:-.5rem;margin-bottom:1rem">
  Question <span style="color:#6366f1">{idx+1}</span> of {total}
</div>""", unsafe_allow_html=True)

    # Past answers sidebar-style
    if st.session_state.evaluations:
        with st.expander(f"📊 Answered ({len(st.session_state.evaluations)}/{total})"):
            for i, ev in enumerate(st.session_state.evaluations):
                color = score_color(ev.get('overall_score', 0))
                st.markdown(f"""
<div class="hist-item">
  <div class="hist-q">Q{i+1}: {qs[i]['question'][:70]}...</div>
  <span class="hist-score" style="color:{color}">Score: {ev.get('overall_score',0)}/100 · {score_label(ev.get('overall_score',0))}</span>
</div>""", unsafe_allow_html=True)

    if idx < total:
        q = qs[idx]
        col1, col2 = st.columns([.2, .8])
        with col1:
            cat_colors = {"concept":"#6366f1","algorithm":"#10b981","system":"#f59e0b",
                          "behavioral":"#ec4899","design":"#14b8a6","default":"#6366f1"}
            cat = q.get("category","").lower()
            c = cat_colors.get(cat, cat_colors["default"])
            st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:.65rem;'
                        f'color:{c};border:1px solid {c}44;padding:.2rem .5rem;border-radius:3rem;'
                        f'text-align:center;background:{c}11">{q.get("category","General")}</div>',
                        unsafe_allow_html=True)
        with col2:
            pass

        st.markdown(f'<div class="q-bubble">{q["question"]}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        answer = st.text_area(
            "Your Answer",
            height=180,
            placeholder="Type your answer here… be thorough and specific.",
            key=f"ans_{idx}",
            label_visibility="collapsed"
        )

        col_a, col_b, col_c = st.columns([1, 1, 2])
        with col_a:
            if st.button("✓  Submit Answer", use_container_width=True):
                if not answer.strip():
                    st.warning("Please enter an answer before submitting.")
                else:
                    with st.spinner("Evaluating…"):
                        try:
                            ev = evaluate_answer(q, answer)
                            st.session_state.answers.append(answer)
                            st.session_state.evaluations.append(ev)
                            st.session_state.current_q += 1
                            if st.session_state.current_q >= total:
                                st.session_state.step = 2
                            st.rerun()
                        except Exception as e:
                            st.error(f"Evaluation failed: {e}")
        with col_b:
            if st.button("⏭  Skip Question", use_container_width=True):
                st.session_state.answers.append("[Skipped]")
                st.session_state.evaluations.append({
                    "confidence_score": 0, "keyword_coverage": 0,
                    "accuracy_score": 0, "overall_score": 0,
                    "covered_keywords": [], "missing_keywords": q.get("key_concepts", []),
                    "strengths": "—", "improvements": "Question was skipped.",
                    "detailed_feedback": "No answer provided."
                })
                st.session_state.current_q += 1
                if st.session_state.current_q >= total:
                    st.session_state.step = 2
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — RESULTS
# ══════════════════════════════════════════════════════════════════════════════
def page_results():
    render_steps()
    evs = st.session_state.evaluations
    qs  = st.session_state.questions
    ans = st.session_state.answers
    role = st.session_state.role

    if not evs:
        st.warning("No evaluations found.")
        return

    scores = [e.get("overall_score", 0) for e in evs]
    avg_overall    = sum(scores) / len(scores)
    avg_confidence = sum(e.get("confidence_score", 0) for e in evs) / len(evs)
    avg_keyword    = sum(e.get("keyword_coverage", 0) for e in evs) / len(evs)
    avg_accuracy   = sum(e.get("accuracy_score", 0) for e in evs) / len(evs)

    # ── Hero score ──
    st.markdown(f"""
<div style="text-align:center;padding:1rem 0 .5rem">
  <div style="font-family:'DM Mono',monospace;font-size:.72rem;letter-spacing:.2em;
       color:#10b981;margin-bottom:.5rem">INTERVIEW COMPLETE</div>
  <div style="font-size:clamp(1.8rem,4vw,3rem);font-weight:800;letter-spacing:-.03em;
       background:linear-gradient(135deg,#e8eaf0,#6366f1);
       -webkit-background-clip:text;-webkit-text-fill-color:transparent">
    {role}
  </div>
</div>""", unsafe_allow_html=True)

    # ── Four metric rings ──
    cols = st.columns(4)
    for col, (val, lbl) in zip(cols, [
        (int(avg_overall), "Overall"),
        (int(avg_confidence), "Confidence"),
        (int(avg_keyword), "Keywords"),
        (int(avg_accuracy), "Accuracy"),
    ]):
        with col:
            st.markdown(f"""
<div class="glass-card" style="text-align:center;animation-delay:{cols.index(col)*.1}s">
  {score_ring_svg(int(val), size=100, label=lbl)}
  <div style="font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.1em;
       color:{score_color(int(val))};margin-top:.3rem">{score_label(int(val))}</div>
</div>""", unsafe_allow_html=True)

    # ── AI Summary ──
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-label">🤖 AI Performance Summary</p>', unsafe_allow_html=True)
    with st.spinner("Generating summary…"):
        try:
            summary = generate_summary(evs, role)
        except:
            summary = "Summary unavailable."
    st.markdown(f'<div class="fb-block">{summary}</div>', unsafe_allow_html=True)

    # ── Per-question breakdown ──
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-label">📋 Question-by-Question Breakdown</p>', unsafe_allow_html=True)

    for i, (q, ev, a) in enumerate(zip(qs, evs, ans)):
        sc = ev.get("overall_score", 0)
        color = score_color(sc)
        with st.expander(f"Q{i+1} · {q['question'][:65]}… · Score: {sc}/100"):
            c1, c2 = st.columns([.65, .35])
            with c1:
                st.markdown(f'<div class="q-bubble" style="font-size:.92rem">{q["question"]}</div>',
                            unsafe_allow_html=True)
                st.markdown(f"""
<div style="margin-top:.9rem">
  <div style="font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.15em;
       color:rgba(232,234,240,.4);text-transform:uppercase;margin-bottom:.4rem">Your Answer</div>
  <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
       border-radius:10px;padding:.9rem 1rem;font-size:.88rem;line-height:1.6;
       font-family:'DM Mono',monospace;color:rgba(232,234,240,.75)">{a if a != "[Skipped]" else "<em>Skipped</em>"}</div>
</div>""", unsafe_allow_html=True)

                # Keywords
                covered = ev.get("covered_keywords", [])
                missing = ev.get("missing_keywords", [])
                st.markdown("""
<div style="margin-top:1rem">
  <div style="font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.15em;
       color:rgba(232,234,240,.4);text-transform:uppercase;margin-bottom:.4rem">Keywords</div>
  <div class="chip-row">""", unsafe_allow_html=True)
                chips = ""
                for kw in covered:
                    chips += f'<span class="chip chip-ok">✓ {kw}</span>'
                for kw in missing:
                    chips += f'<span class="chip chip-miss">✗ {kw}</span>'
                st.markdown(f'{chips}</div></div>', unsafe_allow_html=True)

                # Feedback
                st.markdown(f"""
<div style="margin-top:1rem">
  <div style="font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.15em;
       color:rgba(232,234,240,.4);text-transform:uppercase;margin-bottom:.4rem">Feedback</div>
  <div class="fb-block">{ev.get('detailed_feedback','')}</div>
</div>""", unsafe_allow_html=True)

            with c2:
                # Mini score rings
                for metric, key in [("Overall","overall_score"),("Confidence","confidence_score"),
                                     ("Keywords","keyword_coverage"),("Accuracy","accuracy_score")]:
                    val = ev.get(key, 0)
                    st.markdown(f"""
<div style="display:flex;align-items:center;gap:.7rem;margin-bottom:.7rem;
     background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);
     border-radius:10px;padding:.5rem .8rem">
  {score_ring_svg(val, size=50, label="")}
  <div>
    <div style="font-size:.82rem;font-weight:600">{val}<span style="font-size:.65rem;color:rgba(232,234,240,.4)">/100</span></div>
    <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:rgba(232,234,240,.4)">{metric}</div>
  </div>
</div>""", unsafe_allow_html=True)

                # Strengths / Improvements
                st.markdown(f"""
<div style="margin-top:.4rem">
  <div style="font-family:'DM Mono',monospace;font-size:.64rem;color:#10b981;
       letter-spacing:.1em;margin-bottom:.3rem">STRENGTH</div>
  <div style="font-size:.8rem;color:rgba(232,234,240,.75);line-height:1.5">{ev.get('strengths','')}</div>
  <div style="font-family:'DM Mono',monospace;font-size:.64rem;color:#f59e0b;
       letter-spacing:.1em;margin:.6rem 0 .3rem">IMPROVE</div>
  <div style="font-size:.8rem;color:rgba(232,234,240,.75);line-height:1.5">{ev.get('improvements','')}</div>
</div>""", unsafe_allow_html=True)

    # ── Actions ──
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄  New Interview", use_container_width=True):
            for k in ["questions","answers","evaluations","step","current_q"]:
                st.session_state[k] = defaults[k]
            st.rerun()
    with c2:
        if st.button("⚙  Change Config", use_container_width=True):
            st.session_state.step = 0
            st.session_state.questions = []
            st.session_state.answers = []
            st.session_state.evaluations = []
            st.rerun()
    with c3:
        # Export as text
        report = f"AI INTERVIEW REPORT\n{'='*50}\n"
        report += f"Role: {role} | Domain: {st.session_state.domain}\n"
        report += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        report += f"OVERALL SCORE: {avg_overall:.0f}/100\n\n"
        for i, (q, ev, a) in enumerate(zip(qs, evs, ans)):
            report += f"Q{i+1}: {q['question']}\nAnswer: {a}\nScore: {ev.get('overall_score',0)}/100\nFeedback: {ev.get('detailed_feedback','')}\n\n"
        st.download_button("📥  Export Report", report, file_name="interview_report.txt",
                           mime="text/plain", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-badge">AI · POWERED · INTERVIEW SIMULATOR</div>
  <h1>Ace Your Next<br>Technical Interview</h1>
  <p>Groq LLaMA 3.3 · Real-time evaluation · Semantic scoring</p>
</div>
""", unsafe_allow_html=True)

step = st.session_state.step
if step == 0:
    page_config()
elif step == 1:
    page_interview()
elif step == 2:
    page_results()
