import streamlit as st
import time
import json
import random
from groq_client import GroqInterviewer
from utils import (
    calculate_score, get_performance_badge, format_feedback,
    JOB_ROLES, DIFFICULTY_LEVELS, INTERVIEW_TYPES
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InterviewAI — Intelligent Mock Interviews",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ── */
:root {
  --bg-primary: #0a0a0f;
  --bg-secondary: #111118;
  --bg-card: #16161f;
  --bg-glass: rgba(255,255,255,0.04);
  --accent-cyan: #00f5d4;
  --accent-purple: #7c3aed;
  --accent-pink: #f72585;
  --accent-amber: #ffd60a;
  --text-primary: #f0f0ff;
  --text-secondary: #8888aa;
  --border: rgba(255,255,255,0.08);
  --radius: 16px;
  --radius-sm: 10px;
}

/* ── Global Reset ── */
* { box-sizing: border-box; }

.stApp {
  background: var(--bg-primary) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  color: var(--text-primary) !important;
}

/* Animated gradient background */
.stApp::before {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(124,58,237,0.12) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 90%, rgba(0,245,212,0.08) 0%, transparent 60%),
    radial-gradient(ellipse 40% 40% at 50% 50%, rgba(247,37,133,0.05) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg-secondary) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1rem !important; }

/* ── Hide Streamlit Defaults ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Typography ── */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* ── Hero Banner ── */
.hero-banner {
  background: linear-gradient(135deg, #16161f 0%, #1a1a2e 50%, #16161f 100%);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 3rem 2.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}
.hero-banner::before {
  content: '';
  position: absolute;
  top: -50%; left: -20%;
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(124,58,237,0.2) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-banner::after {
  content: '';
  position: absolute;
  bottom: -30%; right: -10%;
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(0,245,212,0.15) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-title {
  font-family: 'Syne', sans-serif !important;
  font-size: 3.2rem;
  font-weight: 800;
  line-height: 1.1;
  background: linear-gradient(135deg, #f0f0ff 0%, var(--accent-cyan) 50%, var(--accent-purple) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 0.5rem 0;
  position: relative;
  z-index: 1;
}
.hero-sub {
  color: var(--text-secondary);
  font-size: 1.1rem;
  font-weight: 400;
  position: relative;
  z-index: 1;
}
.hero-badge {
  display: inline-block;
  background: rgba(0,245,212,0.1);
  border: 1px solid rgba(0,245,212,0.3);
  color: var(--accent-cyan);
  padding: 0.3rem 0.9rem;
  border-radius: 50px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}

/* ── Cards ── */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: border-color 0.2s, transform 0.2s;
}
.card:hover { border-color: rgba(124,58,237,0.4); transform: translateY(-2px); }
.card-title {
  font-family: 'Syne', sans-serif;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}
.card-value {
  font-family: 'Syne', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
}

/* ── Question Box ── */
.question-box {
  background: linear-gradient(135deg, #1a1a2e 0%, #16161f 100%);
  border: 1px solid rgba(124,58,237,0.4);
  border-left: 4px solid var(--accent-purple);
  border-radius: var(--radius);
  padding: 2rem;
  margin: 1.5rem 0;
  position: relative;
}
.question-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--accent-purple);
  margin-bottom: 0.75rem;
}
.question-text {
  font-size: 1.25rem;
  font-weight: 500;
  line-height: 1.6;
  color: var(--text-primary);
}
.question-number {
  position: absolute;
  top: 1.5rem; right: 1.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* ── Feedback Box ── */
.feedback-box {
  border-radius: var(--radius);
  padding: 1.75rem;
  margin: 1rem 0;
}
.feedback-excellent {
  background: rgba(0,245,212,0.06);
  border: 1px solid rgba(0,245,212,0.25);
}
.feedback-good {
  background: rgba(124,58,237,0.06);
  border: 1px solid rgba(124,58,237,0.25);
}
.feedback-average {
  background: rgba(255,214,10,0.06);
  border: 1px solid rgba(255,214,10,0.25);
}
.feedback-poor {
  background: rgba(247,37,133,0.06);
  border: 1px solid rgba(247,37,133,0.25);
}
.feedback-score {
  font-family: 'JetBrains Mono', monospace;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}
.score-cyan { color: var(--accent-cyan); }
.score-purple { color: var(--accent-purple); }
.score-amber { color: var(--accent-amber); }
.score-pink { color: var(--accent-pink); }

/* ── Progress Bar ── */
.progress-container {
  background: rgba(255,255,255,0.05);
  border-radius: 50px;
  height: 8px;
  margin: 0.5rem 0 1.5rem 0;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 50px;
  background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan));
  transition: width 0.5s ease;
}

/* ── Status Chips ── */
.chip {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.chip-cyan { background: rgba(0,245,212,0.12); color: var(--accent-cyan); border: 1px solid rgba(0,245,212,0.25); }
.chip-purple { background: rgba(124,58,237,0.12); color: #a78bfa; border: 1px solid rgba(124,58,237,0.25); }
.chip-amber { background: rgba(255,214,10,0.12); color: var(--accent-amber); border: 1px solid rgba(255,214,10,0.25); }
.chip-pink { background: rgba(247,37,133,0.12); color: var(--accent-pink); border: 1px solid rgba(247,37,133,0.25); }

/* ── Timer ── */
.timer-display {
  font-family: 'JetBrains Mono', monospace;
  font-size: 2.5rem;
  font-weight: 700;
  text-align: center;
  color: var(--accent-cyan);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem;
  letter-spacing: 0.05em;
}
.timer-warning { color: var(--accent-amber) !important; }
.timer-danger { color: var(--accent-pink) !important; }

/* ── Report Card ── */
.report-header {
  text-align: center;
  padding: 3rem 2rem;
  background: linear-gradient(135deg, #1a1a2e 0%, #16161f 100%);
  border: 1px solid var(--border);
  border-radius: 24px;
  margin-bottom: 2rem;
}
.report-score-ring {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  margin: 1.5rem auto;
  font-family: 'Syne', sans-serif;
}
.report-score-big {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1;
}
.report-score-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* ── Stagger animation ── */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-in { animation: fadeSlideUp 0.4s ease forwards; }

/* ── Streamlit Widget Overrides ── */
.stButton > button {
  background: linear-gradient(135deg, var(--accent-purple), #5b21b6) !important;
  color: white !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  padding: 0.65rem 1.5rem !important;
  transition: all 0.2s !important;
  width: 100%;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #6d28d9, var(--accent-purple)) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 8px 25px rgba(124,58,237,0.35) !important;
}
.stTextArea textarea {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 1rem !important;
  transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
  border-color: var(--accent-purple) !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}
.stSelectbox > div > div {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
}
.stSlider > div { color: var(--text-primary) !important; }
div[data-testid="stMetric"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 1.2rem !important;
}
div[data-testid="stMetricValue"] {
  color: var(--accent-cyan) !important;
  font-family: 'Syne', sans-serif !important;
  font-size: 2rem !important;
}
.stSuccess { background: rgba(0,245,212,0.08) !important; border: 1px solid rgba(0,245,212,0.2) !important; color: var(--accent-cyan) !important; border-radius: var(--radius-sm) !important; }
.stWarning { background: rgba(255,214,10,0.08) !important; border: 1px solid rgba(255,214,10,0.2) !important; border-radius: var(--radius-sm) !important; }
.stError { background: rgba(247,37,133,0.08) !important; border: 1px solid rgba(247,37,133,0.2) !important; border-radius: var(--radius-sm) !important; }
.stInfo { background: rgba(124,58,237,0.08) !important; border: 1px solid rgba(124,58,237,0.2) !important; border-radius: var(--radius-sm) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Sidebar Labels ── */
[data-testid="stSidebar"] label {
  color: var(--text-secondary) !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
}

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-card) !important;
  border-radius: var(--radius-sm) !important;
  padding: 0.25rem !important;
  gap: 0.25rem !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text-secondary) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
  background: var(--accent-purple) !important;
  color: white !important;
}

/* ── Expander ── */
details {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--accent-purple); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ─────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "phase": "setup",           # setup | interview | results
        "questions": [],
        "answers": [],
        "feedbacks": [],
        "scores": [],
        "current_q": 0,
        "api_key": "",
        "job_role": "",
        "difficulty": "Intermediate",
        "interview_type": "Technical",
        "num_questions": 5,
        "start_time": None,
        "q_start_time": None,
        "time_per_q": 120,
        "interviewer": None,
        "resume_text": "",
        "follow_ups": [],
        "total_time": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:2rem;">
      <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;
                  background:linear-gradient(135deg,#f0f0ff,#00f5d4);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  background-clip:text;margin-bottom:0.25rem;">
        InterviewAI
      </div>
      <div style="color:#8888aa;font-size:0.78rem;letter-spacing:0.08em;text-transform:uppercase;font-weight:600;">
        Powered by Groq · Llama 3
      </div>
    </div>
    """, unsafe_allow_html=True)

    # API Key
    api_key = st.text_input(
        "🔑 Groq API Key",
        type="password",
        value=st.session_state.api_key,
        placeholder="gsk_...",
        help="Get your free key at console.groq.com"
    )
    if api_key:
        st.session_state.api_key = api_key
        st.markdown('<span class="chip chip-cyan">✓ API Key Set</span>', unsafe_allow_html=True)

    st.markdown("---")

    # Session state indicator
    phase_labels = {"setup": "⚙️ Setup", "interview": "🎤 Live Interview", "results": "📊 Results"}
    phase_colors = {"setup": "chip-amber", "interview": "chip-pink", "results": "chip-cyan"}
    st.markdown(f'<span class="chip {phase_colors[st.session_state.phase]}">{phase_labels[st.session_state.phase]}</span>', unsafe_allow_html=True)

    if st.session_state.phase == "interview":
        st.markdown("---")
        progress = (st.session_state.current_q) / max(len(st.session_state.questions), 1)
        st.markdown(f"""
        <div class="card-title">Progress</div>
        <div class="progress-container">
          <div class="progress-fill" style="width:{progress*100:.0f}%"></div>
        </div>
        <div style="color:#8888aa;font-size:0.85rem;text-align:center;">
          Question {st.session_state.current_q} of {len(st.session_state.questions)}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.phase != "setup":
        if st.button("🔄 Start New Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Tips
    st.markdown("""
    <div style="margin-top:2rem;">
      <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#8888aa;margin-bottom:0.75rem;">Interview Tips</div>
    """, unsafe_allow_html=True)
    tips = [
        "💡 Use the STAR method",
        "⏱️ Aim for 90–120 sec answers",
        "🎯 Be specific with examples",
        "❓ Ask clarifying questions",
        "📊 Quantify your achievements",
    ]
    for tip in tips:
        st.markdown(f'<div style="color:#8888aa;font-size:0.82rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">{tip}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── PHASE: SETUP ───────────────────────────────────────────────────────────────
if st.session_state.phase == "setup":

    # Hero
    st.markdown("""
    <div class="hero-banner animate-in">
      <div class="hero-badge">🚀 AI-Powered · Free with Groq</div>
      <div class="hero-title">Ace Your Next<br/>Interview</div>
      <div class="hero-sub">Real-time AI feedback • Personalized questions • Detailed scoring</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("50+", "Job Roles", "chip-cyan"),
        ("3", "Interview Types", "chip-purple"),
        ("Real-time", "AI Feedback", "chip-amber"),
        ("Free", "via Groq API", "chip-pink"),
    ]
    for col, (val, label, chip) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:1.25rem 1rem;">
              <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:var(--text-primary);">{val}</div>
              <div style="color:var(--text-secondary);font-size:0.82rem;margin-top:0.25rem;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Config form
    tab_config, tab_resume, tab_howto = st.tabs(["⚙️ Interview Config", "📄 Resume (Optional)", "❓ How It Works"])

    with tab_config:
        col_left, col_right = st.columns(2, gap="large")

        with col_left:
            st.markdown("#### 🎯 Role & Type")
            job_role = st.selectbox("Job Role / Domain", options=JOB_ROLES, index=0)
            interview_type = st.selectbox("Interview Type", options=INTERVIEW_TYPES)
            difficulty = st.selectbox("Difficulty Level", options=DIFFICULTY_LEVELS, index=1)

        with col_right:
            st.markdown("#### 📊 Session Settings")
            num_questions = st.slider("Number of Questions", min_value=3, max_value=15, value=5, step=1)
            time_per_q = st.slider("Time per Question (seconds)", min_value=60, max_value=300, value=120, step=30,
                                   help="You'll see a countdown timer for each question")
            custom_role = st.text_input("Custom Role (optional)", placeholder="e.g., Prompt Engineer, MLOps Lead")

        if custom_role:
            job_role = custom_role

        st.markdown("---")
        st.markdown("""
        <div class="card" style="background:rgba(124,58,237,0.06);border-color:rgba(124,58,237,0.25);">
          <div style="font-size:0.9rem;color:#a78bfa;font-weight:600;margin-bottom:0.5rem;">🤖 AI Model</div>
          <div style="color:var(--text-secondary);font-size:0.85rem;">
            Using <strong style="color:var(--text-primary);">llama-3.3-70b-versatile</strong> via Groq — 
            ultra-fast inference, completely free tier available. Get your key at 
            <strong style="color:#00f5d4;">console.groq.com</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with tab_resume:
        st.markdown("#### 📄 Paste Your Resume Text")
        st.markdown('<div style="color:var(--text-secondary);font-size:0.88rem;margin-bottom:1rem;">Optional — the AI will tailor questions to your background when provided.</div>', unsafe_allow_html=True)
        resume_text = st.text_area(
            "Resume Content",
            placeholder="Paste your resume text here...\n\nExample:\nSoftware Engineer with 5 years experience in Python, React...",
            height=300,
            label_visibility="collapsed"
        )
        if resume_text:
            word_count = len(resume_text.split())
            st.markdown(f'<span class="chip chip-cyan">📝 {word_count} words detected</span>', unsafe_allow_html=True)

    with tab_howto:
        st.markdown("""
        <div style="display:grid;gap:1rem;">
        """, unsafe_allow_html=True)
        steps = [
            ("1", "🔑 Add API Key", "Get your free Groq API key from console.groq.com — no credit card required."),
            ("2", "⚙️ Configure", "Choose your role, interview type, difficulty, and number of questions."),
            ("3", "🎤 Answer", "Each question appears with a countdown timer. Type your answer naturally."),
            ("4", "🤖 Feedback", "After each answer, AI provides instant scoring and detailed feedback."),
            ("5", "📊 Review", "At the end, get a full performance report with scores, strengths, and improvements."),
        ]
        for num, title, desc in steps:
            st.markdown(f"""
            <div class="card" style="display:flex;gap:1rem;align-items:flex-start;">
              <div style="background:var(--accent-purple);color:white;width:32px;height:32px;border-radius:50%;
                          display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.85rem;
                          flex-shrink:0;margin-top:2px;">{num}</div>
              <div>
                <div style="font-weight:600;margin-bottom:0.25rem;">{title}</div>
                <div style="color:var(--text-secondary);font-size:0.88rem;">{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Launch button
    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        if st.button("🚀 Start Interview Session", use_container_width=True):
            if not st.session_state.api_key:
                st.error("⚠️ Please enter your Groq API key in the sidebar to continue.")
            else:
                with st.spinner("🤖 Generating personalized questions..."):
                    try:
                        interviewer = GroqInterviewer(st.session_state.api_key)
                        questions = interviewer.generate_questions(
                            job_role=job_role,
                            interview_type=interview_type,
                            difficulty=difficulty,
                            num_questions=num_questions,
                            resume_text=resume_text if 'resume_text' in locals() else ""
                        )
                        st.session_state.update({
                            "phase": "interview",
                            "questions": questions,
                            "job_role": job_role,
                            "interview_type": interview_type,
                            "difficulty": difficulty,
                            "num_questions": num_questions,
                            "time_per_q": time_per_q,
                            "interviewer": interviewer,
                            "resume_text": resume_text if 'resume_text' in locals() else "",
                            "start_time": time.time(),
                            "q_start_time": time.time(),
                            "current_q": 0,
                            "answers": [],
                            "feedbacks": [],
                            "scores": [],
                            "follow_ups": [],
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    with col_info:
        if not st.session_state.api_key:
            st.warning("🔑 Enter your Groq API key in the sidebar to begin")
        else:
            st.success("✅ Ready to start! Click the button to launch your interview.")

# ── PHASE: INTERVIEW ───────────────────────────────────────────────────────────
elif st.session_state.phase == "interview":
    questions = st.session_state.questions
    current_q = st.session_state.current_q

    if current_q >= len(questions):
        st.session_state.phase = "results"
        st.session_state.total_time = time.time() - st.session_state.start_time
        st.rerun()

    q = questions[current_q]

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"""
        <div style="margin-bottom:1.5rem;">
          <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:var(--text-primary);">
            Live Interview
          </div>
          <div style="color:var(--text-secondary);font-size:0.9rem;margin-top:0.25rem;">
            {st.session_state.job_role} · {st.session_state.interview_type} · {st.session_state.difficulty}
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        elapsed = int(time.time() - st.session_state.q_start_time)
        remaining = max(0, st.session_state.time_per_q - elapsed)
        timer_class = ""
        if remaining < 30:
            timer_class = "timer-danger"
        elif remaining < 60:
            timer_class = "timer-warning"
        mins = remaining // 60
        secs = remaining % 60
        st.markdown(f"""
        <div class="timer-display {timer_class}">
          {mins:02d}:{secs:02d}
        </div>
        <div style="text-align:center;color:var(--text-secondary);font-size:0.75rem;margin-top:0.5rem;">Time Remaining</div>
        """, unsafe_allow_html=True)

    # Overall progress
    progress_pct = current_q / len(questions) * 100
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
      <div style="color:var(--text-secondary);font-size:0.82rem;">Interview Progress</div>
      <div style="color:var(--text-secondary);font-size:0.82rem;">{current_q}/{len(questions)} questions</div>
    </div>
    <div class="progress-container">
      <div class="progress-fill" style="width:{progress_pct}%"></div>
    </div>
    """, unsafe_allow_html=True)

    # Question box
    q_type_chip = {
        "Technical": "chip-purple",
        "Behavioral": "chip-cyan",
        "HR": "chip-amber",
        "Mixed": "chip-pink",
    }.get(st.session_state.interview_type, "chip-purple")

    st.markdown(f"""
    <div class="question-box animate-in">
      <div class="question-number">Q{current_q + 1} / {len(questions)}</div>
      <div class="question-label">
        <span class="chip {q_type_chip}" style="margin-right:0.5rem;">{st.session_state.interview_type}</span>
        Interview Question
      </div>
      <div class="question-text">{q}</div>
    </div>
    """, unsafe_allow_html=True)

    # Previous feedback (if any)
    if st.session_state.feedbacks:
        with st.expander("👁️ View Previous Answer Feedback"):
            last_fb = st.session_state.feedbacks[-1]
            last_score = st.session_state.scores[-1]
            score_color = "score-cyan" if last_score >= 80 else "score-purple" if last_score >= 60 else "score-amber" if last_score >= 40 else "score-pink"
            fb_class = "feedback-excellent" if last_score >= 80 else "feedback-good" if last_score >= 60 else "feedback-average" if last_score >= 40 else "feedback-poor"
            st.markdown(f"""
            <div class="feedback-box {fb_class}">
              <div class="feedback-score {score_color}">{last_score}/100</div>
              <div style="color:var(--text-secondary);font-size:0.8rem;margin-bottom:1rem;">Previous Question Score</div>
              <div style="color:var(--text-primary);line-height:1.7;font-size:0.95rem;">{last_fb}</div>
            </div>
            """, unsafe_allow_html=True)

    # Answer area
    st.markdown('<div style="margin:1rem 0 0.5rem 0;font-weight:600;font-size:0.9rem;color:var(--text-secondary);text-transform:uppercase;letter-spacing:0.08em;">✍️ Your Answer</div>', unsafe_allow_html=True)
    answer = st.text_area(
        "Your Answer",
        placeholder="Type your answer here...\n\nTips:\n• Use STAR format for behavioral questions (Situation → Task → Action → Result)\n• Be specific with examples and metrics\n• Aim for 2–3 minutes of speaking time",
        height=220,
        label_visibility="collapsed",
        key=f"answer_{current_q}"
    )

    col_sub, col_skip, col_hint = st.columns([3, 1.5, 1.5])

    with col_sub:
        submit_label = "✅ Submit & Get Feedback" if current_q < len(questions) - 1 else "🏁 Submit Final Answer"
        if st.button(submit_label, use_container_width=True):
            if not answer.strip():
                st.warning("⚠️ Please write an answer before submitting.")
            else:
                with st.spinner("🤖 Analyzing your answer..."):
                    try:
                        feedback, score = st.session_state.interviewer.evaluate_answer(
                            question=q,
                            answer=answer,
                            job_role=st.session_state.job_role,
                            interview_type=st.session_state.interview_type,
                            difficulty=st.session_state.difficulty
                        )
                        follow_up = st.session_state.interviewer.generate_follow_up(q, answer)
                        st.session_state.answers.append(answer)
                        st.session_state.feedbacks.append(feedback)
                        st.session_state.scores.append(score)
                        st.session_state.follow_ups.append(follow_up)
                        st.session_state.current_q += 1
                        st.session_state.q_start_time = time.time()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    with col_skip:
        if st.button("⏭️ Skip Question", use_container_width=True):
            st.session_state.answers.append("[Skipped]")
            st.session_state.feedbacks.append("Question was skipped — no feedback available.")
            st.session_state.scores.append(0)
            st.session_state.follow_ups.append("")
            st.session_state.current_q += 1
            st.session_state.q_start_time = time.time()
            st.rerun()

    with col_hint:
        if st.button("💡 Get Hint", use_container_width=True):
            with st.spinner("Generating hint..."):
                try:
                    hint = st.session_state.interviewer.get_hint(q, st.session_state.job_role)
                    st.info(f"💡 **Hint:** {hint}")
                except Exception as e:
                    st.error(f"Could not generate hint: {e}")

# ── PHASE: RESULTS ─────────────────────────────────────────────────────────────
elif st.session_state.phase == "results":
    scores = st.session_state.scores
    avg_score = sum(scores) / len(scores) if scores else 0
    total_mins = int(st.session_state.total_time // 60)
    total_secs = int(st.session_state.total_time % 60)
    badge, badge_color, badge_desc = get_performance_badge(avg_score)

    score_ring_bg = (
        "linear-gradient(135deg, rgba(0,245,212,0.2), rgba(0,245,212,0.05))" if avg_score >= 80 else
        "linear-gradient(135deg, rgba(124,58,237,0.2), rgba(124,58,237,0.05))" if avg_score >= 60 else
        "linear-gradient(135deg, rgba(255,214,10,0.2), rgba(255,214,10,0.05))" if avg_score >= 40 else
        "linear-gradient(135deg, rgba(247,37,133,0.2), rgba(247,37,133,0.05))"
    )
    score_text_color = (
        "var(--accent-cyan)" if avg_score >= 80 else
        "#a78bfa" if avg_score >= 60 else
        "var(--accent-amber)" if avg_score >= 40 else
        "var(--accent-pink)"
    )
    score_border = (
        "2px solid var(--accent-cyan)" if avg_score >= 80 else
        "2px solid var(--accent-purple)" if avg_score >= 60 else
        "2px solid var(--accent-amber)" if avg_score >= 40 else
        "2px solid var(--accent-pink)"
    )

    # Report header
    st.markdown(f"""
    <div class="report-header animate-in">
      <div style="font-family:'Syne',sans-serif;font-size:0.8rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.15em;color:var(--text-secondary);margin-bottom:0.5rem;">Interview Complete</div>
      <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;color:var(--text-primary);">
        Performance Report
      </div>
      <div style="color:var(--text-secondary);margin-top:0.5rem;">
        {st.session_state.job_role} · {st.session_state.interview_type} · {st.session_state.difficulty}
      </div>
      <div class="report-score-ring" style="background:{score_ring_bg};border:{score_border};">
        <div class="report-score-big" style="color:{score_text_color};">{avg_score:.0f}</div>
        <div class="report-score-label">/ 100</div>
      </div>
      <div style="font-size:1.5rem;margin-bottom:0.25rem;">{badge}</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:{score_text_color};">{badge_desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("Average Score", f"{avg_score:.0f}/100", "score-cyan" if avg_score >= 70 else ""),
        ("Questions", f"{len(scores)}", ""),
        ("Time Taken", f"{total_mins}m {total_secs}s", ""),
        ("Skipped", f"{scores.count(0)}", ""),
    ]
    for col, (label, val, _) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.metric(label, val)

    st.markdown("---")

    # Tabs for detail
    tab_qa, tab_scores, tab_summary = st.tabs(["📝 Q&A Review", "📊 Score Analysis", "🎯 AI Summary"])

    with tab_qa:
        for i, (q, ans, fb, score, fu) in enumerate(zip(
            st.session_state.questions,
            st.session_state.answers,
            st.session_state.feedbacks,
            st.session_state.scores,
            st.session_state.follow_ups
        )):
            score_color = "score-cyan" if score >= 80 else "score-purple" if score >= 60 else "score-amber" if score >= 40 else "score-pink"
            fb_class = "feedback-excellent" if score >= 80 else "feedback-good" if score >= 60 else "feedback-average" if score >= 40 else "feedback-poor"
            with st.expander(f"Q{i+1}: {q[:70]}{'...' if len(q) > 70 else ''} — Score: {score}/100"):
                st.markdown(f"""
                <div class="question-box" style="margin-bottom:1rem;">
                  <div class="question-label">Question</div>
                  <div style="color:var(--text-primary);font-size:1rem;line-height:1.6;">{q}</div>
                </div>
                <div style="margin-bottom:1rem;">
                  <div class="card-title" style="margin-bottom:0.5rem;">Your Answer</div>
                  <div style="color:var(--text-primary);font-size:0.95rem;line-height:1.7;
                               background:var(--bg-card);border:1px solid var(--border);
                               border-radius:var(--radius-sm);padding:1rem;">
                    {ans if ans != '[Skipped]' else '<em style="color:var(--text-secondary);">Question was skipped</em>'}
                  </div>
                </div>
                <div class="feedback-box {fb_class}">
                  <div class="feedback-score {score_color}">{score}/100</div>
                  <div style="color:var(--text-secondary);font-size:0.78rem;margin-bottom:0.75rem;">AI Evaluation Score</div>
                  <div style="color:var(--text-primary);line-height:1.7;font-size:0.95rem;">{fb}</div>
                </div>
                """, unsafe_allow_html=True)
                if fu:
                    st.markdown(f"""
                    <div class="card" style="border-color:rgba(0,245,212,0.25);background:rgba(0,245,212,0.04);margin-top:0.75rem;">
                      <div style="color:var(--accent-cyan);font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;">
                        🔄 Follow-up Question (for practice)
                      </div>
                      <div style="color:var(--text-primary);font-size:0.95rem;">{fu}</div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab_scores:
        import json
        score_data = {f"Q{i+1}": s for i, s in enumerate(scores)}

        # Bar chart using Streamlit native
        st.markdown('<div style="margin-bottom:1rem;color:var(--text-secondary);font-size:0.88rem;">Score breakdown per question (100 = perfect)</div>', unsafe_allow_html=True)
        st.bar_chart(score_data, color="#7c3aed", height=300)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            <div class="card">
              <div class="card-title">Score Distribution</div>
            """, unsafe_allow_html=True)
            ranges = {"Excellent (80-100)": 0, "Good (60-79)": 0, "Average (40-59)": 0, "Poor (0-39)": 0}
            for s in scores:
                if s >= 80: ranges["Excellent (80-100)"] += 1
                elif s >= 60: ranges["Good (60-79)"] += 1
                elif s >= 40: ranges["Average (40-59)"] += 1
                else: ranges["Poor (0-39)"] += 1
            for label, count in ranges.items():
                pct = (count / len(scores) * 100) if scores else 0
                st.markdown(f"""
                <div style="margin-bottom:0.75rem;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                    <span style="font-size:0.85rem;color:var(--text-secondary);">{label}</span>
                    <span style="font-size:0.85rem;color:var(--text-primary);font-weight:600;">{count}</span>
                  </div>
                  <div class="progress-container" style="margin:0;">
                    <div class="progress-fill" style="width:{pct}%;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            best_q = scores.index(max(scores)) + 1 if scores else 0
            worst_q = scores.index(min(scores)) + 1 if scores else 0
            st.markdown(f"""
            <div class="card">
              <div class="card-title">Highlights</div>
              <div style="display:grid;gap:0.75rem;margin-top:0.5rem;">
                <div style="background:rgba(0,245,212,0.06);border:1px solid rgba(0,245,212,0.2);border-radius:10px;padding:1rem;">
                  <div style="color:var(--accent-cyan);font-size:0.8rem;font-weight:600;margin-bottom:0.25rem;">🏆 Best Question</div>
                  <div style="font-size:1.2rem;font-weight:700;">Q{best_q} — {max(scores) if scores else 0}/100</div>
                </div>
                <div style="background:rgba(247,37,133,0.06);border:1px solid rgba(247,37,133,0.2);border-radius:10px;padding:1rem;">
                  <div style="color:var(--accent-pink);font-size:0.8rem;font-weight:600;margin-bottom:0.25rem;">📌 Needs Improvement</div>
                  <div style="font-size:1.2rem;font-weight:700;">Q{worst_q} — {min(scores) if scores else 0}/100</div>
                </div>
                <div style="background:rgba(124,58,237,0.06);border:1px solid rgba(124,58,237,0.2);border-radius:10px;padding:1rem;">
                  <div style="color:#a78bfa;font-size:0.8rem;font-weight:600;margin-bottom:0.25rem;">📈 Consistency</div>
                  <div style="font-size:1.2rem;font-weight:700;">±{(max(scores)-min(scores)) if scores else 0} pts range</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_summary:
        with st.spinner("🤖 Generating overall performance summary..."):
            try:
                summary = st.session_state.interviewer.generate_summary(
                    questions=st.session_state.questions,
                    answers=st.session_state.answers,
                    scores=st.session_state.scores,
                    job_role=st.session_state.job_role,
                    interview_type=st.session_state.interview_type,
                )
                st.markdown(f"""
                <div class="feedback-box feedback-good" style="margin-top:1rem;">
                  <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:1rem;color:#a78bfa;">
                    🎯 AI Performance Summary
                  </div>
                  <div style="color:var(--text-primary);line-height:1.8;font-size:0.97rem;">{summary}</div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Could not generate summary: {e}")

    st.markdown("---")
    col_restart, col_dl = st.columns(2)
    with col_restart:
        if st.button("🔄 Start New Interview", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col_dl:
        # Export results as text
        report_lines = [
            "=" * 60,
            "INTERVIEW AI — PERFORMANCE REPORT",
            "=" * 60,
            f"Role: {st.session_state.job_role}",
            f"Type: {st.session_state.interview_type}",
            f"Difficulty: {st.session_state.difficulty}",
            f"Overall Score: {avg_score:.0f}/100",
            f"Badge: {badge_desc}",
            "=" * 60,
        ]
        for i, (q, ans, fb, score) in enumerate(zip(
            st.session_state.questions, st.session_state.answers,
            st.session_state.feedbacks, st.session_state.scores
        )):
            report_lines += [f"\nQ{i+1} [{score}/100]: {q}", f"Answer: {ans}", f"Feedback: {fb}", "-"*40]
        report_text = "\n".join(report_lines)
        st.download_button(
            "📥 Download Report (.txt)",
            data=report_text,
            file_name=f"interview_report_{st.session_state.job_role.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )
