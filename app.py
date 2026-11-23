from html import escape as esc
from pathlib import Path
import pandas as pd
import streamlit as st
import tomllib

BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "settings.toml", "rb") as f:
    cfg = tomllib.load(f)

st.set_page_config(
    page_title=cfg["title"],
    page_icon=cfg["icon"],
    layout="wide",
    initial_sidebar_state="expanded",
)

# 1. State Initialization (tanpa data dummy bawaan)
st.session_state.setdefault("view", "landing")  # "landing" | "login" | "signup" | "app"
st.session_state.setdefault("accounts", {})
st.session_state.setdefault("active_page", "Profil")
st.session_state.setdefault("selected_comp", "Semua Kompetisi")
st.session_state.setdefault("user_profile", {
    "name": "", "major": "", "year": 2026, "campus": "",
    "role": "Software / Fullstack Developer", "skills": [],
    "level": "Menengah", "availability": "", "contact": "", "portfolio": ""
})
st.session_state.setdefault("competitions", [])
st.session_state.setdefault("candidates", [])
st.session_state.setdefault("teams", [])

SKILL_OPTS = ["Python", "Machine Learning", "UI/UX", "Frontend/Web", "Business Analysis", "Finance", "Public Speaking", "Pitching", "Backend", "Cyber Security"]
ROLE_OPTS = ["Software / Fullstack Developer", "Frontend Developer", "Backend Developer", "UI/UX Designer", "Data / ML Engineer", "Business Analyst", "Product & Pitcher"]
CAT_OPTS = ["Hackathon", "Business Case", "UI/UX Design", "Data Science", "Competitive Programming"]
LEVEL_OPTS = ["Pemula", "Menengah", "Mahir"]
LEVEL_WEIGHTS = {"Pemula": 0.6, "Menengah": 0.8, "Mahir": 1.0}
PAGES = ["Profil", "Kompetisi", "Rekomendasi", "Tim Saya"]

BG_PHOTOS = {
    "auth": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=2000&q=85",
    "Profil": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=1920&q=85",
    "Kompetisi": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1920&q=85",
    "Rekomendasi": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1920&q=85",
    "Tim Saya": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1920&q=85",
}


# 2. Helper Functions (PEP 8 snake_case + one-line docstring sesuai README.md)
def html(markup: str) -> None:
    """Render compact HTML string inside full-width Streamlit markdown container."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()), unsafe_allow_html=True)


def set_view(target: str) -> None:
    """Switch top-level application view and trigger rerun."""
    st.session_state.view = target
    st.rerun()


def avatar(name: str, size: int = 40) -> str:
    """Return HTML squared monogram badge for a given name."""
    ch = esc((name or "?")[:1].upper())
    return f'<div class="monogram" style="--s:{size}px">{ch}</div>'


def badges(items: list, muted: bool = False) -> str:
    """Render a list of strings as structured rectangular tag spans."""
    cls = "rect-tag subtle" if muted else "rect-tag"
    return "".join(f'<span class="{cls}">{esc(str(s))}</span>' for s in items)


def safe_url(url: str) -> str:
    """Ensure a URL string starts with http:// or https://."""
    u = url.strip()
    return u if u.startswith(("http://", "https://")) else f"https://{u}"


def compute_match_score(user: dict, cand: dict, comp: dict | None = None) -> int:
    """Compute matching percentage using README formula: 0.5*skill + 0.3*role + 0.2*time."""
    if "match" in cand and not comp:
        return int(cand["match"])

    u_skills = set(user.get("skills", []))
    c_skills = set(cand.get("skills", []))
    req_skills = set(comp.get("required_skills", [])) if comp else (u_skills | c_skills)
    weight = LEVEL_WEIGHTS.get(cand.get("level", "Menengah"), 0.8)

    if req_skills:
        overlap = len(c_skills & req_skills) / max(len(req_skills), 1)
    else:
        comp_skills = len(c_skills - u_skills) + 0.5 * len(c_skills & u_skills)
        overlap = min(1.0, comp_skills / max(len(u_skills) or 1, 3))
    skill_score = min(1.0, overlap * weight + 0.25)

    c_role = cand.get("role", "")
    needed_roles = comp.get("roles_needed", []) if comp else []
    if needed_roles:
        role_score = 1.0 if c_role in needed_roles else 0.55
    else:
        role_score = 1.0 if c_role and c_role != user.get("role") else 0.7

    u_time = set(user.get("availability", "").lower().replace(",", " ").split())
    c_time_raw = (cand.get("availability") or cand.get("avail", "")).lower()
    c_time = set(c_time_raw.replace(",", " ").split())
    if "fleksibel" in c_time_raw or (u_time and (u_time & c_time)):
        time_score = 1.0
    elif not u_time or not c_time:
        time_score = 0.75
    else:
        time_score = 0.5

    final = round((skill_score * 0.5 + role_score * 0.3 + time_score * 0.2) * 100)
    return max(1, min(99, final))


# 3. Architectural CSS + Scroll-Driven Animations (Apple / ASUS Product Showcase Style)
curr_view = st.session_state.view
is_app = curr_view == "app"
curr_page = st.session_state.active_page if st.session_state.active_page in PAGES else "Profil"
active_bg_url = BG_PHOTOS[curr_page] if is_app else BG_PHOTOS["auth"]

bg_css = f"""
.stApp {{
    background-image:
        radial-gradient(circle at 16% 14%, rgba(166, 123, 91, 0.22) 0%, transparent 48%),
        radial-gradient(circle at 86% 82%, rgba(139, 94, 60, 0.18) 0%, transparent 52%),
        linear-gradient(135deg, rgba(10, 8, 7, {'0.88' if is_app else '0.62'}) 0%, rgba(14, 11, 9, {'0.80' if is_app else '0.78'}) 50%, rgba(10, 8, 7, {'0.91' if is_app else '0.92'}) 100%),
        url('{active_bg_url}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    transition: background-image 0.5s ease-in-out;
}}
.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(650px circle at 25% 25%, rgba(196, 154, 108, 0.11), transparent 70%),
        radial-gradient(550px circle at 78% 72%, rgba(139, 94, 60, 0.10), transparent 70%);
    pointer-events: none;
    z-index: 0;
    animation: ambientDrift 12s ease-in-out infinite alternate;
}}
"""

sidebar_dock_css = """
section[data-testid="stSidebar"] {
    display: block !important;
    position: fixed !important;
    top: 50% !important;
    left: 0 !important;
    transform: translateY(-50%) translateX(-238px) !important;
    width: 244px !important;
    min-width: 244px !important;
    max-width: 244px !important;
    height: auto !important;
    max-height: 86vh !important;
    background: rgba(18, 14, 12, 0.92) !important;
    backdrop-filter: blur(32px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(32px) saturate(180%) !important;
    border: 1px solid rgba(196, 154, 108, 0.36) !important;
    border-left: none !important;
    border-radius: 0 18px 18px 0 !important;
    box-shadow: 0 28px 70px rgba(0, 0, 0, 0.9) !important;
    z-index: 999999 !important;
    opacity: 1 !important;
    transition: transform 0.34s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.28s ease !important;
    overflow: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 20px 18px 22px !important;
    overflow: visible !important;
}
section[data-testid="stSidebar"]::before {
    content: "";
    position: absolute;
    top: -25vh;
    bottom: -25vh;
    right: -44px;
    width: 52px;
    background: transparent;
}
section[data-testid="stSidebar"]::after {
    content: "☰  MENU";
    position: absolute;
    top: 50%;
    right: -34px;
    transform: translateY(-50%);
    writing-mode: vertical-rl;
    text-orientation: mixed;
    letter-spacing: 0.18em;
    font-size: 10px;
    font-weight: 800;
    color: #F5EBE1;
    background: linear-gradient(180deg, #9C6B43, #6F4E37);
    border: 1px solid rgba(212, 163, 115, 0.65);
    border-left: none;
    padding: 16px 8px;
    border-radius: 0 10px 10px 0;
    box-shadow: 6px 0 22px rgba(0, 0, 0, 0.75);
    cursor: pointer;
    animation: dockPulse 3s ease-in-out infinite;
    transition: opacity 0.2s ease, transform 0.2s ease;
}
section[data-testid="stSidebar"]:hover,
section[data-testid="stSidebar"]:focus-within {
    transform: translateY(-50%) translateX(0) !important;
}
section[data-testid="stSidebar"]:hover::after {
    opacity: 0 !important;
    pointer-events: none;
}
section[data-testid="stSidebar"] .stButton > button {
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 0 14px !important;
    height: 42px !important;
    border-radius: 10px !important;
    transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1), background 0.16s ease, border-color 0.16s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    transform: scale(1.045) translateX(6px) !important;
}
""" if is_app else """
section[data-testid="stSidebar"] { display: none !important; }
"""

html(f"""<style>
@import url('https://fonts.cdnfonts.com/css/gotham-6');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

:root, .stApp, [data-testid="stAppViewContainer"] {{
    color-scheme: dark;
    --primary-color: #8B5E3C !important;
    --bg: #0A0908;
    --card: rgba(20, 16, 14, 0.76);
    --surface: rgba(24, 20, 17, 0.80);
    --surface-2: rgba(36, 30, 25, 0.88);
    --brown: #8B5E3C;
    --brown-dark: #6F4E37;
    --brown-light: #C49A6C;
    --brown-soft: rgba(139, 94, 60, 0.20);
    --border: rgba(212, 163, 115, 0.18);
    --border-strong: rgba(196, 154, 108, 0.48);
    --ink: #F5F2EB;
    --muted: #B0A69D;
    --subtle: #7A7168;
}}

/* Keyframe Animations */
@keyframes staggerUp {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes barGrow {{
    from {{ width: 0%; }}
}}
@keyframes ambientDrift {{
    0% {{ transform: translate3d(-2%, -2%, 0) scale(1); opacity: 0.75; }}
    100% {{ transform: translate3d(3%, 2%, 0) scale(1.08); opacity: 1; }}
}}
@keyframes dockPulse {{
    0%, 100% {{ box-shadow: 4px 0 18px rgba(139, 94, 60, 0.35); }}
    50% {{ box-shadow: 6px 0 28px rgba(196, 154, 108, 0.72); }}
}}
@keyframes floatBounce {{
    0%, 100% {{ transform: translateY(0); opacity: 0.65; }}
    50% {{ transform: translateY(8px); opacity: 1; }}
}}

/* Scroll-Driven Animations (Apple / ASUS Scroll Reveal) */
@keyframes scrollRevealUp {{
    0% {{ opacity: 0; transform: translateY(70px) scale(0.93); filter: blur(8px); }}
    100% {{ opacity: 1; transform: translateY(0) scale(1); filter: blur(0px); }}
}}
@keyframes scrollRevealLeft {{
    0% {{ opacity: 0; transform: translateX(-60px) scale(0.95); filter: blur(6px); }}
    100% {{ opacity: 1; transform: translateX(0) scale(1); filter: blur(0px); }}
}}
@keyframes scrollRevealRight {{
    0% {{ opacity: 0; transform: translateX(60px) scale(0.95); filter: blur(6px); }}
    100% {{ opacity: 1; transform: translateX(0) scale(1); filter: blur(0px); }}
}}
@keyframes scrollScaleIn {{
    0% {{ opacity: 0; transform: scale(0.86) translateY(40px); filter: blur(10px); }}
    100% {{ opacity: 1; transform: scale(1) translateY(0); filter: blur(0px); }}
}}

@supports (animation-timeline: view()) {{
    .sr-up {{
        animation: scrollRevealUp linear both;
        animation-timeline: view();
        animation-range: entry 5% cover 30%;
    }}
    .sr-left {{
        animation: scrollRevealLeft linear both;
        animation-timeline: view();
        animation-range: entry 8% cover 32%;
    }}
    .sr-right {{
        animation: scrollRevealRight linear both;
        animation-timeline: view();
        animation-range: entry 8% cover 32%;
    }}
    .sr-scale {{
        animation: scrollScaleIn linear both;
        animation-timeline: view();
        animation-range: entry 6% cover 32%;
    }}
}}

html, body, .stApp, [data-testid="stMarkdownContainer"], input, textarea, button, label, select, div {{
    font-family: 'Gotham', 'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    scroll-behavior: smooth;
}}
header[data-testid="stHeader"],
[data-testid="stHeaderActionElements"],
[data-testid="stSidebarHeader"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}
{bg_css}
{sidebar_dock_css}

/* KUNCI RATA KANAN-KIRI 100% */
[data-testid="stMain"],
[data-testid="stAppViewBlockContainer"] {{
    width: 100% !important;
    margin-left: 0 !important;
    position: relative;
    z-index: 1;
}}
.block-container {{
    max-width: 1080px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding-top: {'2rem' if is_app else '2.5rem'} !important;
    padding-bottom: 4rem !important;
    animation: staggerUp .35s cubic-bezier(0.16, 1, 0.3, 1);
}}
div.stMarkdown,
.stMarkdown,
[data-testid="stMarkdown"],
[data-testid="stMarkdownContainer"],
div.stElementContainer,
.stElementContainer,
[data-testid="stElementContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stForm"] {{
    width: 100% !important;
    max-width: 100% !important;
}}
[data-testid="stHorizontalBlock"] {{
    gap: 1rem !important;
    align-items: flex-start !important;
    width: 100% !important;
}}
[data-testid="stMarkdownContainer"] h4 {{
    font-size: 15.5px !important; font-weight: 700 !important;
    letter-spacing: -0.02em !important; color: var(--ink) !important;
    margin: 0 0 .4rem 0 !important;
}}

/* Warna Coklat (Espresso / Bronze) pada Tag Multiselect & Tabs */
span[data-baseweb="tag"],
[data-baseweb="select"] span[data-baseweb="tag"] {{
    background-color: var(--brown-dark) !important;
    background: var(--brown-dark) !important;
    border: 1px solid var(--brown-light) !important;
    border-radius: 6px !important;
    color: #FDFBF7 !important;
    filter: none !important;
    transition: transform 0.15s ease !important;
}}
span[data-baseweb="tag"]:hover {{ transform: translateY(-1px); }}
span[data-baseweb="tag"] * {{
    color: #FDFBF7 !important;
    font-weight: 600 !important;
}}
[data-baseweb="tab-highlight"] {{
    background-color: var(--brown-light) !important;
}}
[data-baseweb="tab"][aria-selected="true"] p,
[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--brown-light) !important;
    font-weight: 700 !important;
}}
button.step-up:hover, button.step-down:hover,
button.step-up:active, button.step-down:active {{
    background-color: var(--brown) !important;
    color: #FFFFFF !important;
}}

/* Translucent Frosted Glass Cards & Forms */
.arch-card, [data-testid="stForm"] {{
    width: 100% !important;
    background: var(--card) !important;
    backdrop-filter: blur(26px) saturate(165%) !important;
    -webkit-backdrop-filter: blur(26px) saturate(165%) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 24px 26px !important;
    box-sizing: border-box !important;
    box-shadow: 0 22px 50px rgba(0, 0, 0, 0.5) !important;
    position: relative !important;
    overflow: hidden !important;
    animation: staggerUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) 0.05s both;
    transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.22s ease, box-shadow 0.22s ease !important;
}}
.arch-card::after {{
    content: "";
    position: absolute;
    top: 0;
    left: -120%;
    width: 75%;
    height: 100%;
    background: linear-gradient(115deg, transparent 20%, rgba(212, 163, 115, 0.11) 50%, transparent 80%);
    transform: skewX(-20deg);
    pointer-events: none;
    transition: left 0.65s cubic-bezier(0.16, 1, 0.3, 1);
}}
.arch-card.hoverable:hover {{
    transform: translateY(-3px);
    border-color: var(--border-strong) !important;
    box-shadow: 0 26px 55px -12px rgba(0, 0, 0, 0.72) !important;
}}
.arch-card.hoverable:hover::after {{
    left: 140%;
}}

/* Inputs & Placeholder Behavior */
[data-testid="stTextInputRootElement"],
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="select"] > div,
[data-baseweb="textarea"] {{
    background-color: rgba(18, 14, 12, 0.75) !important;
    border: 1px solid var(--border) !important;
    border-top-color: var(--border) !important;
    border-right-color: var(--border) !important;
    border-bottom-color: var(--border) !important;
    border-left-color: var(--border) !important;
    border-radius: 8px !important;
    color: var(--ink) !important;
    box-shadow: none !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease !important;
}}
[data-baseweb="input"] > div,
[data-baseweb="base-input"] > div {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
[data-testid="stTextInputRootElement"]:focus-within,
[data-baseweb="input"]:focus-within,
[data-baseweb="base-input"]:focus-within,
[data-baseweb="select"]:focus-within > div,
[data-baseweb="textarea"]:focus-within {{
    border: 1px solid var(--brown-light) !important;
    border-top-color: var(--brown-light) !important;
    border-right-color: var(--brown-light) !important;
    border-bottom-color: var(--brown-light) !important;
    border-left-color: var(--brown-light) !important;
    box-shadow: 0 0 0 1px var(--brown-light), 0 0 16px -4px rgba(196, 154, 108, 0.35) !important;
    background-color: rgba(28, 22, 18, 0.92) !important;
}}
[data-testid="InputInstructions"] {{
    position: absolute !important;
    top: 0 !important;
    bottom: auto !important;
    right: 42px !important;
    transform: translateY(-26px) !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    font-size: 10.5px !important;
    color: var(--muted) !important;
    opacity: 0.75 !important;
    display: flex !important;
    align-items: center !important;
    pointer-events: none !important;
    z-index: 5 !important;
}}
[data-testid="stTextInput"] > div:not(:has(button)) [data-testid="InputInstructions"] {{
    right: 14px !important;
}}
input::placeholder, textarea::placeholder {{
    transition: opacity 0.12s ease !important;
}}
input:focus::placeholder, textarea:focus::placeholder {{
    opacity: 0 !important;
    color: transparent !important;
}}
[data-testid="stTextInput"]:has(input:placeholder-shown) [data-testid="InputInstructions"] {{
    opacity: 0 !important;
}}

/* Buttons */
.stButton > button, .stFormSubmitButton > button, .action-link {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: -0.01em !important;
    height: 42px !important;
    padding: 0 14px !important;
    white-space: nowrap !important;
    transition: transform 0.16s cubic-bezier(0.34, 1.56, 0.64, 1), background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease !important;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover, .action-link:hover {{
    transform: translateY(-2px);
}}
.stButton > button:active, .stFormSubmitButton > button:active, .action-link:active {{
    transform: translateY(1px) scale(0.97) !important;
}}
[data-testid^="stBaseButton-primary"] {{
    background: linear-gradient(135deg, #9C6B43, #7A5233) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--brown-light) !important;
    box-shadow: 0 8px 20px -6px rgba(139, 94, 60, 0.5) !important;
}}
[data-testid^="stBaseButton-primary"] * {{
    color: #FFFFFF !important;
    font-weight: 700 !important;
}}
[data-testid^="stBaseButton-primary"]:hover {{
    background: linear-gradient(135deg, #B07B50, #8B5E3C) !important;
    box-shadow: 0 12px 26px -6px rgba(196, 154, 108, 0.65) !important;
}}
[data-testid^="stBaseButton-secondary"] {{
    background: rgba(24, 20, 17, 0.72) !important;
    backdrop-filter: blur(16px) !important;
    color: var(--ink) !important;
    border: 1px solid var(--border) !important;
}}
[data-testid^="stBaseButton-secondary"]:hover {{
    background: var(--brown-soft) !important;
    border-color: var(--brown-light) !important;
    color: #FFFFFF !important;
}}
.action-link {{
    display: inline-flex; align-items: center; justify-content: center;
    text-decoration: none !important;
    background: linear-gradient(135deg, #9C6B43, #7A5233);
    border: 1px solid var(--brown-light);
    color: #FFFFFF !important;
    font-weight: 700 !important;
}}
.action-link.secondary {{
    background: var(--surface-2); color: var(--ink) !important;
    border: 1px solid var(--border);
}}
.action-link.secondary:hover {{
    border-color: var(--brown-light); background: var(--brown-soft);
}}

/* ================= APPLE / ASUS SCROLLABLE LANDING PAGE STYLES ================= */
.landing-wrap {{
    width: 100% !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center !important;
    margin: 12vh auto 28px !important;
    animation: staggerUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) both;
}}
.landing-eyebrow {{
    width: 100%;
    text-align: center !important;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--brown-light);
    margin-bottom: 18px;
}}
.landing-title {{
    width: 100%;
    text-align: center !important;
    font-size: clamp(42px, 5.8vw, 72px);
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.04;
    color: #FFFFFF !important;
    margin: 0 auto 22px !important;
}}
.landing-sub {{
    width: 100%;
    max-width: 640px !important;
    text-align: center !important;
    font-size: clamp(15px, 1.4vw, 18px);
    line-height: 1.65;
    color: rgba(245, 242, 235, 0.84);
    margin: 0 auto 10px !important;
}}
.scroll-cue {{
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 12vh auto 14vh;
    animation: floatBounce 2.4s ease-in-out infinite;
}}
.scroll-cue-lbl {{
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
}}
.scroll-cue-line {{
    width: 1px;
    height: 44px;
    background: linear-gradient(180deg, var(--brown-light), transparent);
}}

/* Section Headers on Scroll */
.sec-head {{
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center !important;
    margin: 110px auto 40px;
}}
.sec-eyebrow {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--brown-light);
    margin-bottom: 12px;
}}
.sec-title {{
    font-size: clamp(28px, 3.8vw, 46px);
    font-weight: 800;
    letter-spacing: -0.035em;
    line-height: 1.08;
    color: #FFFFFF;
    margin-bottom: 14px;
}}
.sec-desc {{
    max-width: 620px;
    font-size: 15px;
    line-height: 1.6;
    color: var(--muted);
}}

/* Spec Bento Showcase (Section 2) */
.spec-master {{
    width: 100%;
    box-sizing: border-box;
    background: rgba(18, 14, 12, 0.84);
    backdrop-filter: blur(28px);
    border: 1px solid var(--border-strong);
    border-radius: 18px;
    padding: 36px 40px;
    margin-bottom: 20px;
    box-shadow: 0 30px 70px rgba(0, 0, 0, 0.65);
}}
.spec-grid-3 {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    width: 100%;
}}
.spec-box {{
    background: rgba(18, 15, 13, 0.80);
    backdrop-filter: blur(24px);
    border: 1px solid var(--border);
    border-top: 2px solid var(--brown-light);
    border-radius: 16px;
    padding: 28px 26px;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}}
.spec-box:hover {{
    transform: translateY(-5px);
    border-color: var(--border-strong);
    box-shadow: 0 24px 50px -12px rgba(0, 0, 0, 0.8);
}}
.spec-big-num {{
    font-size: clamp(38px, 4.2vw, 54px);
    font-weight: 800;
    letter-spacing: -0.04em;
    color: #FFFFFF;
    line-height: 1;
    margin: 10px 0 12px;
}}

/* Photographic Discipline Cards (Section 3) */
.role-showcase-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    width: 100%;
}}
.role-photo-card {{
    position: relative;
    height: 360px;
    border-radius: 18px;
    border: 1px solid var(--border);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 26px;
    box-sizing: border-box;
    box-shadow: 0 24px 55px rgba(0, 0, 0, 0.6);
}}
.role-photo-bg {{
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    transition: transform 0.65s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 0;
}}
.role-photo-card:hover .role-photo-bg {{
    transform: scale(1.08);
}}
.role-photo-content {{
    position: relative;
    z-index: 1;
}}

/* Workflow Timeline & Arena Strip (Section 4) */
.workflow-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    width: 100%;
    margin-bottom: 24px;
}}
.workflow-step {{
    background: rgba(18, 15, 13, 0.80);
    backdrop-filter: blur(22px);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px 20px;
    transition: border-color 0.2s ease, transform 0.2s ease;
}}
.workflow-step:hover {{
    border-color: var(--brown-light);
    transform: translateY(-3px);
}}
.arena-strip {{
    width: 100%;
    box-sizing: border-box;
    background: rgba(18, 14, 12, 0.82);
    backdrop-filter: blur(24px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 26px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}}
.landing-footer {{
    width: 100%;
    margin-top: 90px;
    padding-top: 28px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    font-size: 12px;
    color: var(--muted);
}}

/* Clean Editorial Header inside App */
.catalog-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 16px;
    padding-bottom: 16px;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border);
    animation: staggerUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
}}
.monogram {{
    flex: none; width: var(--s); height: var(--s); border-radius: 8px;
    background: var(--brown-soft); border: 1px solid var(--brown-light);
    display: flex; align-items: center; justify-content: center;
    color: var(--brown-light); font-weight: 800; font-size: calc(var(--s) * 0.42);
}}
.rect-tag {{
    display: inline-block; background: var(--brown-soft);
    color: #F5EBE1; border: 1px solid var(--border-strong);
    padding: 4px 10px; border-radius: 5px;
    font-size: 11.5px; font-weight: 600; margin: 2px 5px 2px 0;
    transition: transform 0.15s ease, background 0.15s ease;
}}
.rect-tag:hover {{
    transform: translateY(-1px);
    background: rgba(139, 94, 60, 0.34);
}}
.rect-tag.subtle {{
    background: rgba(255, 255, 255, 0.04); border-color: var(--border); color: var(--muted);
}}
.bar-track {{ height: 5px; border-radius: 3px; background: rgba(255,255,255,.10); overflow: hidden; margin: 12px 0; }}
.bar-fill {{
    display: block; height: 100%;
    background: linear-gradient(90deg, #8B5E3C, #D4A373);
    animation: barGrow 0.85s cubic-bezier(0.16, 1, 0.3, 1) both;
}}
</style>""")

# ==============================================================================
# STAGE 1: SCROLLABLE APPLE / ASUS SHOWCASE LANDING PAGE
# ==============================================================================
if curr_view == "landing":
    # --- SECTION 1: HERO UTAMA (Above the Fold) ---
    html("""
        <div class="landing-wrap">
            <div class="landing-eyebrow">CARI TEMAN LOMBA &nbsp;·&nbsp; FASILKOM UI</div>
            <div class="landing-title">Bangun Tim Terbaik.<br>Menangkan Kompetisi.</div>
            <div class="landing-sub">
                Platform kolaborasi mahasiswa untuk menemukan rekan satu frekuensi berdasarkan kesesuaian keahlian, peran tim, dan ketersediaan waktu.
            </div>
        </div>
    """)

    _, btn_left, btn_right, _ = st.columns([1.3, 0.7, 0.7, 1.3], gap="small")
    with btn_left:
        if st.button("Log In", key="hero_login", width="stretch", type="primary"):
            set_view("login")
    with btn_right:
        if st.button("Sign Up", key="hero_signup", width="stretch", type="secondary"):
            set_view("signup")

    html("""
        <div class="scroll-cue">
            <div class="scroll-cue-lbl">Scroll untuk Eksplorasi</div>
            <div class="scroll-cue-line"></div>
        </div>
    """)

    # --- SECTION 2: THE 50-30-20 MATCHING ENGINE (Scroll-Driven Spec Showcase) ---
    html("""
        <div class="sec-head sr-up">
            <div class="sec-eyebrow">ALGORITMA PENCOCOKAN OBJEKTIF</div>
            <div class="sec-title">Dirancang dengan presisi matematis.</div>
            <div class="sec-desc">
                Bukan sekadar daftar kontak. Setiap rekomendasi kandidat dihitung menggunakan pembobotan tiga variabel utama agar komposisi tim saling melengkapi.
            </div>
        </div>

        <div class="spec-master sr-scale">
            <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:16px;margin-bottom:18px;">
                <div>
                    <div style="font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--brown-light);margin-bottom:6px;">FORMULA SKOR KECOCOKAN</div>
                    <div style="font-size:clamp(20px, 2.5vw, 30px);font-weight:800;color:#fff;letter-spacing:-0.03em;">
                        Score = (0.50 × Skill) + (0.30 × Role) + (0.20 × Time)
                    </div>
                </div>
                <div style="font-size:13px;font-weight:700;color:var(--brown-light);background:var(--brown-soft);border:1px solid var(--border-strong);padding:6px 14px;border-radius:6px;">
                    Diurutkan Otomatis dari Skor Tertinggi
                </div>
            </div>
            <div style="display:grid;grid-template-columns:5fr 3fr 2fr;gap:6px;height:10px;border-radius:99px;overflow:hidden;background:rgba(255,255,255,.06);">
                <div style="background:linear-gradient(90deg,#8B5E3C,#C49A6C);"></div>
                <div style="background:rgba(196,154,108,.65);"></div>
                <div style="background:rgba(196,154,108,.35);"></div>
            </div>
            <div style="display:grid;grid-template-columns:5fr 3fr 2fr;gap:6px;margin-top:8px;font-size:11px;font-weight:700;color:var(--muted);">
                <div>50% SKILL OVERLAP</div>
                <div>30% ROLE FIT</div>
                <div>20% TIME OVERLAP</div>
            </div>
        </div>

        <div class="spec-grid-3">
            <div class="spec-box sr-left">
                <div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:var(--brown-light);">VARIABEL 01</div>
                <div class="spec-big-num">50%</div>
                <div style="font-size:18px;font-weight:800;color:#fff;margin-bottom:8px;">Skill Overlap</div>
                <div style="font-size:13px;color:var(--muted);line-height:1.6;">
                    Mengukur irisan maupun komplementaritas keahlian teknis (Python, ML, UI/UX, Finance) yang dikalikan dengan bobot tingkat kemahiran: Pemula (60%), Menengah (80%), dan Mahir (100%).
                </div>
            </div>
            <div class="spec-box sr-up">
                <div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:var(--brown-light);">VARIABEL 02</div>
                <div class="spec-big-num">30%</div>
                <div style="font-size:18px;font-weight:800;color:#fff;margin-bottom:8px;">Role Fit</div>
                <div style="font-size:13px;color:var(--muted);line-height:1.6;">
                    Memastikan tim tidak menumpuk di satu peran yang sama. Kandidat dengan peran yang sedang dibutuhkan oleh target kompetisimu mendapatkan prioritas skor tertinggi.
                </div>
            </div>
            <div class="spec-box sr-right">
                <div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:var(--brown-light);">VARIABEL 03</div>
                <div class="spec-big-num">20%</div>
                <div style="font-size:18px;font-weight:800;color:#fff;margin-bottom:8px;">Time Overlap</div>
                <div style="font-size:13px;color:var(--muted);line-height:1.6;">
                    Mencocokkan ketersediaan waktu luang mingguan antara kamu dan calon rekan tim agar eksekusi proyek, riset, dan latihan pitching berjalan tanpa kendala jadwal.
                </div>
            </div>
        </div>
    """)

    # --- SECTION 3: ANATOMI TIM JUARA (Photographic Discipline Cards) ---
    html(f"""
        <div class="sec-head sr-up">
            <div class="sec-eyebrow">KOMPOSISI LINTAS DISIPLIN</div>
            <div class="sec-title">Satu tim. Tiga kekuatan utama.</div>
            <div class="sec-desc">
                Kompetisi mahasiswa modern menuntut kolaborasi antara eksekusi kode, ketajaman analisis data, estetika antarmuka, dan strategi bisnis.
            </div>
        </div>

        <div class="role-showcase-grid">
            <div class="role-photo-card sr-left">
                <div class="role-photo-bg" style="background-image:linear-gradient(180deg, rgba(10,8,7,.15) 0%, rgba(10,8,7,.94) 85%), url('{BG_PHOTOS['Kompetisi']}');"></div>
                <div class="role-photo-content">
                    <div style="font-size:10.5px;font-weight:700;letter-spacing:.14em;color:var(--brown-light);margin-bottom:6px;">HACKATHON &amp; SOFTWARE</div>
                    <div style="font-size:22px;font-weight:800;color:#fff;margin-bottom:8px;letter-spacing:-0.02em;">Engineering &amp; Architecture</div>
                    <div style="font-size:13px;color:var(--muted);line-height:1.55;margin-bottom:14px;">
                        Membangun prototipe fungsional dari sisi frontend, arsitektur backend API, hingga keamanan siber dalam waktu terbatas.
                    </div>
                    <div>
                        <span class="rect-tag">Fullstack Dev</span>
                        <span class="rect-tag">Backend</span>
                        <span class="rect-tag">Cyber Security</span>
                    </div>
                </div>
            </div>

            <div class="role-photo-card sr-up">
                <div class="role-photo-bg" style="background-image:linear-gradient(180deg, rgba(10,8,7,.15) 0%, rgba(10,8,7,.94) 85%), url('{BG_PHOTOS['Profil']}');"></div>
                <div class="role-photo-content">
                    <div style="font-size:10.5px;font-weight:700;letter-spacing:.14em;color:var(--brown-light);margin-bottom:6px;">AI &amp; DATA SCIENCE</div>
                    <div style="font-size:22px;font-weight:800;color:#fff;margin-bottom:8px;letter-spacing:-0.02em;">Intelligence &amp; Analytics</div>
                    <div style="font-size:13px;color:var(--muted);line-height:1.55;margin-bottom:14px;">
                        Mengolah dataset kompleks, melatih model machine learning prediktif, serta menerjemahkan metrik menjadi insight tajam.
                    </div>
                    <div>
                        <span class="rect-tag">Machine Learning</span>
                        <span class="rect-tag">Python</span>
                        <span class="rect-tag">Data / ML Engineer</span>
                    </div>
                </div>
            </div>

            <div class="role-photo-card sr-right">
                <div class="role-photo-bg" style="background-image:linear-gradient(180deg, rgba(10,8,7,.15) 0%, rgba(10,8,7,.94) 85%), url('{BG_PHOTOS['Tim Saya']}');"></div>
                <div class="role-photo-content">
                    <div style="font-size:10.5px;font-weight:700;letter-spacing:.14em;color:var(--brown-light);margin-bottom:6px;">PRODUCT, UI/UX &amp; BUSINESS</div>
                    <div style="font-size:22px;font-weight:800;color:#fff;margin-bottom:8px;letter-spacing:-0.02em;">Design &amp; Deal-Making</div>
                    <div style="font-size:13px;color:var(--muted);line-height:1.55;margin-bottom:14px;">
                        Merancang pengalaman pengguna yang intuitif, menyusun proyeksi finansial, dan memukau dewan juri saat sesi pitching.
                    </div>
                    <div>
                        <span class="rect-tag">UI/UX Design</span>
                        <span class="rect-tag">Business Analysis</span>
                        <span class="rect-tag">Pitching</span>
                    </div>
                </div>
            </div>
        </div>
    """)

    # --- SECTION 4: ALUR KERJA 4 LANGKAH & KOMPETISI TARGET ---
    html("""
        <div class="sec-head sr-up">
            <div class="sec-eyebrow">ALUR KOLABORASI</div>
            <div class="sec-title">Dari profil menuju podium.</div>
            <div class="sec-desc">
                Empat tahapan terstruktur untuk membantu kamu membangun tim impian tanpa membuang waktu mencari secara manual.
            </div>
        </div>

        <div class="workflow-grid">
            <div class="workflow-step sr-left">
                <div style="font-size:12px;font-weight:800;color:var(--brown-light);margin-bottom:10px;">LANGKAH 01</div>
                <div style="font-size:16.5px;font-weight:800;color:#fff;margin-bottom:6px;">Bangun Profil &amp; Skill</div>
                <div style="font-size:12.5px;color:var(--muted);line-height:1.55;">
                    Daftarkan akun, pilih peran utama, keahlian, tingkat kemahiran, jadwal luang, serta tautan portofolio GitHub atau LinkedIn.
                </div>
            </div>
            <div class="workflow-step sr-up">
                <div style="font-size:12px;font-weight:800;color:var(--brown-light);margin-bottom:10px;">LANGKAH 02</div>
                <div style="font-size:16.5px;font-weight:800;color:#fff;margin-bottom:6px;">Pilih Target Kompetisi</div>
                <div style="font-size:12.5px;color:var(--muted);line-height:1.55;">
                    Telusuri katalog lomba aktif berdasarkan kategori bidang, batas waktu pendaftaran, kapasitas tim, dan daftar peran yang dicari.
                </div>
            </div>
            <div class="workflow-step sr-up">
                <div style="font-size:12px;font-weight:800;color:var(--brown-light);margin-bottom:10px;">LANGKAH 03</div>
                <div style="font-size:16.5px;font-weight:800;color:#fff;margin-bottom:6px;">Analisis Peringkat Rekan</div>
                <div style="font-size:12.5px;color:var(--muted);line-height:1.55;">
                    Dapatkan daftar rekomendasi kandidat yang telah diurutkan otomatis berdasarkan skor kecocokan tertinggi untuk lomba pilihanmu.
                </div>
            </div>
            <div class="workflow-step sr-right">
                <div style="font-size:12px;font-weight:800;color:var(--brown-light);margin-bottom:10px;">LANGKAH 04</div>
                <div style="font-size:16.5px;font-weight:800;color:#fff;margin-bottom:6px;">Bentuk &amp; Gabung Tim</div>
                <div style="font-size:12.5px;color:var(--muted);line-height:1.55;">
                    Buka rekrutmen tim barumu sendiri atau langsung bergabung ke tim terbuka dan hubungi rekan lewat tautan WhatsApp/LinkedIn.
                </div>
            </div>
        </div>

        <div class="arena-strip sr-scale">
            <div>
                <div style="font-size:10.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--brown-light);margin-bottom:4px;">DIREKTORI AJANG KOMPETISI MAHASISWA</div>
                <div style="font-size:18px;font-weight:800;color:#fff;">Siap digunakan untuk berbagai kompetisi tingkat nasional.</div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">
                <span class="rect-tag">GEMASTIK</span>
                <span class="rect-tag">COMPFEST UI</span>
                <span class="rect-tag">Arkavidia ITB</span>
                <span class="rect-tag">Find IT! UGM</span>
                <span class="rect-tag">National Business Case</span>
                <span class="rect-tag">ICPC Regional</span>
            </div>
        </div>
    """)

    # --- SECTION 5: BOTTOM CTA & OFFICIAL FOOTER ---
    html("""
        <div class="sec-head sr-up" style="margin-top:90px;margin-bottom:24px;">
            <div class="sec-eyebrow">MULAI KOLABORASI SEKARANG</div>
            <div class="sec-title" style="font-size:clamp(26px, 3.2vw, 40px);">Siap menemukan rekan tim terbaikmu?</div>
        </div>
    """)

    _, b_bot_l, b_bot_r, _ = st.columns([1.3, 0.7, 0.7, 1.3], gap="small")
    with b_bot_l:
        if st.button("Masuk ke Akun", key="footer_login", width="stretch", type="primary"):
            set_view("login")
    with b_bot_r:
        if st.button("Daftar Akun Baru", key="footer_signup", width="stretch", type="secondary"):
            set_view("signup")

    html("""
        <div class="landing-footer">
            <div>
                <b style="color:#fff;">Cari Teman Lomba</b> &nbsp;·&nbsp; Tugas Akhir DDP 1 (G) Fasilkom Universitas Indonesia
            </div>
            <div>
                Kelompok 17: Haris Zidan &nbsp;·&nbsp; Farraj Bagas Alamsyah &nbsp;·&nbsp; Muhammad Nur Ataya
            </div>
        </div>
    """)

# ==============================================================================
# STAGE 2A: DEDICATED LOG IN PAGE
# ==============================================================================
elif curr_view == "login":
    _, col_card, _ = st.columns([0.9, 1.2, 0.9])
    with col_card:
        if st.button("← Kembali ke Beranda", type="secondary"):
            set_view("landing")

        with st.form("login_form"):
            html("""
                <div style="margin-bottom:14px;">
                    <div style="font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--brown-light);margin-bottom:4px;">Autentikasi Akun</div>
                    <div style="font-size:26px;font-weight:800;letter-spacing:-0.03em;color:#fff;">Log In</div>
                    <div style="font-size:13px;color:var(--muted);margin-top:4px;">Masuk ke akun kolaborasimu untuk melanjutkan.</div>
                </div>
            """)
            email_in = st.text_input("Email atau Username", placeholder="nama@ui.ac.id")
            pass_in = st.text_input("Kata Sandi", type="password", placeholder="••••••••")

            if st.form_submit_button("Masuk ke Aplikasi", width="stretch", type="primary"):
                if not email_in.strip() or not pass_in.strip():
                    st.error("Masukkan email/username dan kata sandi.")
                else:
                    acc = st.session_state.accounts.get(email_in.strip().lower())
                    if acc and acc["password"] != pass_in:
                        st.error("Kata sandi tidak sesuai.")
                    else:
                        if acc:
                            st.session_state.user_profile["name"] = acc["name"]
                            st.session_state.user_profile["campus"] = acc["campus"]
                        elif not st.session_state.user_profile["name"]:
                            st.session_state.user_profile["name"] = email_in.split("@")[0].replace(".", " ").title()
                        set_view("app")

        if st.button("Belum punya akun? Sign Up →", width="stretch", type="secondary"):
            set_view("signup")

# ==============================================================================
# STAGE 2B: DEDICATED SIGN UP PAGE
# ==============================================================================
elif curr_view == "signup":
    _, col_card, _ = st.columns([0.85, 1.3, 0.85])
    with col_card:
        if st.button("← Kembali ke Beranda", type="secondary"):
            set_view("landing")

        with st.form("signup_form"):
            html("""
                <div style="margin-bottom:14px;">
                    <div style="font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--brown-light);margin-bottom:4px;">Registrasi Peserta</div>
                    <div style="font-size:26px;font-weight:800;letter-spacing:-0.03em;color:#fff;">Sign Up</div>
                    <div style="font-size:13px;color:var(--muted);margin-top:4px;">Buat akun baru untuk mulai mencari rekan tim lomba.</div>
                </div>
            """)
            reg_name = st.text_input("Nama Lengkap *", placeholder="Farraj Bagas")
            reg_campus = st.text_input("Universitas / Institusi *", placeholder="Universitas Indonesia")
            reg_email = st.text_input("Email Kampus / Username *", placeholder="farraj.bagas@ui.ac.id")
            reg_pass = st.text_input("Buat Kata Sandi *", type="password", placeholder="Minimal 6 karakter")

            if st.form_submit_button("Buat Akun & Masuk", width="stretch", type="primary"):
                if not reg_name.strip() or not reg_email.strip() or not reg_pass.strip():
                    st.error("Nama lengkap, email, dan kata sandi wajib diisi.")
                else:
                    st.session_state.accounts[reg_email.strip().lower()] = {
                        "name": reg_name.strip(),
                        "campus": reg_campus.strip(),
                        "password": reg_pass,
                    }
                    st.session_state.user_profile["name"] = reg_name.strip()
                    st.session_state.user_profile["campus"] = reg_campus.strip()
                    set_view("app")

        if st.button("Sudah punya akun? Log In →", width="stretch", type="secondary"):
            set_view("login")

# ==============================================================================
# STAGE 3: MAIN WEBSITE
# ==============================================================================
else:
    prof = st.session_state.user_profile
    page = curr_page
    st.session_state.active_page = page

    with st.sidebar:
        u_label = esc(prof["name"] or "Mahasiswa")
        u_camp = esc(prof["campus"] or "Fasilkom UI")
        html(f"""
            <div style="display:flex;align-items:center;gap:11px;padding-bottom:14px;margin-bottom:14px;border-bottom:1px solid var(--border);">
                <div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#9C6B43,#6F4E37);color:#FFFFFF;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:12px;letter-spacing:-0.04em;border:1px solid var(--brown-light);">CT</div>
                <div style="min-width:0;">
                    <div style="font-size:13px;font-weight:800;letter-spacing:-0.02em;color:#fff;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">CARI TEMAN LOMBA</div>
                    <div style="font-size:11px;color:var(--brown-light);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{u_label} · {u_camp}</div>
                </div>
            </div>
            <div style="font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:8px;padding-left:4px;">Navigasi Halaman</div>
        """)
        for p_name in PAGES:
            if st.button(p_name, key=f"dock_{p_name}", width="stretch", type="primary" if page == p_name else "secondary"):
                st.session_state.active_page = p_name
                st.rerun()

        html('<div style="height:1px;background:var(--border);margin:14px 0;"></div>')
        if st.button("Keluar dari Akun", key="dock_logout", width="stretch", type="secondary"):
            set_view("landing")

    # --------------------------------------------------------------------------
    # HALAMAN 1: PROFIL
    # --------------------------------------------------------------------------
    if page == "Profil":
        status_label = "Profil Aktif" if (prof["name"] and prof["skills"]) else "Belum Lengkap"
        html(f"""
            <div class="catalog-header">
                <div>
                    <div style="font-size:28px;font-weight:800;letter-spacing:-0.03em;color:#fff;line-height:1.1;">Profil Kolaborator</div>
                    <div style="font-size:13.5px;color:var(--muted);margin-top:6px;">Atur data akademik, peran utama, dan keahlian untuk pencocokan rekan tim.</div>
                </div>
                <div style="font-size:13px;font-weight:700;color:var(--brown-light);background:var(--card);border:1px solid var(--border);padding:8px 16px;border-radius:8px;">
                    {status_label}
                </div>
            </div>
        """)

        with st.form("profile_form"):
            st.markdown("#### Informasi Akademik & Keahlian")
            col_l, col_r = st.columns(2, gap="medium")
            with col_l:
                name = st.text_input("Nama Lengkap *", value=prof["name"], placeholder="Farraj Bagas")
                curr_role = prof.get("role", ROLE_OPTS[0])
                role = st.selectbox("Peran Utama dalam Tim *", ROLE_OPTS, index=ROLE_OPTS.index(curr_role) if curr_role in ROLE_OPTS else 0)
                campus = st.text_input("Universitas / Institusi", value=prof["campus"], placeholder="Universitas Indonesia")
                c_maj, c_yr = st.columns([1.4, 0.8], gap="small")
                major = c_maj.text_input("Program Studi", value=prof["major"], placeholder="Ilmu Komputer")
                year = c_yr.number_input("Angkatan", 2015, 2030, prof["year"])
            with col_r:
                skills = st.multiselect("Keahlian Utama *", SKILL_OPTS, default=prof["skills"])
                curr_lvl = prof.get("level", "Menengah")
                level = st.selectbox("Tingkat Pengalaman", LEVEL_OPTS, index=LEVEL_OPTS.index(curr_lvl) if curr_lvl in LEVEL_OPTS else 1)
                avail = st.text_input("Ketersediaan Waktu", value=prof["availability"], placeholder="Weekday malam & weekend penuh")
                c_wa, c_pf = st.columns(2, gap="small")
                contact = c_wa.text_input("Kontak WhatsApp / LinkedIn", value=prof.get("contact", ""), placeholder="wa.me/62812...")
                portfolio = c_pf.text_input("Portofolio / GitHub", value=prof["portfolio"], placeholder="github.com/username")

            if st.form_submit_button("Simpan Profil", width="stretch", type="primary"):
                if not name.strip() or not skills:
                    st.error("Nama lengkap dan minimal 1 keahlian wajib diisi.")
                else:
                    st.session_state.user_profile = {
                        "name": name.strip(), "major": major.strip(), "year": year, "campus": campus.strip(),
                        "role": role, "skills": skills, "level": level,
                        "availability": avail.strip(), "contact": contact.strip(), "portfolio": portfolio.strip()
                    }
                    st.toast("Profil berhasil disimpan.")
                    st.rerun()

        if prof["name"] and prof["skills"]:
            st.write("")
            links_list = []
            if prof.get("contact"):
                links_list.append(f'<a class="action-link" style="height:34px !important;font-size:12px !important;" href="{esc(safe_url(prof["contact"]))}" target="_blank">WhatsApp / LinkedIn ↗</a>')
            if prof.get("portfolio"):
                links_list.append(f'<a class="action-link secondary" style="height:34px !important;font-size:12px !important;" href="{esc(safe_url(prof["portfolio"]))}" target="_blank">Portofolio ↗</a>')
            links_html = f'<div style="display:flex;gap:8px;">{"".join(links_list)}</div>' if links_list else ""

            html(f"""
                <div class="arch-card hoverable">
                    <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:12px;margin-bottom:12px;border-bottom:1px solid var(--border);flex-wrap:wrap;gap:10px;">
                        <span class="rect-tag" style="margin:0">{esc(prof.get('role', 'Kolaborator'))}</span>
                        <span style="font-size:12px;color:var(--muted);font-weight:600;">Level: <b style="color:#fff">{esc(prof['level'])}</b> &nbsp;|&nbsp; Jadwal: <b style="color:#fff">{esc(prof['availability'] or 'Fleksibel')}</b></span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;">
                        <div>
                            <div style="font-size:20px;font-weight:800;letter-spacing:-0.025em;color:#fff;margin-bottom:4px;">{esc(prof['name'])}</div>
                            <div style="font-size:12.5px;color:var(--muted);margin-bottom:12px;">{esc(prof['major'] or 'Program Studi')} · {esc(prof['campus'] or 'Universitas')} ({prof['year']})</div>
                            <div>{badges(prof['skills'], muted=True)}</div>
                        </div>
                        {links_html}
                    </div>
                </div>
            """)

    # --------------------------------------------------------------------------
    # HALAMAN 2: KOMPETISI
    # --------------------------------------------------------------------------
    elif page == "Kompetisi":
        comps = st.session_state.competitions
        html(f"""
            <div class="catalog-header">
                <div>
                    <div style="font-size:28px;font-weight:800;letter-spacing:-0.03em;color:#fff;line-height:1.1;">Katalog Kompetisi</div>
                    <div style="font-size:13.5px;color:var(--muted);margin-top:6px;">Daftar kompetisi teknologi, data science, desain, dan bisnis beserta kebutuhan peran tim.</div>
                </div>
                <div style="font-size:13px;font-weight:700;color:var(--brown-light);background:var(--card);border:1px solid var(--border);padding:8px 16px;border-radius:8px;">
                    {len(comps)} Kompetisi Terdaftar
                </div>
            </div>
        """)

        c1, c2, c3 = st.columns([2.2, 1, 1], gap="small")
        q = c1.text_input("Cari", placeholder="Cari nama kompetisi, penyelenggara, atau peran...", label_visibility="collapsed").strip().lower()
        cat_f = c2.selectbox("Kategori", ["Semua Kategori", *CAT_OPTS], label_visibility="collapsed")
        sort_f = c3.selectbox("Urutan", ["Deadline Terdekat", "Nama (A-Z)", "Terbaru"], label_visibility="collapsed")

        with st.expander("+ Daftarkan Kompetisi Baru"):
            with st.form("add_comp", clear_on_submit=True):
                f1, f2, f3 = st.columns([1.3, 1, 0.8], gap="small")
                title = f1.text_input("Nama Kompetisi *", placeholder="Gemastik XIX 2026")
                cat = f2.selectbox("Kategori Bidang", CAT_OPTS)
                team_size = f3.number_input("Ukuran Tim (Orang)", 1, 10, 3)

                f4, f5 = st.columns(2, gap="small")
                org = f4.text_input("Penyelenggara", placeholder="Puspresnas / Kemendikbud")
                ddl = f5.date_input("Batas Pendaftaran")

                f6, f7 = st.columns(2, gap="small")
                roles_req = f6.multiselect("Peran yang Dibutuhkan (Roles Needed)", ROLE_OPTS, default=[ROLE_OPTS[0], ROLE_OPTS[3]])
                skills_req = f7.multiselect("Keahlian yang Dibutuhkan", SKILL_OPTS)

                if st.form_submit_button("Simpan Kompetisi", width="stretch", type="primary"):
                    if title.strip():
                        comps.append({
                            "title": title.strip(), "category": cat, "organizer": org.strip() or "-",
                            "deadline": str(ddl), "team_size": team_size,
                            "roles_needed": roles_req, "required_skills": skills_req
                        })
                        st.toast("Kompetisi berhasil ditambahkan.")
                        st.rerun()
                    else:
                        st.warning("Nama kompetisi wajib diisi.")

        filtered = [
            c for c in comps
            if (cat_f == "Semua Kategori" or c["category"] == cat_f)
            and (not q or q in c["title"].lower() or q in c["organizer"].lower() or q in " ".join(c.get("roles_needed", [])).lower())
        ]
        if sort_f == "Deadline Terdekat":
            filtered.sort(key=lambda x: x["deadline"])
        elif sort_f == "Nama (A-Z)":
            filtered.sort(key=lambda x: x["title"].lower())
        else:
            filtered = list(reversed(filtered))

        if not filtered:
            html("""
                <div class="arch-card" style="text-align:center;padding:48px 28px !important;margin-top:8px;">
                    <div style="font-size:18px;font-weight:800;letter-spacing:-0.02em;color:#fff;margin-bottom:6px;">Belum Ada Kompetisi Terdaftar</div>
                    <div style="font-size:13.5px;color:var(--muted);max-width:46ch;margin:0 auto;line-height:1.55;">
                        Buka panel <b>+ Daftarkan Kompetisi Baru</b> di atas untuk menambahkan lomba beserta ukuran tim dan peran yang dibutuhkan.
                    </div>
                </div>
            """)
        else:
            cols = st.columns(2, gap="medium")
            for i, comp in enumerate(filtered):
                t_size = comp.get("team_size", 3)
                r_needed = comp.get("roles_needed", [])
                roles_markup = badges(r_needed, muted=True) if r_needed else '<span class="rect-tag subtle">Semua Peran</span>'
                with cols[i % 2]:
                    html(f"""
                        <div class="arch-card hoverable" style="margin-bottom:10px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:12px;margin-bottom:12px;border-bottom:1px solid var(--border);">
                                <span class="rect-tag" style="margin:0">{esc(comp['category'])}</span>
                                <span style="font-size:12px;color:var(--muted);font-weight:600;">Tim: <b style="color:#fff">{t_size} Orang</b> &nbsp;|&nbsp; Tenggat: <b style="color:#fff">{esc(comp['deadline'])}</b></span>
                            </div>
                            <div style="font-size:20px;font-weight:800;letter-spacing:-0.025em;color:#fff;margin-bottom:4px;">{esc(comp['title'])}</div>
                            <div style="font-size:12.5px;color:var(--muted);margin-bottom:14px;">Penyelenggara: {esc(comp['organizer'])}</div>
                            <div style="font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--brown-light);margin-bottom:6px;">Peran Dibutuhkan</div>
                            <div>{roles_markup}</div>
                        </div>
                    """)
                    if st.button(f"Cari Rekan untuk {comp['title']} →", key=f"match_comp_{i}", width="stretch", type="secondary"):
                        st.session_state.selected_comp = comp["title"]
                        st.session_state.active_page = "Rekomendasi"
                        st.rerun()

    # --------------------------------------------------------------------------
    # HALAMAN 3: REKOMENDASI
    # --------------------------------------------------------------------------
    elif page == "Rekomendasi":
        candidates = st.session_state.candidates
        comps = st.session_state.competitions
        comp_titles = ["Semua Kompetisi", *[c["title"] for c in comps]]
        if st.session_state.selected_comp not in comp_titles:
            st.session_state.selected_comp = "Semua Kompetisi"

        html(f"""
            <div class="catalog-header">
                <div>
                    <div style="font-size:28px;font-weight:800;letter-spacing:-0.03em;color:#fff;line-height:1.1;">Rekomendasi Rekan Tim</div>
                    <div style="font-size:13.5px;color:var(--muted);margin-top:6px;">Daftar kandidat rekan kolaborasi berdasarkan kesesuaian keahlian, peran, dan ketersediaan jadwal.</div>
                </div>
                <div style="font-size:13px;font-weight:700;color:var(--brown-light);background:var(--card);border:1px solid var(--border);padding:8px 16px;border-radius:8px;">
                    {len(candidates)} Kandidat Tersedia
                </div>
            </div>
        """)

        c1, c2, c3 = st.columns([2.2, 1, 1], gap="small")
        q_cand = c1.text_input("Cari Kandidat", placeholder="Cari nama, universitas, atau keahlian kandidat...", label_visibility="collapsed").strip().lower()
        sel_title = c2.selectbox("Target Kompetisi", comp_titles, index=comp_titles.index(st.session_state.selected_comp), label_visibility="collapsed")
        st.session_state.selected_comp = sel_title
        role_filter = c3.selectbox("Filter Peran", ["Semua Peran", *ROLE_OPTS], label_visibility="collapsed")

        if not prof["name"] or not prof["skills"]:
            html("""
                <div class="arch-card" style="text-align:center;padding:48px 28px !important;margin-top:8px;">
                    <div style="font-size:18px;font-weight:800;letter-spacing:-0.02em;color:#fff;margin-bottom:6px;">Profil & Keahlian Belum Lengkap</div>
                    <div style="font-size:13.5px;color:var(--muted);max-width:46ch;margin:0 auto;line-height:1.55;">
                        Lengkapi nama dan minimal 1 keahlian pada halaman <b>Profil</b> terlebih dahulu untuk melihat peringkat kecocokan kandidat.
                    </div>
                </div>
            """)
        else:
            active_comp = next((c for c in comps if c["title"] == sel_title), None)
            scored_list = []
            for c in candidates:
                if role_filter != "Semua Peran" and c.get("role") and c.get("role") != role_filter:
                    continue
                haystack = f"{c['name']} {c['campus']} {c['major']} {' '.join(c['skills'])}".lower()
                if q_cand and q_cand not in haystack:
                    continue
                score = compute_match_score(prof, c, active_comp)
                scored_list.append((c, score))
            scored_list.sort(key=lambda item: item[1], reverse=True)

            if not scored_list:
                html("""
                    <div class="arch-card" style="text-align:center;padding:48px 28px !important;margin-top:8px;">
                        <div style="font-size:18px;font-weight:800;letter-spacing:-0.02em;color:#fff;margin-bottom:6px;">Belum Ada Kandidat yang Sesuai</div>
                        <div style="font-size:13.5px;color:var(--muted);max-width:46ch;margin:0 auto;line-height:1.55;">
                            Daftar rekomendasi rekan tim akan otomatis tampil di sini saat data peserta telah tersedia.
                        </div>
                    </div>
                """)
            else:
                cols = st.columns(2, gap="medium")
                for i, (c, score) in enumerate(scored_list):
                    avail_txt = c.get("availability") or c.get("avail", "Fleksibel")
                    c_role = c.get("role", "Kolaborator")
                    contact_btn = f'<a class="action-link secondary" style="width:100%;margin-top:12px;" href="{esc(safe_url(c["contact"]))}" target="_blank">Hubungi {esc(c["name"].split()[0])} ↗</a>' if c.get("contact") else ""
                    with cols[i % 2]:
                        html(f"""
                            <div class="arch-card hoverable" style="margin-bottom:12px;">
                                <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:12px;margin-bottom:12px;border-bottom:1px solid var(--border);">
                                    <span class="rect-tag" style="margin:0">{esc(c_role)}</span>
                                    <span style="font-size:12.5px;color:var(--muted);font-weight:600;">Kecocokan: <b style="color:var(--brown-light)">{score}%</b></span>
                                </div>
                                <div style="font-size:20px;font-weight:800;letter-spacing:-0.025em;color:#fff;margin-bottom:4px;">{esc(c['name'])}</div>
                                <div style="font-size:12.5px;color:var(--muted);margin-bottom:14px;">{esc(c['major'])} · {esc(c['campus'])} &nbsp;|&nbsp; Jadwal: {esc(avail_txt)}</div>
                                <div style="font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--brown-light);margin-bottom:6px;">Keahlian</div>
                                <div>{badges(c['skills'], muted=True)}</div>
                                {contact_btn}
                            </div>
                        """)

    # --------------------------------------------------------------------------
    # HALAMAN 4: TIM SAYA
    # --------------------------------------------------------------------------
    else:
        teams = st.session_state.teams
        comps = st.session_state.competitions
        comp_choices = [c["title"] for c in comps] or ["Kompetisi Umum"]

        html(f"""
            <div class="catalog-header">
                <div>
                    <div style="font-size:28px;font-weight:800;letter-spacing:-0.03em;color:#fff;line-height:1.1;">Rekrutmen & Manajemen Tim</div>
                    <div style="font-size:13.5px;color:var(--muted);margin-top:6px;">Bentuk tim baru untuk kompetisi incaranmu atau bergabung ke tim yang sedang membuka posisi.</div>
                </div>
                <div style="font-size:13px;font-weight:700;color:var(--brown-light);background:var(--card);border:1px solid var(--border);padding:8px 16px;border-radius:8px;">
                    {len(teams)} Tim Terbuka
                </div>
            </div>
        """)

        with st.form("create_team_form", clear_on_submit=True):
            st.markdown("#### Bentuk Tim Baru")
            tc1, tc2 = st.columns(2, gap="medium")
            with tc1:
                t_name = st.text_input("Nama Tim *", placeholder="Contoh: Garuda UI Team")
                t_comp = st.selectbox("Target Kompetisi", comp_choices)
                t_max = st.number_input("Kapasitas Maksimal Anggota", 2, 6, 3)
            with tc2:
                t_roles = st.multiselect("Peran Anggota yang Dicari", ROLE_OPTS, default=[ROLE_OPTS[3], ROLE_OPTS[6]])
                t_contact = st.text_input("Tautan Grup WhatsApp / Kontak Tim", value=prof.get("contact", ""), placeholder="wa.me/628...")

            if st.form_submit_button("Bentuk Tim Sekarang", width="stretch", type="primary"):
                if not t_name.strip():
                    st.error("Nama tim wajib diisi.")
                else:
                    leader = prof["name"] or "Ketua Tim"
                    teams.append({
                        "name": t_name.strip(),
                        "competition": t_comp,
                        "max_size": t_max,
                        "members": [leader],
                        "roles_needed": t_roles,
                        "contact": t_contact.strip(),
                    })
                    st.toast("Tim berhasil dibentuk.")
                    st.rerun()

        st.write("")
        if not teams:
            html("""
                <div class="arch-card" style="text-align:center;padding:48px 28px !important;">
                    <div style="font-size:18px;font-weight:800;letter-spacing:-0.02em;color:#fff;margin-bottom:6px;">Belum Ada Tim yang Terbentuk</div>
                    <div style="font-size:13.5px;color:var(--muted);max-width:46ch;margin:0 auto;line-height:1.55;">
                        Isi formulir <b>Bentuk Tim Baru</b> di atas untuk membuka rekrutmen anggota tim pertamamu.
                    </div>
                </div>
            """)
        else:
            cols = st.columns(2, gap="medium")
            for idx, tm in enumerate(teams):
                cur_members = tm["members"]
                is_full = len(cur_members) >= tm["max_size"]
                user_label = prof["name"] or "Anda"
                already_in = user_label in cur_members
                roles_html = badges(tm["roles_needed"], muted=True) if tm["roles_needed"] else '<span class="rect-tag subtle">Terbuka untuk semua peran</span>'

                with cols[idx % 2]:
                    html(f"""
                        <div class="arch-card hoverable" style="margin-bottom:10px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:10px;margin-bottom:10px;border-bottom:1px solid var(--border);">
                                <span class="rect-tag" style="margin:0">{esc(tm['competition'])}</span>
                                <span style="font-size:12px;font-weight:700;color:var(--brown-light);">{len(cur_members)} / {tm['max_size']} Anggota</span>
                            </div>
                            <div style="font-size:20px;font-weight:800;letter-spacing:-0.025em;color:#fff;margin-bottom:6px;">{esc(tm['name'])}</div>
                            <div style="font-size:12.5px;color:var(--muted);margin-bottom:12px;">Anggota Saat Ini: <b style="color:#fff">{esc(', '.join(cur_members))}</b></div>
                            <div style="font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--brown-light);margin-bottom:6px;">Mencari Peran</div>
                            <div>{roles_html}</div>
                        </div>
                    """)
                    b_col1, b_col2 = st.columns(2, gap="small")
                    with b_col1:
                        if not already_in and not is_full:
                            if st.button(f"Gabung ke {tm['name']}", key=f"join_tm_{idx}", width="stretch", type="primary"):
                                tm["members"].append(user_label)
                                st.toast(f"Berhasil bergabung ke {tm['name']}.")
                                st.rerun()
                        else:
                            status_lbl = "Sudah Bergabung" if already_in else "Tim Penuh"
                            st.button(status_lbl, key=f"join_tm_{idx}", width="stretch", disabled=True)
                    with b_col2:
                        if tm.get("contact"):
                            html(f'<a class="action-link secondary" style="width:100%" href="{esc(safe_url(tm["contact"]))}" target="_blank">Hubungi Tim ↗</a>')
