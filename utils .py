"""
utils.py — Constants and helper functions for InterviewAI
"""

# ── Job Roles ──────────────────────────────────────────────────────────────────
JOB_ROLES = [
    # Engineering
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Mobile Developer (iOS/Android)",
    "DevOps / SRE Engineer",
    "Cloud Architect",
    "Data Engineer",
    "Machine Learning Engineer",
    "AI/LLM Engineer",
    "Embedded Systems Engineer",
    "QA / Test Engineer",
    "Security Engineer",
    "Blockchain Developer",
    # Data & Analytics
    "Data Scientist",
    "Data Analyst",
    "Business Intelligence Analyst",
    "Research Scientist",
    # Product & Design
    "Product Manager",
    "Product Designer / UX Designer",
    "UI Designer",
    "UX Researcher",
    "Technical Program Manager",
    # Leadership
    "Engineering Manager",
    "VP of Engineering",
    "CTO",
    "Head of Product",
    # Business & Operations
    "Marketing Manager",
    "Growth Hacker",
    "Sales Engineer",
    "Account Executive",
    "Customer Success Manager",
    "Operations Manager",
    "Business Analyst",
    "Financial Analyst",
    "HR Manager",
    "Recruiter",
    # Finance & Legal
    "Quantitative Analyst",
    "Investment Banker",
    "Financial Planner",
    # Healthcare & Science
    "Biomedical Engineer",
    "Clinical Data Scientist",
    "Healthcare IT Specialist",
    # Other Tech
    "IT Support Specialist",
    "Systems Administrator",
    "Network Engineer",
    "Prompt Engineer",
    "MLOps Engineer",
    "Solutions Architect",
    "Technical Writer",
]

# ── Interview Types ────────────────────────────────────────────────────────────
INTERVIEW_TYPES = [
    "Technical",
    "Behavioral",
    "HR",
    "Mixed",
]

# ── Difficulty Levels ──────────────────────────────────────────────────────────
DIFFICULTY_LEVELS = [
    "Beginner",
    "Intermediate",
    "Advanced",
    "Expert",
]

# ── Performance Badges ─────────────────────────────────────────────────────────
def get_performance_badge(score: float) -> tuple[str, str, str]:
    """Returns (emoji, hex_color, label) based on average score."""
    if score >= 90:
        return "🏆", "#00f5d4", "Outstanding Performance"
    elif score >= 80:
        return "⭐", "#00f5d4", "Excellent Performance"
    elif score >= 70:
        return "✅", "#7c3aed", "Good Performance"
    elif score >= 60:
        return "📈", "#a78bfa", "Above Average"
    elif score >= 50:
        return "📊", "#ffd60a", "Average Performance"
    elif score >= 40:
        return "📌", "#ffd60a", "Below Average"
    else:
        return "🔄", "#f72585", "Needs Significant Practice"


def calculate_score(scores: list[int]) -> float:
    """Calculate weighted average score."""
    if not scores:
        return 0.0
    # Weight later questions slightly more (shows consistency)
    weights = [1 + (i * 0.05) for i in range(len(scores))]
    weighted = sum(s * w for s, w in zip(scores, weights))
    return weighted / sum(weights)


def format_feedback(feedback: str) -> str:
    """Apply basic HTML formatting to feedback text."""
    lines = feedback.strip().split("\n")
    formatted = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("**") and line.endswith("**"):
            formatted.append(f"<strong>{line[2:-2]}</strong>")
        elif line.startswith("- "):
            formatted.append(f"• {line[2:]}")
        else:
            formatted.append(line)
    return "<br>".join(formatted)


def time_grade(seconds_taken: int, time_limit: int) -> str:
    """Grade time management."""
    ratio = seconds_taken / time_limit if time_limit > 0 else 1
    if ratio < 0.3:
        return "Too Brief"
    elif ratio < 0.6:
        return "Concise"
    elif ratio < 0.85:
        return "Well-Paced"
    elif ratio <= 1.0:
        return "Good Timing"
    else:
        return "Over Time"
