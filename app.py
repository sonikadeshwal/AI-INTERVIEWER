import streamlit as st
import time
import streamlit.components.v1 as components
from groq_client import GroqInterviewer
from utils import JOB_ROLES, DIFFICULTY_LEVELS, INTERVIEW_TYPES, get_performance_badge

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VoiceCoach AI — Interview Mastery",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Master CSS + Animations ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@700;800&display=swap');

:root {
  --bg0: #05050d;
  --bg1: #0c0c1a;
  --bg2: #111126;
  --bg3: #181830;
  --card: rgba(255,255,255,0.03);
  --border: rgba(255,255,255,0.07);
  --border-bright: rgba(255,255,255,0.15);
  --c1: #6ee7f7;   /* ice blue */
  --c2: #a78bfa;   /* violet */
  --c3: #f472b6;   /* pink */
  --c4: #34d399;   /* emerald */
  --c5: #fbbf24;   /* amber */
  --text: #eeeeff;
  --muted: #6666aa;
  --radius: 18px;
  --radius-sm: 10px;
  --glow1: rgba(110,231,247,0.15);
  --glow2: rgba(167,139,250,0.15);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; }

/* ── App Shell ── */
.stApp {
  background: var(--bg0) !important;
  font-family: 'Outfit', sans-serif !important;
  color: var(--text) !important;
  min-height: 100vh;
}
.stApp::before {
  content: '';
  position: fixed; inset: 0;
  background:
    radial-gradient(ellipse 70% 50% at 15% 20%, rgba(110,231,247,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 60% 60% at 85% 80%, rgba(167,139,250,0.08) 0%, transparent 60%),
    radial-gradient(ellipse 40% 40% at 50% 50%, rgba(244,114,182,0.04) 0%, transparent 70%);
  pointer-events: none; z-index: 0;
}

/* ── Hide Streamlit UI ── */
footer, .stDeployButton { display: none !important; }

/* ── Force Sidebar Visible ── */
section[data-testid="stSidebar"] {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  transform: none !important;
  min-width: 260px !important;
}
[data-testid="collapsedControl"] {
  display: flex !important;
  visibility: visible !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg1) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1.2rem !important; }
[data-testid="stSidebar"] label {
  color: var(--muted) !important;
  font-size: 0.75rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stTextInput > div > div > input {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: 'Outfit', sans-serif !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  color: white !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.95rem !important;
  padding: 0.7rem 1.5rem !important;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
  width: 100%;
  letter-spacing: 0.02em !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 30px rgba(99,102,241,0.4) !important;
  background: linear-gradient(135deg, #818cf8, #a78bfa) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Text areas ── */
.stTextArea textarea {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 1rem !important;
  line-height: 1.7 !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
  resize: vertical !important;
}
.stTextArea textarea:focus {
  border-color: var(--c2) !important;
  box-shadow: 0 0 0 3px rgba(167,139,250,0.12) !important;
  outline: none !important;
}

/* ── Alerts ── */
.stSuccess { background: rgba(52,211,153,0.08) !important; border: 1px solid rgba(52,211,153,0.25) !important; border-radius: var(--radius-sm) !important; color: var(--c4) !important; }
.stWarning { background: rgba(251,191,36,0.08) !important; border: 1px solid rgba(251,191,36,0.25) !important; border-radius: var(--radius-sm) !important; }
.stError   { background: rgba(244,114,182,0.08) !important; border: 1px solid rgba(244,114,182,0.25) !important; border-radius: var(--radius-sm) !important; }
.stInfo    { background: rgba(110,231,247,0.08) !important; border: 1px solid rgba(110,231,247,0.25) !important; border-radius: var(--radius-sm) !important; }

/* ── Metrics ── */
div[data-testid="stMetric"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 1.25rem !important;
  backdrop-filter: blur(10px) !important;
}
div[data-testid="stMetricValue"] {
  font-family: 'Outfit', sans-serif !important;
  font-weight: 800 !important;
  font-size: 2rem !important;
  color: var(--c1) !important;
}
div[data-testid="stMetricLabel"] {
  color: var(--muted) !important;
  font-size: 0.78rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg2) !important;
  border-radius: var(--radius-sm) !important;
  padding: 0.3rem !important;
  gap: 0.2rem !important;
  border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-family: 'Outfit', sans-serif !important;
  transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(99,102,241,0.3) !important;
}

/* ── Expanders ── */
details {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
}
details summary { color: var(--text) !important; font-weight: 600 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg0); }
::-webkit-scrollbar-thumb { background: var(--c2); border-radius: 3px; }

/* ── Keyframes ── */
@keyframes fadeUp   { from { opacity:0; transform:translateY(24px); } to { opacity:1; transform:translateY(0); } }
@keyframes fadeIn   { from { opacity:0; } to { opacity:1; } }
@keyframes pulse    { 0%,100% { transform:scale(1); } 50% { transform:scale(1.05); } }
@keyframes shimmer  { 0% { background-position:200% center; } 100% { background-position:-200% center; } }
@keyframes float    { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-8px); } }
@keyframes ripple   { 0% { transform:scale(0.8); opacity:1; } 100% { transform:scale(2.5); opacity:0; } }
@keyframes spin     { from { transform:rotate(0deg); } to { transform:rotate(360deg); } }
@keyframes gradMove { 0%,100% { background-position:0% 50%; } 50% { background-position:100% 50%; } }
@keyframes orb1     { 0%,100% { transform:translate(0,0) scale(1); } 33% { transform:translate(30px,-20px) scale(1.1); } 66% { transform:translate(-20px,10px) scale(0.95); } }
@keyframes orb2     { 0%,100% { transform:translate(0,0) scale(1); } 33% { transform:translate(-25px,15px) scale(0.9); } 66% { transform:translate(20px,-25px) scale(1.05); } }
@keyframes waveBar  { 0%,100% { height:6px; } 50% { height:24px; } }
@keyframes blink    { 0%,100% { opacity:1; } 50% { opacity:0.3; } }

/* ── Utility Classes ── */
.fade-up  { animation: fadeUp 0.5s ease forwards; }
.fade-in  { animation: fadeIn 0.4s ease forwards; }

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%);
  border: 1px solid var(--border);
  border-radius: 28px;
  padding: 3.5rem 3rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
  animation: fadeUp 0.6s ease;
}
.hero-orb1 {
  position: absolute; width: 300px; height: 300px; border-radius: 50%;
  background: radial-gradient(circle, rgba(110,231,247,0.18) 0%, transparent 70%);
  top: -80px; left: -60px;
  animation: orb1 8s ease-in-out infinite;
}
.hero-orb2 {
  position: absolute; width: 250px; height: 250px; border-radius: 50%;
  background: radial-gradient(circle, rgba(167,139,250,0.15) 0%, transparent 70%);
  bottom: -60px; right: -40px;
  animation: orb2 10s ease-in-out infinite;
}
.hero-badge {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: rgba(110,231,247,0.1);
  border: 1px solid rgba(110,231,247,0.25);
  color: var(--c1);
  padding: 0.35rem 1rem;
  border-radius: 50px;
  font-size: 0.78rem; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  margin-bottom: 1.25rem;
  position: relative; z-index: 1;
}
.hero-badge::before {
  content: ''; width: 6px; height: 6px; border-radius: 50%;
  background: var(--c1);
  animation: blink 1.5s ease-in-out infinite;
}
.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 800; line-height: 1.1;
  background: linear-gradient(135deg, #eeeeff 0%, var(--c1) 40%, var(--c2) 80%);
  background-size: 200% auto;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 4s linear infinite;
  margin-bottom: 1rem;
  position: relative; z-index: 1;
}
.hero-sub {
  color: var(--muted); font-size: 1.1rem; font-weight: 400;
  line-height: 1.6; max-width: 600px;
  position: relative; z-index: 1;
}
.hero-chips {
  display: flex; flex-wrap: wrap; gap: 0.5rem;
  margin-top: 1.5rem; position: relative; z-index: 1;
}
.hchip {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-bright);
  color: var(--text); padding: 0.35rem 0.9rem;
  border-radius: 50px; font-size: 0.82rem; font-weight: 500;
}

/* ── Cards ── */
.glass-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  backdrop-filter: blur(12px);
  transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
  animation: fadeUp 0.5s ease;
}
.glass-card:hover {
  border-color: var(--border-bright);
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.3);
}
.card-label {
  font-size: 0.72rem; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.12em;
  color: var(--muted); margin-bottom: 0.5rem;
}

/* ── Mode Selector ── */
.mode-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 1rem; margin: 1rem 0;
}
.mode-card {
  background: var(--card);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  text-align: center; cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  position: relative; overflow: hidden;
}
.mode-card::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(135deg, transparent, rgba(255,255,255,0.03));
  opacity: 0; transition: opacity 0.25s;
}
.mode-card:hover::before { opacity: 1; }
.mode-card:hover {
  border-color: var(--c2);
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(167,139,250,0.2);
}
.mode-card.active {
  border-color: var(--c1);
  background: rgba(110,231,247,0.06);
  box-shadow: 0 0 0 1px var(--c1), 0 12px 35px rgba(110,231,247,0.15);
}
.mode-icon {
  font-size: 2.5rem; margin-bottom: 0.75rem;
  animation: float 4s ease-in-out infinite;
}
.mode-title { font-weight: 800; font-size: 1.1rem; margin-bottom: 0.25rem; }
.mode-desc  { color: var(--muted); font-size: 0.85rem; }

/* ── Question Display ── */
.question-panel {
  background: linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%);
  border: 1px solid rgba(110,231,247,0.2);
  border-left: 4px solid var(--c1);
  border-radius: var(--radius);
  padding: 2rem;
  margin: 1.5rem 0;
  position: relative;
  animation: fadeUp 0.4s ease;
}
.q-badge {
  display: inline-flex; align-items: center; gap: 0.4rem;
  font-size: 0.72rem; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.12em;
  color: var(--c1); margin-bottom: 0.75rem;
}
.q-number {
  position: absolute; top: 1.5rem; right: 1.5rem;
  font-family: 'DM Mono', monospace;
  font-size: 0.78rem; color: var(--muted);
}
.q-text {
  font-size: 1.3rem; font-weight: 600; line-height: 1.65;
  color: var(--text);
}

/* ── Waveform Visualizer ── */
.waveform {
  display: flex; align-items: center; justify-content: center;
  gap: 4px; height: 40px; margin: 1rem 0;
}
.wave-bar {
  width: 4px; background: var(--c1);
  border-radius: 2px; height: 6px;
}
.wave-bar:nth-child(1)  { animation: waveBar 0.8s ease-in-out infinite 0.0s; }
.wave-bar:nth-child(2)  { animation: waveBar 0.8s ease-in-out infinite 0.1s; }
.wave-bar:nth-child(3)  { animation: waveBar 0.8s ease-in-out infinite 0.2s; }
.wave-bar:nth-child(4)  { animation: waveBar 0.8s ease-in-out infinite 0.1s; }
.wave-bar:nth-child(5)  { animation: waveBar 0.8s ease-in-out infinite 0.0s; }
.wave-bar:nth-child(6)  { animation: waveBar 0.8s ease-in-out infinite 0.15s; }
.wave-bar:nth-child(7)  { animation: waveBar 0.8s ease-in-out infinite 0.25s; }
.wave-bar:nth-child(8)  { animation: waveBar 0.8s ease-in-out infinite 0.1s; }
.wave-bar:nth-child(9)  { animation: waveBar 0.8s ease-in-out infinite 0.05s; }
.wave-bar:nth-child(10) { animation: waveBar 0.8s ease-in-out infinite 0.2s; }

/* ── Score Ring ── */
.score-ring-wrap { text-align: center; padding: 2rem 0; }
.score-value {
  font-family: 'Playfair Display', serif;
  font-size: 5rem; font-weight: 800; line-height: 1;
}
.score-label {
  font-size: 0.78rem; color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.12em;
}

/* ── Feedback Panels ── */
.fb-panel {
  border-radius: var(--radius);
  padding: 1.75rem;
  margin: 1rem 0;
  animation: fadeUp 0.4s ease;
}
.fb-excellent { background: rgba(52,211,153,0.06); border: 1px solid rgba(52,211,153,0.25); }
.fb-good      { background: rgba(110,231,247,0.06); border: 1px solid rgba(110,231,247,0.25); }
.fb-average   { background: rgba(251,191,36,0.06);  border: 1px solid rgba(251,191,36,0.25);  }
.fb-poor      { background: rgba(244,114,182,0.06); border: 1px solid rgba(244,114,182,0.25); }
.fb-score { font-family: 'DM Mono', monospace; font-size: 2.5rem; font-weight: 700; }
.fb-section-title {
  font-size: 0.75rem; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.1em;
  margin: 1rem 0 0.5rem 0;
}
.pronunciation-item {
  display: flex; align-items: flex-start; gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(255,255,255,0.03);
  border-radius: 8px; margin-bottom: 0.5rem;
  border: 1px solid var(--border);
}
.wrong-word {
  font-family: 'DM Mono', monospace;
  color: var(--c3); font-weight: 700;
  text-decoration: line-through;
}
.correct-word {
  font-family: 'DM Mono', monospace;
  color: var(--c4); font-weight: 700;
}

/* ── Progress bar ── */
.prog-wrap {
  background: rgba(255,255,255,0.05);
  border-radius: 50px; height: 6px;
  overflow: hidden; margin: 0.5rem 0 1.5rem;
}
.prog-fill {
  height: 100%; border-radius: 50px;
  background: linear-gradient(90deg, var(--c2), var(--c1));
  transition: width 0.6s cubic-bezier(0.4,0,0.2,1);
}

/* ── Timer ── */
.timer-box {
  font-family: 'DM Mono', monospace;
  font-size: 2.2rem; font-weight: 700;
  color: var(--c1); text-align: center;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1rem;
  letter-spacing: 0.05em;
}
.timer-warn   { color: var(--c5) !important; }
.timer-danger { color: var(--c3) !important; }

/* ── Chips ── */
.chip { display:inline-flex; align-items:center; gap:0.3rem; padding:0.3rem 0.8rem; border-radius:50px; font-size:0.75rem; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; }
.chip-blue   { background:rgba(110,231,247,0.1); color:var(--c1); border:1px solid rgba(110,231,247,0.25); }
.chip-purple { background:rgba(167,139,250,0.1); color:var(--c2); border:1px solid rgba(167,139,250,0.25); }
.chip-pink   { background:rgba(244,114,182,0.1); color:var(--c3); border:1px solid rgba(244,114,182,0.25); }
.chip-green  { background:rgba(52,211,153,0.1);  color:var(--c4); border:1px solid rgba(52,211,153,0.25);  }
.chip-amber  { background:rgba(251,191,36,0.1);  color:var(--c5); border:1px solid rgba(251,191,36,0.25);  }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Report header ── */
.report-hero {
  text-align: center; padding: 3rem 2rem;
  background: linear-gradient(135deg, var(--bg2), var(--bg3));
  border: 1px solid var(--border);
  border-radius: 28px; margin-bottom: 2rem;
  position: relative; overflow: hidden;
}
.report-hero-orb {
  position: absolute; border-radius: 50%;
  background: radial-gradient(circle, rgba(110,231,247,0.12) 0%, transparent 70%);
  width: 400px; height: 400px;
  top: -100px; left: 50%; transform: translateX(-50%);
  pointer-events: none;
}

/* ── Sidebar logo ── */
.sb-logo {
  font-family: 'Playfair Display', serif;
  font-size: 1.6rem; font-weight: 800;
  background: linear-gradient(135deg, var(--c1), var(--c2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.25rem;
}
.sb-sub {
  color: var(--muted); font-size: 0.75rem;
  font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.1em; margin-bottom: 1.5rem;
}

/* ── Voice recording UI ── */
.voice-recording-panel {
  background: rgba(244,114,182,0.05);
  border: 2px solid rgba(244,114,182,0.3);
  border-radius: var(--radius);
  padding: 2rem; text-align: center;
  animation: fadeUp 0.3s ease;
}
.recording-dot {
  width: 16px; height: 16px; border-radius: 50%;
  background: var(--c3);
  display: inline-block; margin-right: 0.5rem;
  animation: blink 1s ease-in-out infinite;
}

/* ── Pronunciation correction box ── */
.pronun-box {
  background: rgba(99,102,241,0.05);
  border: 1px solid rgba(99,102,241,0.2);
  border-radius: var(--radius);
  padding: 1.5rem; margin-top: 1rem;
}
.phonetic {
  font-family: 'DM Mono', monospace;
  font-size: 1.1rem; color: var(--c1);
  background: rgba(110,231,247,0.08);
  padding: 0.3rem 0.7rem; border-radius: 6px;
  display: inline-block;
}

/* ── Communication score bars ── */
.comm-bar-wrap { margin: 0.6rem 0; }
.comm-bar-label {
  display: flex; justify-content: space-between;
  font-size: 0.85rem; font-weight: 600; margin-bottom: 0.3rem;
}
.comm-bar-track {
  background: rgba(255,255,255,0.06);
  border-radius: 50px; height: 8px; overflow: hidden;
}
.comm-bar-fill {
  height: 100%; border-radius: 50px;
  background: linear-gradient(90deg, var(--c2), var(--c1));
  transition: width 1s cubic-bezier(0.4,0,0.2,1);
}
</style>
""", unsafe_allow_html=True)


# ── Session State ──────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "phase": "setup",
        "api_key": "",
        "job_role": "Software Engineer",
        "difficulty": "Intermediate",
        "interview_type": "Mixed",
        "num_questions": 5,
        "time_per_q": 120,
        "question_mode": "text",   # text | voice
        "answer_mode": "text",     # text | voice
        "questions": [],
        "answers": [],
        "feedbacks": [],
        "scores": [],
        "pronunciation_reports": [],
        "communication_scores": [],
        "follow_ups": [],
        "current_q": 0,
        "start_time": None,
        "q_start_time": None,
        "interviewer": None,
        "resume_text": "",
        "cached_summary": None,
        "voice_transcript": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Load API key from secrets if available ─────────────────────────────────────
if not st.session_state.api_key:
    try:
        st.session_state.api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass


# ── Voice TTS Component ────────────────────────────────────────────────────────
def render_tts(text: str, key: str):
    """Text-to-speech button using browser Web Speech API."""
    safe = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
    components.html(f"""
    <div style="font-family:'Outfit',sans-serif; display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
      <button id="btn-play-{key}" onclick="playTTS()" style="
        background:linear-gradient(135deg,#6ee7f7,#38bdf8);
        color:#05050d; border:none; border-radius:10px;
        padding:10px 20px; font-weight:800; font-size:14px;
        cursor:pointer; display:flex; align-items:center; gap:8px;
        font-family:'Outfit',sans-serif; letter-spacing:0.02em;
        box-shadow:0 4px 15px rgba(110,231,247,0.3);
        transition:all 0.2s;
      " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        🔊 Listen to Question
      </button>
      <button id="btn-stop-{key}" onclick="stopTTS()" style="
        background:rgba(244,114,182,0.15);
        color:#f472b6; border:1px solid rgba(244,114,182,0.35);
        border-radius:10px; padding:10px 20px;
        font-weight:800; font-size:14px; cursor:pointer;
        font-family:'Outfit',sans-serif; display:none;
        transition:all 0.2s;
      ">⏹ Stop</button>
      <span id="status-{key}" style="color:#6666aa; font-size:13px;"></span>
    </div>
    <script>
      var synth = window.speechSynthesis;
      var utt_{key} = null;
      function playTTS() {{
        if(synth.speaking) synth.cancel();
        utt_{key} = new SpeechSynthesisUtterance('{safe}');
        utt_{key}.rate = 0.92;
        utt_{key}.pitch = 1.05;
        utt_{key}.volume = 1;
        // prefer a natural voice
        var voices = synth.getVoices();
        var preferred = voices.find(v => v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha'));
        if(preferred) utt_{key}.voice = preferred;
        utt_{key}.onstart  = () => {{
          document.getElementById('btn-play-{key}').style.display='none';
          document.getElementById('btn-stop-{key}').style.display='flex';
          document.getElementById('status-{key}').innerText = '🎙 Speaking...';
        }};
        utt_{key}.onend = utt_{key}.onerror = () => {{
          document.getElementById('btn-play-{key}').style.display='flex';
          document.getElementById('btn-stop-{key}').style.display='none';
          document.getElementById('status-{key}').innerText = '';
        }};
        synth.speak(utt_{key});
      }}
      function stopTTS() {{
        synth.cancel();
        document.getElementById('btn-play-{key}').style.display='flex';
        document.getElementById('btn-stop-{key}').style.display='none';
        document.getElementById('status-{key}').innerText = '';
      }}
    </script>
    """, height=60)


# ── Voice STT Component ────────────────────────────────────────────────────────
def render_stt(key: str, placeholder_key: str):
    """Speech-to-text using browser Web Speech API. Writes transcript to a hidden field."""
    components.html(f"""
    <div style="font-family:'Outfit',sans-serif;">
      <div id="stt-panel-{key}" style="
        background:rgba(244,114,182,0.05);
        border:2px solid rgba(244,114,182,0.25);
        border-radius:14px; padding:1.5rem; text-align:center;
      ">
        <div style="margin-bottom:1rem;">
          <!-- Waveform bars -->
          <div id="wave-{key}" style="display:none; justify-content:center; align-items:center; gap:4px; height:40px; margin-bottom:1rem;">
            {''.join([f'<div style="width:4px;background:#6ee7f7;border-radius:2px;height:6px;animation:wb 0.8s ease-in-out infinite {i*0.1}s"></div>' for i in range(10)])}
          </div>
          <style>
            @keyframes wb {{ 0%,100%{{height:6px}} 50%{{height:28px}} }}
          </style>
        </div>

        <button id="btn-rec-{key}" onclick="startRec()" style="
          background:linear-gradient(135deg,#f472b6,#ec4899);
          color:white; border:none; border-radius:12px;
          padding:14px 28px; font-weight:800; font-size:15px;
          cursor:pointer; font-family:'Outfit',sans-serif;
          box-shadow:0 6px 20px rgba(244,114,182,0.35);
          letter-spacing:0.02em; transition:all 0.2s;
          display:flex; align-items:center; gap:10px; margin:0 auto;
        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
          🎤 Start Speaking
        </button>

        <button id="btn-stop-rec-{key}" onclick="stopRec()" style="
          background:rgba(251,191,36,0.15);
          color:#fbbf24; border:1px solid rgba(251,191,36,0.35);
          border-radius:12px; padding:14px 28px;
          font-weight:800; font-size:15px; cursor:pointer;
          font-family:'Outfit',sans-serif; display:none;
          align-items:center; gap:10px; margin:0 auto;
          transition:all 0.2s;
        ">⏹ Stop Recording</button>

        <div id="rec-status-{key}" style="color:#6666aa; font-size:13px; margin-top:1rem;"></div>
        <div id="rec-live-{key}" style="
          color:#eeeeff; font-size:0.95rem; margin-top:1rem;
          min-height:40px; text-align:left;
          background:rgba(255,255,255,0.03);
          border-radius:8px; padding:0.75rem;
          border:1px solid rgba(255,255,255,0.07);
          display:none; line-height:1.6;
          font-family:'Outfit',sans-serif;
        "></div>
      </div>

      <!-- Hidden input to communicate transcript to Streamlit via URL trick -->
      <textarea id="transcript-out-{key}" style="display:none;"></textarea>
    </div>

    <script>
      var recog_{key} = null;
      var fullTranscript_{key} = '';

      function startRec() {{
        var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if(!SR) {{
          document.getElementById('rec-status-{key}').innerText = '⚠️ Speech recognition not supported in this browser. Use Chrome.';
          return;
        }}
        recog_{key} = new SR();
        recog_{key}.continuous = true;
        recog_{key}.interimResults = true;
        recog_{key}.lang = 'en-US';
        fullTranscript_{key} = '';

        recog_{key}.onstart = () => {{
          document.getElementById('btn-rec-{key}').style.display='none';
          document.getElementById('btn-stop-rec-{key}').style.display='flex';
          document.getElementById('wave-{key}').style.display='flex';
          document.getElementById('rec-status-{key}').innerHTML='<span style="color:#f472b6">● Recording...</span>';
          document.getElementById('rec-live-{key}').style.display='block';
        }};

        recog_{key}.onresult = (e) => {{
          var interim = '';
          var final = '';
          for(var i = e.resultIndex; i < e.results.length; i++) {{
            if(e.results[i].isFinal) final += e.results[i][0].transcript + ' ';
            else interim += e.results[i][0].transcript;
          }}
          fullTranscript_{key} += final;
          document.getElementById('rec-live-{key}').innerHTML =
            '<span style="color:#eeeeff">' + fullTranscript_{key} + '</span>' +
            '<span style="color:#6666aa;font-style:italic">' + interim + '</span>';
          // Store in textarea for reading
          document.getElementById('transcript-out-{key}').value = fullTranscript_{key} + interim;
        }};

        recog_{key}.onerror = (e) => {{
          document.getElementById('rec-status-{key}').innerText = '⚠️ Error: ' + e.error;
          stopRec();
        }};

        recog_{key}.onend = () => {{
          if(fullTranscript_{key}) {{
            document.getElementById('rec-status-{key}').innerHTML =
              '<span style="color:#34d399">✓ Captured ' + fullTranscript_{key}.trim().split(' ').length + ' words</span>';
          }}
        }};

        recog_{key}.start();
      }}

      function stopRec() {{
        if(recog_{key}) recog_{key}.stop();
        document.getElementById('btn-rec-{key}').style.display='flex';
        document.getElementById('btn-stop-rec-{key}').style.display='none';
        document.getElementById('wave-{key}').style.display='none';
      }}
    </script>
    """, height=280, scrolling=False)


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">VoiceCoach AI</div>
    <div class="sb-sub">Interview Mastery System</div>
    """, unsafe_allow_html=True)

    api_key = st.text_input("🔑 Groq API Key", type="password",
                             value=st.session_state.api_key, placeholder="gsk_...")
    if api_key:
        st.session_state.api_key = api_key
        st.markdown('<span class="chip chip-green">✓ API Key Active</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="chip chip-amber">⚠ Key Required</span>', unsafe_allow_html=True)

    st.markdown("---")

    # Phase indicator
    phase_map = {"setup": ("⚙️ Setup", "chip-purple"), "interview": ("🎤 Live", "chip-pink"), "results": ("📊 Results", "chip-green")}
    label, color = phase_map[st.session_state.phase]
    st.markdown(f'<span class="chip {color}">{label}</span>', unsafe_allow_html=True)

    # Progress during interview
    if st.session_state.phase == "interview":
        st.markdown("---")
        q_done = st.session_state.current_q
        q_total = len(st.session_state.questions)
        pct = (q_done / max(q_total, 1)) * 100
        st.markdown(f"""
        <div class="card-label">Progress — {q_done}/{q_total}</div>
        <div class="prog-wrap"><div class="prog-fill" style="width:{pct:.0f}%"></div></div>
        """, unsafe_allow_html=True)

        # Scores so far
        if st.session_state.scores:
            avg = sum(st.session_state.scores) / len(st.session_state.scores)
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;padding:1rem;">
              <div class="card-label">Running Avg</div>
              <div style="font-size:2rem;font-weight:800;color:var(--c1);">{avg:.0f}</div>
              <div style="color:var(--muted);font-size:0.78rem;">/ 100</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.phase != "setup":
        if st.button("🔄 New Session"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    st.markdown("""
    <div style="margin-top:1.5rem;">
      <div class="card-label" style="margin-bottom:0.75rem;">Quick Tips</div>
      <div style="color:var(--muted);font-size:0.82rem;line-height:2;">
        💡 STAR method for behaviorals<br>
        ⏱️ Aim for 90–120 sec answers<br>
        🎯 Cite specific examples<br>
        📊 Quantify achievements<br>
        🗣️ Speak clearly & confidently
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE: SETUP
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.phase == "setup":

    # Hero
    st.markdown("""
    <div class="hero">
      <div class="hero-orb1"></div>
      <div class="hero-orb2"></div>
      <div class="hero-badge">🎙 AI-Powered · Voice + Text · Free with Groq</div>
      <div class="hero-title">Master Your<br/>Interview Skills</div>
      <div class="hero-sub">
        Practice with an AI interviewer that asks questions in voice or text,
        evaluates your answers in real-time, and coaches your pronunciation
        and communication skills.
      </div>
      <div class="hero-chips">
        <span class="hchip">🎤 Voice Input</span>
        <span class="hchip">🔊 Voice Questions</span>
        <span class="hchip">🗣️ Pronunciation Coach</span>
        <span class="hchip">📊 Communication Score</span>
        <span class="hchip">🤖 AI Feedback</span>
        <span class="hchip">50+ Job Roles</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── STEP 1: Mode Selection ─────────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:800;margin-bottom:0.25rem;">
      Step 1 — Choose Your Interview Mode
    </div>
    <div style="color:var(--muted);font-size:0.9rem;margin-bottom:1.5rem;">
      How should the AI ask questions? How will you answer?
    </div>
    """, unsafe_allow_html=True)

    col_q, col_a = st.columns(2, gap="large")

    with col_q:
        st.markdown('<div class="card-label" style="margin-bottom:0.75rem;">🔊 Question Delivery Mode</div>', unsafe_allow_html=True)
        q_mode = st.session_state.question_mode

        st.markdown(f"""
        <div class="mode-grid">
          <div class="mode-card {'active' if q_mode=='text' else ''}" onclick="this.closest('[data-testid]')" id="qm-text">
            <div class="mode-icon">📝</div>
            <div class="mode-title">Text</div>
            <div class="mode-desc">Questions shown as text on screen</div>
          </div>
          <div class="mode-card {'active' if q_mode=='voice' else ''}" id="qm-voice">
            <div class="mode-icon">🔊</div>
            <div class="mode-title">Voice</div>
            <div class="mode-desc">AI speaks questions aloud to you</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        qm_col1, qm_col2 = st.columns(2)
        with qm_col1:
            if st.button("📝 Text Mode", key="qm_text"):
                st.session_state.question_mode = "text"
                st.rerun()
        with qm_col2:
            if st.button("🔊 Voice Mode", key="qm_voice"):
                st.session_state.question_mode = "voice"
                st.rerun()

        active_qmode = "chip-blue" if st.session_state.question_mode == "voice" else "chip-purple"
        st.markdown(f'<span class="chip {active_qmode}">Selected: {st.session_state.question_mode.title()} Mode</span>', unsafe_allow_html=True)

    with col_a:
        st.markdown('<div class="card-label" style="margin-bottom:0.75rem;">🎤 Answer Input Mode</div>', unsafe_allow_html=True)
        a_mode = st.session_state.answer_mode

        st.markdown(f"""
        <div class="mode-grid">
          <div class="mode-card {'active' if a_mode=='text' else ''}" id="am-text">
            <div class="mode-icon">⌨️</div>
            <div class="mode-title">Type</div>
            <div class="mode-desc">Type your answers using keyboard</div>
          </div>
          <div class="mode-card {'active' if a_mode=='voice' else ''}" id="am-voice">
            <div class="mode-icon">🎤</div>
            <div class="mode-title">Speak</div>
            <div class="mode-desc">Speak your answers — AI transcribes</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        am_col1, am_col2 = st.columns(2)
        with am_col1:
            if st.button("⌨️ Type Mode", key="am_text"):
                st.session_state.answer_mode = "text"
                st.rerun()
        with am_col2:
            if st.button("🎤 Speak Mode", key="am_voice"):
                st.session_state.answer_mode = "voice"
                st.rerun()

        active_amode = "chip-pink" if st.session_state.answer_mode == "voice" else "chip-purple"
        st.markdown(f'<span class="chip {active_amode}">Selected: {st.session_state.answer_mode.title()} Mode</span>', unsafe_allow_html=True)

    st.markdown("---")

    # ── STEP 2: Interview Config ───────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:800;margin-bottom:0.25rem;">
      Step 2 — Configure Your Interview
    </div>
    <div style="color:var(--muted);font-size:0.9rem;margin-bottom:1.5rem;">
      Personalize the difficulty, role, and focus area.
    </div>
    """, unsafe_allow_html=True)

    tab_cfg, tab_resume, tab_howto = st.tabs(["⚙️ Settings", "📄 Resume", "❓ How It Works"])

    with tab_cfg:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            job_role = st.selectbox("Job Role", JOB_ROLES)
            interview_type = st.selectbox("Interview Type", INTERVIEW_TYPES)
            custom = st.text_input("Custom Role (optional)", placeholder="e.g., Prompt Engineer")
            if custom.strip():
                job_role = custom.strip()

        with c2:
            difficulty = st.selectbox("Difficulty", DIFFICULTY_LEVELS, index=1)
            num_questions = st.slider("Number of Questions", 3, 15, 5)
            time_per_q = st.slider("Seconds per Question", 60, 300, 120, step=30)

        st.markdown(f"""
        <div class="glass-card" style="background:rgba(99,102,241,0.05);border-color:rgba(99,102,241,0.2);margin-top:1rem;">
          <div style="color:#a78bfa;font-weight:700;margin-bottom:0.5rem;">🤖 AI Engine</div>
          <div style="color:var(--muted);font-size:0.88rem;">
            <strong style="color:var(--text)">llama-3.1-8b-instant</strong> via Groq —
            ultra-fast inference for real-time feedback. Get your free key at
            <strong style="color:var(--c1)">console.groq.com</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with tab_resume:
        st.markdown('<div style="color:var(--muted);font-size:0.88rem;margin-bottom:1rem;">Paste your resume to get personalized, tailored questions.</div>', unsafe_allow_html=True)
        resume_text = st.text_area("Resume Text", placeholder="Paste your resume here...", height=280, label_visibility="collapsed")
        if resume_text:
            wc = len(resume_text.split())
            st.markdown(f'<span class="chip chip-green">📝 {wc} words</span>', unsafe_allow_html=True)

    with tab_howto:
        steps = [
            ("🎙", "Choose Mode", "Pick voice or text for both questions and answers — mix and match freely."),
            ("⚙️", "Configure", "Select role, type, difficulty and number of questions."),
            ("🎤", "Answer", "Speak or type each answer within the countdown timer."),
            ("🤖", "Get Feedback", "AI scores your answer AND analyzes pronunciation + communication."),
            ("📊", "Full Report", "Review detailed scores, corrections, and improvement tips."),
        ]
        for icon, title, desc in steps:
            st.markdown(f"""
            <div class="glass-card" style="display:flex;gap:1rem;align-items:flex-start;margin-bottom:0.75rem;">
              <div style="font-size:1.5rem;flex-shrink:0;">{icon}</div>
              <div>
                <div style="font-weight:700;margin-bottom:0.2rem;">{title}</div>
                <div style="color:var(--muted);font-size:0.87rem;">{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Launch ─────────────────────────────────────────────────────────────────
    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        if st.button("🚀 Launch Interview Session", use_container_width=True):
            if not st.session_state.api_key:
                st.error("⚠️ Enter your Groq API key in the sidebar.")
            else:
                with st.spinner("🤖 Generating personalized questions..."):
                    try:
                        interviewer = GroqInterviewer(st.session_state.api_key)
                        questions = interviewer.generate_questions(
                            job_role=job_role,
                            interview_type=interview_type,
                            difficulty=difficulty,
                            num_questions=num_questions,
                            resume_text=resume_text if 'resume_text' in locals() else "",
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
                            "answers": [], "feedbacks": [], "scores": [],
                            "pronunciation_reports": [], "communication_scores": [],
                            "follow_ups": [], "cached_summary": None,
                            "voice_transcript": "",
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
    with col_info:
        if st.session_state.api_key:
            st.success(f"✅ Ready! {num_questions if 'num_questions' in dir() else 5} questions · {st.session_state.question_mode.title()} questions · {st.session_state.answer_mode.title()} answers")
        else:
            st.warning("🔑 Add your Groq API key in the sidebar to begin")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE: INTERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "interview":
    questions = st.session_state.questions
    current_q = st.session_state.current_q

    if current_q >= len(questions):
        st.session_state.phase = "results"
        st.session_state.total_time = time.time() - st.session_state.start_time
        st.rerun()

    q_text = questions[current_q]

    # ── Header row ─────────────────────────────────────────────────────────────
    col_hdr, col_timer = st.columns([3, 1])
    with col_hdr:
        st.markdown(f"""
        <div class="fade-up">
          <div style="font-family:'Playfair Display',serif;font-size:2rem;font-weight:800;">Live Interview</div>
          <div style="color:var(--muted);font-size:0.88rem;margin-top:0.25rem;">
            {st.session_state.job_role} ·
            <span class="chip chip-purple" style="font-size:0.7rem;">{st.session_state.interview_type}</span>
            <span class="chip chip-blue" style="font-size:0.7rem;margin-left:0.3rem;">{st.session_state.difficulty}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_timer:
        elapsed = int(time.time() - st.session_state.q_start_time)
        remaining = max(0, st.session_state.time_per_q - elapsed)
        tcls = "timer-danger" if remaining < 30 else "timer-warn" if remaining < 60 else ""
        st.markdown(f"""
        <div class="timer-box {tcls}">{remaining//60:02d}:{remaining%60:02d}</div>
        <div style="text-align:center;color:var(--muted);font-size:0.72rem;margin-top:0.3rem;">TIME LEFT</div>
        """, unsafe_allow_html=True)

    # Progress bar
    pct = current_q / len(questions) * 100
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;color:var(--muted);font-size:0.8rem;margin-bottom:0.3rem;">
      <span>Question {current_q+1} of {len(questions)}</span>
      <span>{pct:.0f}% complete</span>
    </div>
    <div class="prog-wrap"><div class="prog-fill" style="width:{pct}%"></div></div>
    """, unsafe_allow_html=True)

    # ── Question Panel ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="question-panel">
      <div class="q-number">Q{current_q+1}/{len(questions)}</div>
      <div class="q-badge">🎯 Interview Question</div>
      <div class="q-text">{q_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # TTS button if voice mode
    if st.session_state.question_mode == "voice":
        render_tts(q_text, key=f"q{current_q}")
        st.markdown("""
        <div style="color:var(--muted);font-size:0.82rem;margin-top:0.5rem;">
          🔊 Voice mode active — click above to hear the question read aloud.
        </div>
        """, unsafe_allow_html=True)

    # ── Previous feedback peek ─────────────────────────────────────────────────
    if st.session_state.feedbacks:
        with st.expander("👁 View Last Answer Feedback"):
            last_score = st.session_state.scores[-1]
            last_fb = st.session_state.feedbacks[-1]
            fb_cls = "fb-excellent" if last_score >= 80 else "fb-good" if last_score >= 60 else "fb-average" if last_score >= 40 else "fb-poor"
            score_col = ("var(--c4)" if last_score >= 80 else "var(--c1)" if last_score >= 60
                        else "var(--c5)" if last_score >= 40 else "var(--c3)")
            st.markdown(f"""
            <div class="fb-panel {fb_cls}">
              <div class="fb-score" style="color:{score_col};">{last_score}/100</div>
              <div style="color:var(--muted);font-size:0.78rem;margin-bottom:0.75rem;">Previous Answer Score</div>
              <div style="color:var(--text);line-height:1.75;font-size:0.95rem;">{last_fb}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Answer Section ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-weight:700;font-size:0.82rem;text-transform:uppercase;
                letter-spacing:0.1em;color:var(--muted);margin:1.25rem 0 0.5rem;">
      ✍️ Your Answer
    </div>
    """, unsafe_allow_html=True)

    answer_text = ""

    if st.session_state.answer_mode == "voice":
        st.markdown("""
        <div style="color:var(--muted);font-size:0.85rem;margin-bottom:0.75rem;">
          🎤 Click the button below to start speaking. Your speech will be transcribed automatically.
          <br>After recording, paste your transcript in the text box below or submit directly.
        </div>
        """, unsafe_allow_html=True)

        render_stt(key=f"stt{current_q}", placeholder_key=f"stt{current_q}")

        st.markdown("""
        <div style="color:var(--muted);font-size:0.82rem;margin:0.75rem 0 0.4rem;">
          📋 Your transcribed answer (edit if needed):
        </div>
        """, unsafe_allow_html=True)
        answer_text = st.text_area(
            "Transcribed Answer",
            placeholder="Your speech will appear here after recording. You can also type directly.",
            height=160,
            label_visibility="collapsed",
            key=f"ans_voice_{current_q}"
        )
    else:
        answer_text = st.text_area(
            "Type your answer",
            placeholder="Type your answer here...\n\n💡 Tips:\n• STAR format: Situation → Task → Action → Result\n• Be specific with examples and metrics\n• Aim for 2–3 minutes of speaking time",
            height=220,
            label_visibility="collapsed",
            key=f"ans_text_{current_q}"
        )

    # ── Action Buttons ─────────────────────────────────────────────────────────
    col_sub, col_skip, col_hint = st.columns([3, 1.5, 1.5])

    with col_sub:
        btn_label = "✅ Submit & Get Full Feedback" if current_q < len(questions) - 1 else "🏁 Submit Final Answer"
        if st.button(btn_label, use_container_width=True):
            if not answer_text.strip():
                st.warning("⚠️ Please provide an answer before submitting.")
            else:
                with st.spinner("🤖 Analyzing answer, pronunciation & communication..."):
                    try:
                        # Content feedback
                        feedback, score = st.session_state.interviewer.evaluate_answer(
                            question=q_text,
                            answer=answer_text,
                            job_role=st.session_state.job_role,
                            interview_type=st.session_state.interview_type,
                            difficulty=st.session_state.difficulty,
                        )
                        # Pronunciation + communication analysis
                        pron_report, comm_scores = st.session_state.interviewer.analyze_language(
                            answer=answer_text,
                            job_role=st.session_state.job_role,
                        )
                        follow_up = st.session_state.interviewer.generate_follow_up(q_text, answer_text)

                        st.session_state.answers.append(answer_text)
                        st.session_state.feedbacks.append(feedback)
                        st.session_state.scores.append(score)
                        st.session_state.pronunciation_reports.append(pron_report)
                        st.session_state.communication_scores.append(comm_scores)
                        st.session_state.follow_ups.append(follow_up)
                        st.session_state.current_q += 1
                        st.session_state.q_start_time = time.time()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

    with col_skip:
        if st.button("⏭ Skip", use_container_width=True):
            st.session_state.answers.append("[Skipped]")
            st.session_state.feedbacks.append("Skipped — no feedback.")
            st.session_state.scores.append(0)
            st.session_state.pronunciation_reports.append({})
            st.session_state.communication_scores.append({})
            st.session_state.follow_ups.append("")
            st.session_state.current_q += 1
            st.session_state.q_start_time = time.time()
            st.rerun()

    with col_hint:
        if st.button("💡 Hint", use_container_width=True):
            with st.spinner("Generating hint..."):
                try:
                    hint = st.session_state.interviewer.get_hint(q_text, st.session_state.job_role)
                    st.info(f"💡 {hint}")
                except Exception as e:
                    st.error(str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE: RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "results":
    scores = st.session_state.scores
    avg_score = sum(scores) / len(scores) if scores else 0
    total_time = getattr(st.session_state, 'total_time', 0)
    badge, _, badge_desc = get_performance_badge(avg_score)

    score_color = (
        "var(--c4)" if avg_score >= 80 else
        "var(--c1)" if avg_score >= 60 else
        "var(--c5)" if avg_score >= 40 else "var(--c3)"
    )
    ring_bg = (
        "rgba(52,211,153,0.1)" if avg_score >= 80 else
        "rgba(110,231,247,0.1)" if avg_score >= 60 else
        "rgba(251,191,36,0.1)" if avg_score >= 40 else "rgba(244,114,182,0.1)"
    )

    # ── Report Hero ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="report-hero fade-up">
      <div class="report-hero-orb"></div>
      <div style="font-family:'Playfair Display',serif;font-size:0.85rem;font-weight:700;
                  text-transform:uppercase;letter-spacing:0.15em;color:var(--muted);margin-bottom:0.5rem;">
        Interview Complete
      </div>
      <div style="font-family:'Playfair Display',serif;font-size:2.8rem;font-weight:800;color:var(--text);">
        Performance Report
      </div>
      <div style="color:var(--muted);margin-top:0.5rem;font-size:0.9rem;">
        {st.session_state.job_role} · {st.session_state.interview_type} · {st.session_state.difficulty}
      </div>
      <div style="
        width:160px; height:160px; border-radius:50%; margin:2rem auto 1rem;
        background:{ring_bg}; border:3px solid {score_color};
        display:flex; flex-direction:column; align-items:center; justify-content:center;
      ">
        <div style="font-family:'Playfair Display',serif;font-size:3.5rem;font-weight:800;
                    color:{score_color};line-height:1;">{avg_score:.0f}</div>
        <div style="color:var(--muted);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;">/100</div>
      </div>
      <div style="font-size:1.5rem;margin-bottom:0.25rem;">{badge}</div>
      <div style="font-family:'Playfair Display',serif;font-size:1.2rem;font-weight:700;color:{score_color};">{badge_desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics Row ────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Overall Score", f"{avg_score:.0f}/100")
    with m2: st.metric("Questions", len(scores))
    with m3: st.metric("Time Taken", f"{int(total_time//60)}m {int(total_time%60)}s")
    with m4:
        avg_comm = 0
        if st.session_state.communication_scores:
            valid = [c for c in st.session_state.communication_scores if c]
            if valid:
                all_vals = [v for c in valid for v in c.values() if isinstance(v, (int, float))]
                avg_comm = sum(all_vals) / len(all_vals) if all_vals else 0
        st.metric("Communication", f"{avg_comm:.0f}/100")

    st.markdown("---")

    # ── Detail Tabs ────────────────────────────────────────────────────────────
    tab_qa, tab_pronun, tab_comm, tab_scores_tab, tab_summary = st.tabs([
        "📝 Q&A Review",
        "🗣️ Pronunciation",
        "📡 Communication",
        "📊 Score Analysis",
        "🎯 AI Summary"
    ])

    # ── Q&A Review ─────────────────────────────────────────────────────────────
    with tab_qa:
        for i, (q, ans, fb, score, fu) in enumerate(zip(
            st.session_state.questions, st.session_state.answers,
            st.session_state.feedbacks, st.session_state.scores,
            st.session_state.follow_ups
        )):
            sc = "var(--c4)" if score >= 80 else "var(--c1)" if score >= 60 else "var(--c5)" if score >= 40 else "var(--c3)"
            fb_cls = "fb-excellent" if score >= 80 else "fb-good" if score >= 60 else "fb-average" if score >= 40 else "fb-poor"
            with st.expander(f"Q{i+1} — Score: {score}/100  |  {q[:65]}{'...' if len(q)>65 else ''}"):
                st.markdown(f"""
                <div class="question-panel" style="margin-bottom:1rem;">
                  <div class="q-badge">Question {i+1}</div>
                  <div style="color:var(--text);font-size:1.05rem;line-height:1.65;">{q}</div>
                </div>
                <div style="margin-bottom:1rem;">
                  <div class="card-label" style="margin-bottom:0.4rem;">Your Answer</div>
                  <div style="background:var(--bg2);border:1px solid var(--border);border-radius:10px;
                               padding:1rem;color:var(--text);font-size:0.95rem;line-height:1.7;">
                    {ans if ans != '[Skipped]' else '<em style="color:var(--muted)">Skipped</em>'}
                  </div>
                </div>
                <div class="fb-panel {fb_cls}">
                  <div class="fb-score" style="color:{sc};">{score}/100</div>
                  <div style="color:var(--muted);font-size:0.78rem;margin-bottom:0.75rem;">Content & Answer Quality</div>
                  <div style="color:var(--text);line-height:1.75;font-size:0.95rem;">{fb}</div>
                </div>
                """, unsafe_allow_html=True)
                if fu:
                    st.markdown(f"""
                    <div class="glass-card" style="border-color:rgba(110,231,247,0.2);background:rgba(110,231,247,0.04);margin-top:0.75rem;">
                      <div style="color:var(--c1);font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">
                        🔄 Follow-up Question
                      </div>
                      <div style="color:var(--text);font-size:0.95rem;">{fu}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── Pronunciation Tab ──────────────────────────────────────────────────────
    with tab_pronun:
        st.markdown("""
        <div style="font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:800;margin-bottom:0.25rem;">
          Pronunciation & Language Coach
        </div>
        <div style="color:var(--muted);font-size:0.88rem;margin-bottom:1.5rem;">
          Detailed analysis of your language, word choice, and pronunciation patterns.
        </div>
        """, unsafe_allow_html=True)

        pron_reports = st.session_state.pronunciation_reports
        for i, (pr, ans) in enumerate(zip(pron_reports, st.session_state.answers)):
            if not pr or ans == "[Skipped]":
                continue
            with st.expander(f"Q{i+1} — Pronunciation Analysis"):
                if isinstance(pr, dict):
                    # Overall language score
                    lang_score = pr.get("language_score", 70)
                    sc = "var(--c4)" if lang_score >= 80 else "var(--c1)" if lang_score >= 60 else "var(--c5)"
                    st.markdown(f"""
                    <div class="pronun-box">
                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                        <div>
                          <div class="card-label">Language Quality Score</div>
                          <div style="font-family:'DM Mono',monospace;font-size:2rem;font-weight:700;color:{sc};">{lang_score}/100</div>
                        </div>
                        <div style="text-align:right;">
                          <div class="card-label">Clarity</div>
                          <div style="font-size:1.2rem;font-weight:700;color:var(--c2);">{pr.get('clarity', 'N/A')}</div>
                        </div>
                      </div>
                    """, unsafe_allow_html=True)

                    # Mispronounced/misused words
                    corrections = pr.get("corrections", [])
                    if corrections:
                        st.markdown(f"""
                        <div class="fb-section-title" style="color:var(--c3);">⚠️ Words to Improve</div>
                        """, unsafe_allow_html=True)
                        for c in corrections[:8]:
                            if isinstance(c, dict):
                                st.markdown(f"""
                                <div class="pronunciation-item">
                                  <div style="flex:1;">
                                    <div style="margin-bottom:0.25rem;">
                                      <span class="wrong-word">{c.get('word','')}</span>
                                      <span style="color:var(--muted);margin:0 0.5rem;">→</span>
                                      <span class="correct-word">{c.get('correct','')}</span>
                                    </div>
                                    <div style="color:var(--muted);font-size:0.82rem;">{c.get('tip','')}</div>
                                    {f'<div class="phonetic" style="margin-top:0.4rem;">{c.get("phonetic","")}</div>' if c.get('phonetic') else ''}
                                  </div>
                                </div>
                                """, unsafe_allow_html=True)

                    # Good phrases
                    good = pr.get("good_phrases", [])
                    if good:
                        st.markdown(f'<div class="fb-section-title" style="color:var(--c4);">✅ Strong Language Used</div>', unsafe_allow_html=True)
                        for g in good[:5]:
                            st.markdown(f'<span class="chip chip-green" style="margin:0.2rem;">{g}</span>', unsafe_allow_html=True)

                    # Filler words
                    fillers = pr.get("filler_words", [])
                    if fillers:
                        st.markdown(f'<div class="fb-section-title" style="color:var(--c5);">⚡ Filler Words Detected</div>', unsafe_allow_html=True)
                        for f in fillers:
                            st.markdown(f'<span class="chip chip-amber" style="margin:0.2rem;">{f}</span>', unsafe_allow_html=True)
                        st.markdown('<div style="color:var(--muted);font-size:0.82rem;margin-top:0.5rem;">Try to reduce filler words — they signal hesitation.</div>', unsafe_allow_html=True)

                    # Overall tip
                    tip = pr.get("overall_tip", "")
                    if tip:
                        st.markdown(f"""
                        <div style="background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.2);
                                     border-radius:10px;padding:1rem;margin-top:1rem;">
                          <div style="color:var(--c2);font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">
                            🎯 Key Recommendation
                          </div>
                          <div style="color:var(--text);font-size:0.92rem;line-height:1.6;">{tip}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="color:var(--text);line-height:1.7;">{pr}</div>', unsafe_allow_html=True)

    # ── Communication Tab ──────────────────────────────────────────────────────
    with tab_comm:
        st.markdown("""
        <div style="font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:800;margin-bottom:0.25rem;">
          Communication Skills Analysis
        </div>
        <div style="color:var(--muted);font-size:0.88rem;margin-bottom:1.5rem;">
          Breakdown of your overall communication effectiveness across all answers.
        </div>
        """, unsafe_allow_html=True)

        comm_scores_list = st.session_state.communication_scores
        valid_comm = [c for c in comm_scores_list if c and isinstance(c, dict)]

        if valid_comm:
            # Aggregate scores
            dims = ["clarity", "confidence", "vocabulary", "structure", "conciseness", "professionalism"]
            dim_labels = {
                "clarity": "Clarity & Articulation",
                "confidence": "Confidence & Tone",
                "vocabulary": "Vocabulary & Word Choice",
                "structure": "Answer Structure",
                "conciseness": "Conciseness",
                "professionalism": "Professionalism",
            }
            agg = {}
            for dim in dims:
                vals = [c.get(dim, 0) for c in valid_comm if isinstance(c.get(dim, 0), (int, float))]
                agg[dim] = sum(vals) / len(vals) if vals else 0

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-family:\'Playfair Display\',serif;font-size:1.1rem;font-weight:800;margin-bottom:1.25rem;">📡 Average Communication Scores</div>', unsafe_allow_html=True)

            for dim, label in dim_labels.items():
                val = agg.get(dim, 0)
                bar_color = (
                    "linear-gradient(90deg,#34d399,#6ee7f7)" if val >= 75 else
                    "linear-gradient(90deg,#a78bfa,#6ee7f7)" if val >= 55 else
                    "linear-gradient(90deg,#fbbf24,#f59e0b)" if val >= 40 else
                    "linear-gradient(90deg,#f472b6,#ef4444)"
                )
                st.markdown(f"""
                <div class="comm-bar-wrap">
                  <div class="comm-bar-label">
                    <span>{label}</span>
                    <span style="color:{'#34d399' if val>=75 else '#6ee7f7' if val>=55 else '#fbbf24' if val>=40 else '#f472b6'};font-family:'DM Mono',monospace;">{val:.0f}/100</span>
                  </div>
                  <div class="comm-bar-track">
                    <div class="comm-bar-fill" style="width:{val}%;background:{bar_color};"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Per-question communication breakdown
            st.markdown('<div style="font-family:\'Playfair Display\',serif;font-size:1.1rem;font-weight:800;margin:1.5rem 0 0.75rem;">Per-Question Breakdown</div>', unsafe_allow_html=True)
            for i, (cs, ans) in enumerate(zip(comm_scores_list, st.session_state.answers)):
                if not cs or ans == "[Skipped]":
                    continue
                with st.expander(f"Q{i+1} — Communication Details"):
                    c1_, c2_, c3_ = st.columns(3)
                    pairs = list(cs.items())[:6]
                    for j, (k, v) in enumerate(pairs):
                        col = [c1_, c2_, c3_][j % 3]
                        with col:
                            if isinstance(v, (int, float)):
                                vc = "#34d399" if v >= 75 else "#6ee7f7" if v >= 55 else "#fbbf24" if v >= 40 else "#f472b6"
                                st.markdown(f"""
                                <div style="text-align:center;padding:0.75rem;background:var(--bg2);
                                             border-radius:10px;border:1px solid var(--border);margin-bottom:0.5rem;">
                                  <div style="font-size:1.5rem;font-weight:800;color:{vc};font-family:'DM Mono',monospace;">{v:.0f}</div>
                                  <div style="color:var(--muted);font-size:0.75rem;text-transform:capitalize;">{k.replace('_',' ')}</div>
                                </div>
                                """, unsafe_allow_html=True)
        else:
            st.info("💡 Communication scores will appear here after submitting answers.")

    # ── Score Analysis Tab ─────────────────────────────────────────────────────
    with tab_scores_tab:
        st.markdown('<div style="color:var(--muted);font-size:0.88rem;margin-bottom:1rem;">Score per question (out of 100)</div>', unsafe_allow_html=True)
        score_data = {f"Q{i+1}": s for i, s in enumerate(scores)}
        st.bar_chart(score_data, color="#a78bfa", height=280)

        col_dist, col_stats = st.columns(2)
        with col_dist:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:800;margin-bottom:1rem;">Score Distribution</div>', unsafe_allow_html=True)
            buckets = [("🏆 Excellent (80–100)", 80, 101, "#34d399"),
                       ("✅ Good (60–79)", 60, 80, "#6ee7f7"),
                       ("📊 Average (40–59)", 40, 60, "#fbbf24"),
                       ("📌 Needs Work (<40)", 0, 40, "#f472b6")]
            for label, lo, hi, color in buckets:
                count = sum(1 for s in scores if lo <= s < hi)
                pct = (count / len(scores) * 100) if scores else 0
                st.markdown(f"""
                <div style="margin-bottom:0.75rem;">
                  <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:0.25rem;">
                    <span style="color:var(--muted);">{label}</span>
                    <span style="color:{color};font-weight:700;">{count}</span>
                  </div>
                  <div class="prog-wrap" style="margin:0;">
                    <div class="prog-fill" style="width:{pct}%;background:linear-gradient(90deg,{color},{color}88);"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_stats:
            best_i = scores.index(max(scores)) + 1 if scores else 0
            worst_i = scores.index(min(scores)) + 1 if scores else 0
            st.markdown(f"""
            <div class="glass-card">
              <div style="font-weight:800;margin-bottom:1rem;">Highlights</div>
              <div style="display:grid;gap:0.75rem;">
                <div style="background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);border-radius:10px;padding:1rem;">
                  <div style="color:var(--c4);font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">🏆 Best Answer</div>
                  <div style="font-size:1.3rem;font-weight:800;">Q{best_i} — {max(scores) if scores else 0}/100</div>
                </div>
                <div style="background:rgba(244,114,182,0.08);border:1px solid rgba(244,114,182,0.2);border-radius:10px;padding:1rem;">
                  <div style="color:var(--c3);font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">📌 Needs Most Work</div>
                  <div style="font-size:1.3rem;font-weight:800;">Q{worst_i} — {min(scores) if scores else 0}/100</div>
                </div>
                <div style="background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.2);border-radius:10px;padding:1rem;">
                  <div style="color:var(--c2);font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">📈 Score Range</div>
                  <div style="font-size:1.3rem;font-weight:800;">±{(max(scores)-min(scores)) if scores else 0} pts</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Summary Tab ────────────────────────────────────────────────────────────
    with tab_summary:
        if not st.session_state.cached_summary:
            with st.spinner("🤖 Generating comprehensive performance summary..."):
                try:
                    st.session_state.cached_summary = st.session_state.interviewer.generate_summary(
                        questions=st.session_state.questions,
                        answers=st.session_state.answers,
                        scores=st.session_state.scores,
                        job_role=st.session_state.job_role,
                        interview_type=st.session_state.interview_type,
                    )
                except Exception as e:
                    st.session_state.cached_summary = f"Could not generate summary: {e}"

        st.markdown(f"""
        <div class="fb-panel fb-good" style="margin-top:1rem;">
          <div style="font-family:'Playfair Display',serif;font-size:1.2rem;font-weight:800;
                      margin-bottom:1rem;color:var(--c2);">🎯 AI Performance Summary</div>
          <div style="color:var(--text);line-height:1.85;font-size:0.97rem;
                      white-space:pre-wrap;">{st.session_state.cached_summary}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Footer Actions ─────────────────────────────────────────────────────────
    st.markdown("---")
    col_new, col_dl = st.columns(2)
    with col_new:
        if st.button("🔄 Start New Interview", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    with col_dl:
        lines = [
            "=" * 60,
            "VOICECOACH AI — PERFORMANCE REPORT",
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
            lines += [f"\nQ{i+1} [{score}/100]: {q}", f"Answer: {ans}", f"Feedback: {fb}", "-"*40]
        if st.session_state.cached_summary:
            lines += ["\nOVERALL AI SUMMARY:", st.session_state.cached_summary]
        st.download_button(
            "📥 Download Full Report",
            data="\n".join(lines),
            file_name=f"voicecoach_report_{st.session_state.job_role.replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
