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
    "auth": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=2000&q=85",
    "Profil": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1800&q=80",
    "Kompetisi": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1800&q=80",
    "Rekomendasi": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=1800&q=80",
    "Tim Saya": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1800&q=80",
}


# 2. Helper Functions (PEP 8 snake_case + one-line docstring sesuai README.md)
def html(markup: str) -> None:
    """Render compact HTML string inside full-width Streamlit markdown container."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()), unsafe_allow_html=True)


def set_view(target: str) -> None:
    """Switch top-level application view and trigger rerun."""
    st.session_state.view = target
    st.rerun()


def avatar(name: str, size: int = 44) -> str:
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


def compute_match_breakdown(user: dict, cand: dict, comp: dict | None = None) -> dict:
    """Compute matching score using README formula: 0.5*skill + 0.3*role + 0.2*time."""
    if "match" in cand and not comp:
        total = int(cand["match"])
        return {"total": total, "skill": total, "role": total, "time": total}

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
    return {
        "total": max(1, min(99, final)),
        "skill": round(skill_score * 100),
        "role": round(role_score * 100),
        "time": round(time_score * 100),
    }


def page_hero(eyebrow: str, title: str, subtitle: str, photo_url: str, meta_label: str = "", meta_val: str = "") -> None:
    """Render full-width architectural hero banner aligned flush with page content."""
    meta_html = f"""
        <div class="hero-stat-box">
            <div class="hero-stat-lbl">{esc(meta_label)}</div>
            <div class="hero-stat-val">{esc(meta_val)}</div>
        </div>
    """ if meta_val else ""
    html(f"""
        <div class="arch-hero" style="background-image: linear-gradient(90deg, rgba(10,9,8,.94) 0%, rgba(12,10,9,.78) 55%, rgba(14,11,9,.48) 100%), url('{photo_url}');">
            <div class="hero-inner">
                <div>
                    <div class="hero-eyebrow">{esc(eyebrow)}</div>
                    <div class="hero-h1">{esc(title)}</div>
                    <div class="hero-p">{esc(subtitle)}</div>
                </div>
                {meta_html}
            </div>
        </div>
    """)


# 3. Architectural CSS + Warm Brown Palette + Visible Mac Dock Handle
curr_view = st.session_state.view
is_app = curr_view == "app"

bg_css = f"""
.stApp {{
    background-image: radial-gradient(circle at 50% 32%, rgba(12, 9, 7, .50) 0%, rgba(10, 8, 7, .90) 100%), url('{BG_PHOTOS["auth"]}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
""" if not is_app else """
.stApp { background: #0A0908; }
"""

sidebar_dock_css = """
/* Mac-Style Auto-Pop-Up Floating Left Dock dengan Penanda Tab "MENU" yang Jelas */
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
    background: rgba(18, 15, 13, 0.94) !important;
    backdrop-filter: blur(32px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(32px) saturate(180%) !important;
    border: 1px solid rgba(196, 154, 108, 0.32) !important;
    border-left: none !important;
    border-radius: 0 18px 18px 0 !important;
    box-shadow: 0 28px 70px rgba(0, 0, 0, 0.9) !important;
    z-index: 999999 !important;
    opacity: 1 !important;
    transition: transform 0.30s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.25s ease !important;
    overflow: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 20px 18px 22px !important;
    overflow: visible !important;
}
/* Area sensor hover ekstra di pinggir kiri layar */
section[data-testid="stSidebar"]::before {
    content: "";
    position: absolute;
    top: -25vh;
    bottom: -25vh;
    right: -44px;
    width: 52px;
    background: transparent;
}
/* PENANDA DOCK (Tab "☰ MENU" berwarna Coklat/Bronze di tepi kiri layar) */
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
    background: linear-gradient(180deg, #8B5E3C, #6F4E37);
    border: 1px solid rgba(212, 163, 115, 0.55);
    border-left: none;
    padding: 16px 8px;
    border-radius: 0 10px 10px 0;
    box-shadow: 6px 0 22px rgba(0, 0, 0, 0.75);
    cursor: pointer;
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
/* Efek Magnification ala Mac Dock pada tombol menu di dalam Dock */
section[data-testid="stSidebar"] .stButton > button {
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 0 14px !important;
    height: 42px !important;
    border-radius: 10px !important;
    transition: transform 0.18s cubic-bezier(0.22, 1, 0.36, 1), background 0.16s ease, border-color 0.16s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    transform: scale(1.04) translateX(5px) !important;
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
    --card: #12100E;
    --surface: #171412;
    --surface-2: #211C18;
    --brown: #8B5E3C;
    --brown-dark: #6F4E37;
    --brown-light: #C49A6C;
    --brown-soft: rgba(139, 94, 60, 0.18);
    --border: rgba(212, 163, 115, 0.16);
    --border-strong: rgba(196, 154, 108, 0.42);
    --ink: #F5F2EB;
    --muted: #A89F96;
    --subtle: #736B63;
}}

@keyframes pageFade {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

html, body, .stApp, [data-testid="stMarkdownContainer"], input, textarea, button, label, select, div {{
    font-family: 'Gotham', 'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
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
}}
.block-container {{
    max-width: 1060px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding-top: {'1.8rem' if is_app else '2.5rem'} !important;
    padding-bottom: 3.5rem !important;
    animation: pageFade .22s ease-out;
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

/* GANTI SEMUA WARNA MERAH STREAMLIT (#FF4B4B) JADI COKLAT (ESPRESSO / BRONZE) */
span[data-baseweb="tag"],
[data-baseweb="select"] span[data-baseweb="tag"] {{
    background-color: var(--brown-dark) !important;
    background: var(--brown-dark) !important;
    border: 1px solid var(--brown-light) !important;
    border-radius: 6px !important;
    color: #FDFBF7 !important;
    filter: none !important;
}}
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
[data-testid="stSliderThumbValue"] {{ color: var(--brown-light) !important; }}
[data-baseweb="slider"] div[role="slider"] {{ background-color: var(--brown) !important; border-color: var(--brown-light) !important; }}

/* Architectural Panels & Forms */
.arch-card, [data-testid="stForm"] {{
    width: 100% !important;
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 24px 26px !important;
    box-sizing: border-box !important;
    transition: border-color .16s ease !important;
}}
.arch-card.hoverable:hover {{
    border-color: var(--border-strong) !important;
}}

/* Inputs & Posisi "Press Enter to submit form" Sejajar Tengah dengan Teks */
[data-testid="stTextInputRootElement"],
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="select"] > div,
[data-baseweb="textarea"] {{
    background-color: #171412 !important;
    border: 1px solid var(--border) !important;
    border-top-color: var(--border) !important;
    border-right-color: var(--border) !important;
    border-bottom-color: var(--border) !important;
    border-left-color: var(--border) !important;
    border-radius: 8px !important;
    color: var(--ink) !important;
    box-shadow: none !important;
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
    box-shadow: 0 0 0 1px var(--brown-light) !important;
    background-color: #1E1915 !important;
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
/* Hilangkan teks contoh (placeholder) otomatis saat input diklik/fokus & sembunyikan 'Press Enter' saat masih kosong */
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

/* Professional Buttons (Aksen Coklat Espresso & Bronze) */
.stButton > button, .stFormSubmitButton > button, .action-link {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: -0.01em !important;
    height: 40px !important;
    padding: 0 14px !important;
    white-space: nowrap !important;
    transition: background .14s ease, border-color .14s ease, transform .08s ease !important;
}}
.stButton > button:active, .stFormSubmitButton > button:active, .action-link:active {{
    transform: translateY(1px) scale(0.99) !important;
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
    background: linear-gradient(135deg, #AE7A4E, #8B5E3C) !important;
}}
[data-testid^="stBaseButton-secondary"] {{
    background: rgba(255, 255, 255, 0.05) !important;
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

/* Landing Page Centered (Pakai <div> penuh agar tidak terkena override <p> Streamlit) */
.landing-wrap {{
    width: 100% !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center !important;
    margin: 9vh auto 26px !important;
}}
.landing-eyebrow {{
    width: 100%;
    text-align: center !important;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--brown-light);
    margin-bottom: 18px;
}}
.landing-title {{
    width: 100%;
    text-align: center !important;
    font-size: clamp(40px, 5.5vw, 68px);
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.05;
    color: #FFFFFF !important;
    margin: 0 auto 20px !important;
}}
.landing-sub {{
    width: 100%;
    max-width: 640px !important;
    text-align: center !important;
    font-size: clamp(15px, 1.4vw, 17.5px);
    line-height: 1.6;
    color: rgba(245, 242, 235, 0.82);
    margin: 0 auto 8px !important;
}}
.pillar-card {{
    background: rgba(18, 15, 13, 0.84);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-top: 2px solid var(--brown-light);
    border-radius: 12px;
    padding: 22px 24px;
    height: 100%;
}}

/* Editorial Photographic Hero inside App */
.arch-hero {{
    width: 100%;
    box-sizing: border-box;
    background-size: cover;
    background-position: center;
    border-radius: 12px;
    border: 1px solid var(--border);
    padding: 32px 34px;
    margin: 0 0 20px 0;
}}
.hero-inner {{
    display: flex; align-items: flex-end; justify-content: space-between;
    flex-wrap: wrap; gap: 20px;
}}
.hero-eyebrow {{
    font-size: 10.5px; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--brown-light); margin-bottom: 6px;
}}
.hero-h1 {{
    font-size: clamp(24px, 2.8vw, 34px); font-weight: 800;
    letter-spacing: -0.03em; line-height: 1.1; color: #FFFFFF !important; margin: 0;
}}
.hero-p {{
    font-size: 13.5px; color: rgba(245, 242, 235, 0.80);
    max-width: 56ch; margin: 8px 0 0 !important; line-height: 1.5;
}}
.hero-stat-box {{
    background: rgba(14, 12, 10, 0.82);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-left: 3px solid var(--brown-light);
    padding: 10px 16px; border-radius: 6px; min-width: 145px;
}}
.hero-stat-lbl {{ font-size: 10px; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); font-weight: 600; }}
.hero-stat-val {{ font-size: 15.5px; font-weight: 800; color: var(--brown-light); margin-top: 2px; }}

/* Squared Monogram & Rectangular Tags */
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
}}
.rect-tag.subtle {{
    background: rgba(255, 255, 255, 0.04); border-color: var(--border); color: var(--muted);
}}

/* Full-Width Horizontal Summary Strips */
.exec-strip {{
    width: 100%; box-sizing: border-box;
    display: grid; grid-template-columns: repeat(3, 1fr);
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; margin: 0 0 20px 0; overflow: hidden;
}}
.exec-cell {{
    padding: 18px 22px; border-right: 1px solid var(--border);
}}
.exec-cell:last-child {{ border-right: none; }}
.exec-lbl {{ font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; color: var(--brown-light); }}
.exec-val {{ font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em; margin-top: 4px; }}
.exec-sub {{ font-size: 12px; color: var(--subtle); margin-top: 2px; }}

.bar-track {{ height: 5px; border-radius: 3px; background: rgba(255,255,255,.08); overflow: hidden; margin: 12px 0; }}
.bar-fill {{ display: block; height: 100%; background: linear-gradient(90deg, #8B5E3C, #C49A6C); }}
.score-table {{
    display: grid; grid-template-columns: repeat(3, 1fr);
    border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
    padding: 10px 0; margin: 12px 0; text-align: left;
}}
.score-col {{ border-right: 1px solid var(--border); padding-left: 10px; }}
.score-col:first-child {{ padding-left: 0; }}
.score-col:last-child {{ border-right: none; }}
</style>""")

# ==============================================================================
# STAGE 1: CENTERED LANDING PAGE (100% Center dengan Flex Column + <div>)
# ==============================================================================
if curr_view == "landing":
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
        if st.button("Log In", width="stretch", type="primary"):
            set_view("login")
    with btn_right:
        if st.button("Sign Up", width="stretch", type="secondary"):
            set_view("signup")

    st.markdown("<div style='height:38px'></div>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3, gap="medium")
    with p1:
        html("""
            <div class="pillar-card">
                <div style="font-size:11px;font-weight:700;letter-spacing:.1em;color:var(--brown-light);margin-bottom:4px;">BOBOT 50%</div>
                <div style="font-size:17px;font-weight:800;color:#fff;">Skill Overlap</div>
                <div style="font-size:12.5px;color:var(--muted);margin-top:4px;line-height:1.5;">Kesesuaian keahlian teknis & non-teknis yang dibobotkan menurut level pengalaman.</div>
            </div>
        """)
    with p2:
        html("""
            <div class="pillar-card">
                <div style="font-size:11px;font-weight:700;letter-spacing:.1em;color:var(--brown-light);margin-bottom:4px;">BOBOT 30%</div>
                <div style="font-size:17px;font-weight:800;color:#fff;">Role Fit</div>
                <div style="font-size:12.5px;color:var(--muted);margin-top:4px;line-height:1.5;">Kecocokan peran spesifik yang dibutuhkan tim dalam suatu kategori kompetisi.</div>
            </div>
        """)
    with p3:
        html("""
            <div class="pillar-card">
                <div style="font-size:11px;font-weight:700;letter-spacing:.1em;color:var(--brown-light);margin-bottom:4px;">BOBOT 20%</div>
                <div style="font-size:17px;font-weight:800;color:#fff;">Time Overlap</div>
                <div style="font-size:12.5px;color:var(--muted);margin-top:4px;line-height:1.5;">Irisan ketersediaan jadwal kerja kolaborasi antara kamu dan anggota tim.</div>
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
# STAGE 3: MAIN WEBSITE DENGAN AUTO-POP-UP MAC DOCK DI SISI KIRI
# ==============================================================================
else:
    prof = st.session_state.user_profile
    page = st.session_state.active_page
    if page not in PAGES:
        page = "Profil"
        st.session_state.active_page = "Profil"

    # Auto-Pop-Up Floating Mac Dock di Sisi Kiri Layar (Dengan Tab Penanda "☰ MENU")
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
        fields = ("name", "campus", "major", "role", "skills", "availability", "contact", "portfolio")
        filled = sum(bool(prof.get(k)) for k in fields)
        page_hero(
            "01 / PROFIL KOLABORATOR",
            "Identitas, Peran & Keahlian",
            "Arahkan kursor ke tab MENU di tepi kiri layar untuk berpindah halaman. Lengkapi profilmu di bawah ini.",
            BG_PHOTOS["Profil"],
            "Kelengkapan Data",
            f"{int(filled / len(fields) * 100)}% Terisi",
        )

        skills_html = badges(prof["skills"]) if prof["skills"] else '<span style="font-size:12.5px;color:var(--subtle)">Belum ada keahlian dipilih</span>'
        weight_val = int(LEVEL_WEIGHTS.get(prof["level"], 0.8) * 100)
        links_list = []
        if prof.get("contact"):
            links_list.append(f'<a class="action-link" style="height:34px !important;font-size:12px !important;" href="{esc(safe_url(prof["contact"]))}" target="_blank">WhatsApp / LinkedIn ↗</a>')
        if prof.get("portfolio"):
            links_list.append(f'<a class="action-link secondary" style="height:34px !important;font-size:12px !important;" href="{esc(safe_url(prof["portfolio"]))}" target="_blank">Portofolio / GitHub ↗</a>')
        links_html = f'<div style="display:flex;gap:10px;margin-top:14px;">{"".join(links_list)}</div>' if links_list else ""

        html(f"""
            <div class="arch-card" style="margin-bottom:20px;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;padding-bottom:18px;margin-bottom:18px;border-bottom:1px solid var(--border);">
                    <div style="display:flex;align-items:center;gap:16px;">
                        {avatar(prof['name'] or '?', 52)}
                        <div>
                            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                                <span style="font-size:21px;font-weight:800;letter-spacing:-0.025em;color:#fff;">{esc(prof['name'] or 'Nama Belum Diisi')}</span>
                                <span class="rect-tag" style="margin:0">{esc(prof.get('role', 'Kolaborator'))}</span>
                            </div>
                            <div style="font-size:13px;color:var(--muted);margin-top:4px;">
                                {esc(prof['major'] or 'Program Studi')} &nbsp;·&nbsp; {esc(prof['campus'] or 'Universitas')} &nbsp;·&nbsp; Angkatan {prof['year']}
                            </div>
                        </div>
                    </div>
                    <div style="display:flex;gap:28px;flex-wrap:wrap;">
                        <div>
                            <div style="font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--brown-light);">Tingkat Pengalaman</div>
                            <div style="font-size:14.5px;font-weight:700;color:#fff;margin-top:3px;">{esc(prof['level'])} ({weight_val}% bobot)</div>
                        </div>
                        <div>
                            <div style="font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--brown-light);">Ketersediaan Waktu</div>
                            <div style="font-size:14.5px;font-weight:700;color:#fff;margin-top:3px;">{esc(prof['availability'] or 'Fleksibel')}</div>
                        </div>
                    </div>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                    <div>
                        <div style="font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--brown-light);margin-bottom:8px;">
                            Keahlian Utama ({len(prof['skills'])})
                        </div>
                        <div>{skills_html}</div>
                    </div>
                    {links_html}
                </div>
            </div>
        """)

        with st.form("profile_form"):
            st.markdown("#### Perbarui Data Akademik, Peran & Keahlian")
            col_l, col_r = st.columns(2, gap="medium")
            with col_l:
                name = st.text_input("Nama Lengkap *", value=prof["name"], placeholder="Farraj Bagas")
                curr_role = prof.get("role", ROLE_OPTS[0])
                role = st.selectbox("Peran Utama dalam Tim (Role) *", ROLE_OPTS, index=ROLE_OPTS.index(curr_role) if curr_role in ROLE_OPTS else 0)
                campus = st.text_input("Universitas / Institusi", value=prof["campus"], placeholder="Universitas Indonesia")
                c_maj, c_yr = st.columns([1.4, 0.8], gap="small")
                major = c_maj.text_input("Program Studi", value=prof["major"], placeholder="Ilmu Komputer")
                year = c_yr.number_input("Angkatan", 2015, 2030, prof["year"])
            with col_r:
                skills = st.multiselect("Keahlian Utama (Skills) *", SKILL_OPTS, default=prof["skills"])
                curr_lvl = prof.get("level", "Menengah")
                level = st.selectbox("Tingkat Pengalaman (Bobot Skill)", LEVEL_OPTS, index=LEVEL_OPTS.index(curr_lvl) if curr_lvl in LEVEL_OPTS else 1)
                avail = st.text_input("Ketersediaan Waktu (Availability)", value=prof["availability"], placeholder="Weekday malam & weekend penuh")
                c_wa, c_pf = st.columns(2, gap="small")
                contact = c_wa.text_input("Kontak WhatsApp / LinkedIn", value=prof.get("contact", ""), placeholder="wa.me/62812...")
                portfolio = c_pf.text_input("Portofolio / GitHub", value=prof["portfolio"], placeholder="github.com/username")

            if st.form_submit_button("Simpan Perubahan Profil", width="stretch", type="primary"):
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

    # --------------------------------------------------------------------------
    # HALAMAN 2: KOMPETISI
    # --------------------------------------------------------------------------
    elif page == "Kompetisi":
        comps = st.session_state.competitions
        page_hero(
            "02 / DIREKTORI KOMPETISI",
            "Eksplorasi Ajang Lomba",
            "Telusuri kompetisi berdasarkan kategori, tenggat pendaftaran, ukuran tim, dan kebutuhan peran.",
            BG_PHOTOS["Kompetisi"],
            "Status Direktori",
            f"{len(comps)} Kompetisi",
        )

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
                        Buka menu <b>+ Daftarkan Kompetisi Baru</b> di atas untuk menambahkan ajang lomba beserta ukuran tim dan peran yang dibutuhkan.
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

        page_hero(
            "03 / PENCOCOKAN TIM",
            "Rekomendasi Rekan Kolaborasi",
            "Peringkat kandidat dihitung secara objektif: 50% Skill Overlap + 30% Role Fit + 20% Time Overlap.",
            BG_PHOTOS["Rekomendasi"],
            "Kandidat Tersedia",
            f"{len(candidates)} Peserta",
        )

        if not prof["name"] or not prof["skills"]:
            html("""
                <div class="arch-card" style="text-align:center;padding:48px 28px !important;">
                    <div style="font-size:19px;font-weight:800;letter-spacing:-0.02em;color:#fff;margin-bottom:6px;">Profil & Keahlian Belum Lengkap</div>
                    <div style="font-size:13.5px;color:var(--muted);max-width:46ch;margin:0 auto;line-height:1.55;">
                        Pilih minimal 1 keahlian utama pada halaman <b>Profil</b> agar sistem dapat menghitung matriks kecocokan kandidat.
                    </div>
                </div>
            """)
        else:
            f_col1, f_col2 = st.columns([1.4, 1], gap="medium")
            with f_col1:
                sel_title = st.selectbox(
                    "Target Kompetisi",
                    comp_titles,
                    index=comp_titles.index(st.session_state.selected_comp),
                )
                st.session_state.selected_comp = sel_title
            with f_col2:
                role_filter = st.selectbox("Filter Peran Kandidat", ["Semua Peran", *ROLE_OPTS])

            active_comp = next((c for c in comps if c["title"] == sel_title), None)

            html(f"""
                <div class="exec-strip">
                    <div class="exec-cell">
                        <div class="exec-lbl">Keahlian & Peran Kamu</div>
                        <div class="exec-val">{len(prof['skills'])} Keahlian</div>
                        <div class="exec-sub">{esc(prof.get('role', '-'))} · Level {esc(prof['level'])}</div>
                    </div>
                    <div class="exec-cell">
                        <div class="exec-lbl">Target Kompetisi</div>
                        <div class="exec-val" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{esc(sel_title)}</div>
                        <div class="exec-sub">{'Filter peran spesifik aktif' if active_comp else 'Pencocokan komplementer umum'}</div>
                    </div>
                    <div class="exec-cell">
                        <div class="exec-lbl">Bobot Kalkulasi Skor</div>
                        <div class="exec-val">50% · 30% · 20%</div>
                        <div class="exec-sub">Skill Overlap · Role Fit · Time Overlap</div>
                    </div>
                </div>
            """)

            scored_list = []
            for c in candidates:
                if role_filter != "Semua Peran" and c.get("role") and c.get("role") != role_filter:
                    continue
                scores = compute_match_breakdown(prof, c, active_comp)
                scored_list.append((c, scores))
            scored_list.sort(key=lambda item: item[1]["total"], reverse=True)

            if not scored_list:
                html("""
                    <div class="arch-card" style="text-align:center;padding:48px 28px !important;">
                        <div style="font-size:18px;font-weight:800;letter-spacing:-0.02em;color:#fff;margin-bottom:6px;">Belum Ada Data Kandidat</div>
                        <div style="font-size:13.5px;color:var(--muted);max-width:44ch;margin:0 auto;line-height:1.55;">
                            Daftar rekomendasi rekan tim akan otomatis diurutkan dari skor tertinggi saat data kandidat tersedia di database.
                        </div>
                    </div>
                """)
            else:
                tab_cards, tab_table = st.tabs(["Matriks Kartu Kandidat", "Tabel Perbandingan"])
                with tab_cards:
                    cols = st.columns(3, gap="medium")
                    for i, (c, sc) in enumerate(scored_list):
                        avail_txt = c.get("availability") or c.get("avail", "Fleksibel")
                        c_role = c.get("role", "Kolaborator")
                        contact_btn = f'<a class="action-link" style="width:100%;margin-top:14px;" href="{esc(safe_url(c["contact"]))}" target="_blank">Hubungi {esc(c["name"].split()[0])} ↗</a>' if c.get("contact") else ""
                        with cols[i % 3]:
                            html(f"""
                                <div class="arch-card hoverable" style="margin-bottom:14px;">
                                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                                        <div style="display:flex;align-items:center;gap:12px;">
                                            {avatar(c['name'], 40)}
                                            <div>
                                                <div style="font-size:16px;font-weight:800;color:#fff;letter-spacing:-0.02em">{esc(c['name'])}</div>
                                                <div style="font-size:12px;color:var(--muted)">{esc(c_role)}</div>
                                            </div>
                                        </div>
                                        <div style="text-align:right">
                                            <div style="font-size:18px;font-weight:800;color:var(--brown-light);line-height:1">{sc['total']}%</div>
                                            <div style="font-size:10px;color:var(--muted);letter-spacing:.06em;margin-top:2px">MATCH</div>
                                        </div>
                                    </div>
                                    <div class="bar-track"><span class="bar-fill" style="width:{sc['total']}%"></span></div>
                                    <div class="score-table">
                                        <div class="score-col"><div style="font-size:10px;color:var(--muted)">SKILL (50%)</div><div style="font-size:12.5px;font-weight:700;color:#fff;margin-top:2px">{sc['skill']}%</div></div>
                                        <div class="score-col"><div style="font-size:10px;color:var(--muted)">ROLE (30%)</div><div style="font-size:12.5px;font-weight:700;color:#fff;margin-top:2px">{sc['role']}%</div></div>
                                        <div class="score-col"><div style="font-size:10px;color:var(--muted)">TIME (20%)</div><div style="font-size:12.5px;font-weight:700;color:#fff;margin-top:2px">{sc['time']}%</div></div>
                                    </div>
                                    <div style="font-size:12px;color:var(--muted);margin-bottom:10px;">{esc(c['campus'])} · {esc(c['major'])} · {esc(avail_txt)}</div>
                                    <div>{badges(c['skills'])}</div>
                                    {contact_btn}
                                </div>
                            """)

                with tab_table:
                    df = pd.DataFrame([{
                        "Nama": c["name"],
                        "Peran": c.get("role", "-"),
                        "Universitas": c["campus"],
                        "Keahlian": ", ".join(c["skills"]),
                        "Skor Total": sc["total"] / 100,
                        "Kontak": safe_url(c["contact"]) if c.get("contact") else ""
                    } for c, sc in scored_list])
                    st.dataframe(df, width="stretch", hide_index=True, column_config={
                        "Skor Total": st.column_config.ProgressColumn("Skor Kecocokan", format="%.0f%%", min_value=0, max_value=1),
                        "Kontak": st.column_config.LinkColumn("WhatsApp / LinkedIn")
                    })

    # --------------------------------------------------------------------------
    # HALAMAN 4: TIM SAYA
    # --------------------------------------------------------------------------
    else:
        teams = st.session_state.teams
        comps = st.session_state.competitions
        comp_choices = [c["title"] for c in comps] or ["Kompetisi Umum"]

        page_hero(
            "04 / MANAJEMEN TIM",
            "Buat & Gabung Tim Lomba",
            "Bentuk tim baru untuk kompetisi incaranmu atau bergabung ke tim yang sedang mencari anggota.",
            BG_PHOTOS["Tim Saya"],
            "Tim Terdaftar",
            f"{len(teams)} Tim Aktif",
        )

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
