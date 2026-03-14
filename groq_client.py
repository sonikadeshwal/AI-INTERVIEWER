"""
groq_client.py — Groq AI client for VoiceCoach AI
Model: llama-3.1-8b-instant (fast, free tier)
"""

import re
import json
from groq import Groq


class GroqInterviewer:
    MODEL = "llama-3.1-8b-instant"

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def _chat(self, system: str, user: str, max_tokens: int = 800, temperature: float = 0.5) -> str:
        resp = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()

    # ── Generate Questions ───────────────────────────────────────────────────
    def generate_questions(self, job_role, interview_type, difficulty, num_questions, resume_text=""):
        resume_ctx = f"\nCandidate background:\n{resume_text[:1500]}" if resume_text.strip() else ""
        difficulty_map = {
            "Beginner":     "entry-level, foundational, simple scenarios",
            "Intermediate": "mid-level, practical application, moderate complexity",
            "Advanced":     "senior-level, complex scenarios, leadership",
            "Expert":       "principal/architect level, extremely challenging",
        }
        type_map = {
            "Technical":  "technical skills, coding, system design, tools, algorithms",
            "Behavioral": "STAR-method situations, past experiences, soft skills, leadership",
            "HR":         "culture fit, motivation, career goals, work style",
            "Mixed":      "blend of technical, behavioral, and situational questions",
        }
        system = f"""You are a senior interviewer at a top company.
Generate exactly {num_questions} interview questions for a {job_role} position.
Type: {interview_type} — {type_map.get(interview_type, 'mixed')}
Difficulty: {difficulty} — {difficulty_map.get(difficulty, 'intermediate')}
{resume_ctx}
Rules:
- Output ONLY a numbered list: 1. Question
- No explanations, no sub-bullets, just the questions
- Each question must be realistic, specific, and professionally worded
- Vary topics across questions"""
        raw = self._chat(system, f"Generate {num_questions} questions.", max_tokens=1200, temperature=0.8)
        questions = []
        for line in raw.split("\n"):
            line = line.strip()
            if not line:
                continue
            cleaned = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
            if cleaned and len(cleaned) > 15:
                questions.append(cleaned)
        fallback = [
            f"Tell me about your experience as a {job_role}.",
            "Describe a challenging project and how you handled it.",
            "How do you manage competing priorities under pressure?",
            "What are your core technical strengths?",
            "Where do you see yourself professionally in 3 years?",
        ]
        while len(questions) < num_questions and fallback:
            questions.append(fallback.pop(0))
        return questions[:num_questions]

    # ── Evaluate Answer ──────────────────────────────────────────────────────
    def evaluate_answer(self, question, answer, job_role, interview_type, difficulty):
        system = """You are a senior hiring manager. Evaluate this interview answer.
Respond in EXACTLY this format (no deviations):
SCORE: [0-100]
STRENGTHS: [2-3 specific things done well, referencing the actual answer]
IMPROVEMENTS: [2-3 specific actionable improvements]
OVERALL: [2-3 sentence coaching summary]
Be specific, honest, and encouraging."""
        user = f"""Role: {job_role} | Type: {interview_type} | Difficulty: {difficulty}
Question: {question}
Answer: {answer}"""
        raw = self._chat(system, user, max_tokens=600, temperature=0.4)
        score = 60
        m = re.search(r"SCORE:\s*(\d+)", raw, re.IGNORECASE)
        if m:
            score = max(0, min(100, int(m.group(1))))
        fb = re.sub(r"SCORE:\s*\d+\s*\n?", "", raw).strip()
        fb = fb.replace("STRENGTHS:", "✅ **Strengths:**")
        fb = fb.replace("IMPROVEMENTS:", "📈 **Areas to Improve:**")
        fb = fb.replace("OVERALL:", "🎯 **Overall:**")
        return fb, score

    # ── Analyze Language ─────────────────────────────────────────────────────
    def analyze_language(self, answer: str, job_role: str) -> tuple:
        if not answer.strip() or answer == "[Skipped]":
            return self._default_pron(), self._default_comm()

        # Step 1: Pronunciation & Language
        pron_system = """You are an expert English language and pronunciation coach.
Analyze this interview answer text for language quality, word choice, and communication patterns.

Respond using EXACTLY this format with these exact labels:

LANGUAGE_SCORE: [number 0-100]
CLARITY: [Excellent / Good / Average / Poor]
OVERALL_TIP: [one sentence of the most important improvement tip]

FILLER_WORDS:
- [filler word found, e.g. um, uh, like, you know, basically, sort of, kind of, right]
- [add more or write: NONE]

CORRECTIONS:
- WRONG: [weak/incorrect phrase from text] | BETTER: [improved version] | PHONETIC: [pronunciation guide] | TIP: [brief reason]
- [up to 5 corrections or write: NONE]

GOOD_PHRASES:
- [strong professional phrase the person used]
- [up to 4 or write: NONE]

GRAMMAR_ISSUES:
- [grammar mistake and how to fix it]
- [up to 3 or write: NONE]

Rules:
- FILLER WORDS to catch: um, uh, like (used as filler), you know, basically, literally, sort of, kind of, right, okay so, I mean
- WEAK LANGUAGE: "I think maybe" -> "I am confident that" | "I guess" -> "I believe" | "I'm not sure but" -> remove
- Always provide phonetic guide for technical words (algorithm, infrastructure, architecture, asynchronous, etc.)
- Be specific and reference the actual words used in the answer"""

        pron_user = f"Job Role: {job_role}\n\nAnswer to analyze:\n{answer[:2000]}"

        try:
            pron_raw = self._chat(pron_system, pron_user, max_tokens=1000, temperature=0.3)
            pron = self._parse_pronunciation(pron_raw)
        except Exception:
            pron = self._default_pron()

        # Step 2: Communication scores
        comm_system = """You are a communication skills evaluator for job interviews.
Score this answer on exactly 6 dimensions. Reply with ONLY these 6 lines, nothing else:

CLARITY: [0-100]
CONFIDENCE: [0-100]
VOCABULARY: [0-100]
STRUCTURE: [0-100]
CONCISENESS: [0-100]
PROFESSIONALISM: [0-100]

Scoring:
CLARITY = how easy to understand (100 = crystal clear)
CONFIDENCE = sounds sure of themselves, no hedging language (100 = very confident)
VOCABULARY = professional appropriate words used (100 = excellent word choice)
STRUCTURE = organized answer with clear points (100 = perfectly structured)
CONCISENESS = makes point without rambling (100 = perfectly concise)
PROFESSIONALISM = formal interview-appropriate tone (100 = highly professional)"""

        comm_user = f"Score this interview answer:\n{answer[:1500]}"

        try:
            comm_raw = self._chat(comm_system, comm_user, max_tokens=150, temperature=0.2)
            comm = self._parse_communication(comm_raw)
        except Exception:
            comm = self._default_comm()

        return pron, comm

    def _parse_pronunciation(self, raw: str) -> dict:
        result = self._default_pron()
        try:
            m = re.search(r"LANGUAGE_SCORE:\s*(\d+)", raw, re.IGNORECASE)
            if m:
                result["language_score"] = max(0, min(100, int(m.group(1))))

            m = re.search(r"CLARITY:\s*(Excellent|Good|Average|Poor)", raw, re.IGNORECASE)
            if m:
                result["clarity"] = m.group(1).capitalize()

            m = re.search(r"OVERALL_TIP:\s*(.+?)(?:\n|$)", raw, re.IGNORECASE)
            if m:
                result["overall_tip"] = m.group(1).strip()

            result["filler_words"] = self._parse_bullets(
                self._extract_section(raw, "FILLER_WORDS"), max_items=6)

            corrections_section = self._extract_section(raw, "CORRECTIONS")
            corrections = []
            for line in corrections_section.split("\n"):
                line = line.strip().lstrip("-•*").strip()
                if not line or line.upper() == "NONE":
                    continue
                c = {}
                wm = re.search(r"WRONG:\s*(.+?)(?:\|)", line, re.IGNORECASE)
                bm = re.search(r"BETTER:\s*(.+?)(?:\|)", line, re.IGNORECASE)
                pm = re.search(r"PHONETIC:\s*(.+?)(?:\|)", line, re.IGNORECASE)
                tm = re.search(r"TIP:\s*(.+?)$", line, re.IGNORECASE)
                if wm: c["word"]     = wm.group(1).strip()
                if bm: c["correct"]  = bm.group(1).strip()
                if pm: c["phonetic"] = pm.group(1).strip()
                if tm: c["tip"]      = tm.group(1).strip()
                if c.get("word") and c.get("correct"):
                    corrections.append(c)
            result["corrections"] = corrections[:5]

            result["good_phrases"] = self._parse_bullets(
                self._extract_section(raw, "GOOD_PHRASES"), max_items=4)

            result["grammar_issues"] = self._parse_bullets(
                self._extract_section(raw, "GRAMMAR_ISSUES"), max_items=3)

        except Exception:
            pass
        return result

    def _parse_communication(self, raw: str) -> dict:
        result = self._default_comm()
        for key in result:
            m = re.search(rf"{key}:\s*(\d+)", raw, re.IGNORECASE)
            if m:
                result[key] = max(0, min(100, int(m.group(1))))
        return result

    def _extract_section(self, text: str, section_name: str) -> str:
        pattern = rf"{section_name}:\s*\n(.*?)(?=\n[A-Z_]{{3,}}:|$)"
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else ""

    def _parse_bullets(self, section: str, max_items: int = 5) -> list:
        items = []
        for line in section.split("\n"):
            line = line.strip().lstrip("-•*").strip()
            if not line or line.upper() == "NONE":
                continue
            items.append(line)
        return items[:max_items]

    def _default_pron(self) -> dict:
        return {
            "language_score": 65,
            "clarity": "Good",
            "overall_tip": "Focus on confident, specific language. Avoid filler words like 'um', 'uh', and 'basically'.",
            "filler_words": [],
            "corrections": [],
            "good_phrases": [],
            "grammar_issues": [],
        }

    def _default_comm(self) -> dict:
        return {
            "clarity": 65, "confidence": 60, "vocabulary": 65,
            "structure": 60, "conciseness": 65, "professionalism": 70,
        }

    # ── Follow-up ────────────────────────────────────────────────────────────
    def generate_follow_up(self, question: str, answer: str) -> str:
        try:
            system = "You are an interviewer. Generate ONE sharp follow-up question (max 20 words). Return ONLY the question, nothing else."
            user = f"Q: {question}\nA: {answer[:400]}\nFollow-up:"
            return self._chat(system, user, max_tokens=60, temperature=0.6)
        except Exception:
            return ""

    # ── Hint ─────────────────────────────────────────────────────────────────
    def get_hint(self, question: str, job_role: str) -> str:
        system = "You are a career coach. Give a brief helpful hint (2-3 sentences) on how to approach this interview question. Do not give the answer, just structure and direction."
        user = f"Role: {job_role}\nQuestion: {question}"
        return self._chat(system, user, max_tokens=140, temperature=0.5)

    # ── Summary ───────────────────────────────────────────────────────────────
    def generate_summary(self, questions, answers, scores, job_role, interview_type):
        avg = sum(scores) / len(scores) if scores else 0
        qa = "\n".join([
            f"Q{i+1} [Score:{s}/100]: {q}\nA: {a[:250]}"
            for i, (q, a, s) in enumerate(zip(questions, answers, scores))
        ])
        system = """You are a senior hiring manager writing a post-interview performance review.
Write a detailed personalized summary with these 5 sections:
1. Overall Assessment
2. Key Strengths
3. Primary Areas for Improvement
4. Top 3 Actionable Recommendations for the next 30 days
5. Hiring Recommendation (Strong Yes / Yes / Maybe / No with reason)
Be specific, reference actual answers, and be constructive. Use plain text with numbered headers."""
        user = f"Role: {job_role} | Type: {interview_type} | Avg Score: {avg:.0f}/100\n\n{qa}"
        return self._chat(system, user, max_tokens=1000, temperature=0.5)
