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
    initial_sidebar_state="collapsed",
)

# 1. State Initialization (tanpa data dummy bawaan)
st.session_state.setdefault("view", "landing")  # "landing" | "login" | "signup" | "app"
st.session_state.setdefault("accounts", {})
st.session_state.setdefault("active_page", "Profil")
st.session_state.setdefault("user_profile", {
    "name": "", "major": "", "year": 2026, "campus": "",
    "skills": [], "level": "Menengah", "availability": "", "portfolio": ""
})
st.session_state.setdefault("competitions", [])
st.session_state.setdefault("candidates", [])

SKILL_OPTS = ["Python", "Machine Learning", "UI/UX", "Frontend/Web", "Business Analysis", "Finance", "Public Speaking", "Pitching", "Backend", "Cyber Security"]
CAT_OPTS = ["Hackathon", "Business Case", "UI/UX Design", "Data Science", "Competitive Programming"]
PAGES = ["Profil", "Eksplorasi Lomba", "Rekomendasi Tim"]

BG_PHOTOS = {
    "auth": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=2000&q=85",
    "Profil": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1800&q=80",
    "Eksplorasi Lomba": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1800&q=80",
    "Rekomendasi Tim": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=1800&q=80",
}

# 2. UI Helpers
def html(markup: str) -> None:
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()), unsafe_allow_html=True)

def set_view(target: str) -> None:
    st.session_state.view = target
    st.rerun()

def avatar(name: str, size: int = 42) -> str:
    ch = esc((name or "?")[:1].upper())
    return f'<div class="apple-avatar" style="--s:{size}px">{ch}</div>'

def badges(items: list) -> str:
    return "".join(f'<span class="pill-tag">{esc(s)}</span>' for s in items)

def safe_url(url: str) -> str:
    u = url.strip()
    return u if u.startswith(("http://", "https://")) else f"https://{u}"

def page_hero(eyebrow: str, title: str, subtitle: str, photo_url: str, pill_text: str = "") -> None:
    pill_html = f'<div class="hero-pill">{esc(pill_text)}</div>' if pill_text else ""
    html(f"""
        <div class="apple-hero" style="background-image: linear-gradient(95deg, rgba(8,8,10,.90) 0%, rgba(8,8,10,.62) 55%, rgba(8,8,10,.40) 100%), url('{photo_url}');">
            <div class="hero-inner">
                <div>
                    <div class="hero-eyebrow">{esc(eyebrow)}</div>
                    <h1 class="hero-h1">{esc(title)}</h1>
                    <p class="hero-p">{esc(subtitle)}</p>
                </div>
                {pill_html}
            </div>
        </div>
    """)

# 3. Apple Website + Gotham CSS
curr_view = st.session_state.view
is_app = curr_view == "app"

bg_css = f"""
.stApp {{
    background-image: radial-gradient(circle at 50% 35%, rgba(0, 0, 0, .52) 0%, rgba(0, 0, 0, .86) 100%), url('{BG_PHOTOS["auth"]}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
""" if not is_app else """
.stApp { background: #08080A; }
"""

html(f"""<style>
@import url('https://fonts.cdnfonts.com/css/gotham-6');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

:root {{
    color-scheme: dark;
    --bg: #08080A;
    --card: rgba(20, 20, 24, 0.78);
    --surface: #121216;
    --surface-2: #1A1A20;
    --border: rgba(255, 255, 255, 0.14);
    --border-strong: rgba(255, 255, 255, 0.30);
    --ink: #F5F5F7;
    --muted: #A1A1A6;
    --subtle: #6E6E73;
}}

@keyframes pageFade {{
    from {{ opacity: 0; transform: translateY(14px) scale(0.995); }}
    to {{ opacity: 1; transform: translateY(0) scale(1); }}
}}

html, body, .stApp, [data-testid="stMarkdownContainer"], input, textarea, button, label, select, div {{
    font-family: 'Gotham', 'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header[data-testid="stHeader"] {{
    display: none !important;
}}
{bg_css}
.block-container {{
    max-width: 1140px;
    padding-top: {'1.25rem' if is_app else '2.5rem'};
    padding-bottom: 3.5rem;
    animation: pageFade .35s cubic-bezier(0.16, 1, 0.3, 1);
}}
[data-testid="stHorizontalBlock"] {{ gap: 1.15rem !important; align-items: center; }}
[data-testid="stMarkdownContainer"] h4 {{
    font-size: 17px !important; font-weight: 700 !important;
    letter-spacing: -0.025em !important; color: var(--ink) !important;
    margin: 0 0 .5rem 0 !important;
}}

/* Frosted Glass Cards & Forms */
.glass-card, [data-testid="stForm"] {{
    background: var(--card) !important;
    backdrop-filter: blur(30px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
    border: 1px solid var(--border) !important;
    border-radius: 26px !important;
    padding: 30px 32px !important;
    box-shadow: 0 28px 65px rgba(0, 0, 0, 0.55) !important;
    transition: transform .2s cubic-bezier(0.16, 1, 0.3, 1), border-color .2s ease !important;
}}
.glass-card.hoverable:hover {{
    transform: translateY(-3px);
    border-color: var(--border-strong) !important;
}}
.glass-card.hoverable:active {{
    transform: scale(0.99);
}}

/* Inputs */
[data-baseweb="input"] > div, [data-baseweb="select"] > div, [data-baseweb="textarea"] > div {{
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 14px !important;
    color: var(--ink) !important;
    transition: border-color .15s ease, background .15s ease !important;
}}
[data-baseweb="input"] > div:focus-within, [data-baseweb="select"] > div:focus-within {{
    border-color: #FFFFFF !important;
    background: rgba(255, 255, 255, 0.11) !important;
}}

/* Apple Pill Buttons & Click Animation */
.stButton > button, .stFormSubmitButton > button, .pill-link {{
    border-radius: 980px !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    letter-spacing: -0.01em !important;
    height: 44px !important;
    padding: 0 1.4rem !important;
    transition: transform .12s cubic-bezier(0.34, 1.56, 0.64, 1), background .18s ease, border-color .18s ease, box-shadow .18s ease !important;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover, .pill-link:hover {{
    transform: translateY(-1px) scale(1.015);
}}
.stButton > button:active, .stFormSubmitButton > button:active, .pill-link:active {{
    transform: scale(0.96) translateY(1px) !important;
}}
[data-testid^="stBaseButton-primary"] {{
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #FFFFFF !important;
    box-shadow: 0 10px 25px -6px rgba(255, 255, 255, 0.35) !important;
}}
[data-testid^="stBaseButton-primary"] * {{
    color: #000000 !important;
    font-weight: 700 !important;
}}
[data-testid^="stBaseButton-primary"]:hover {{
    background: #E8E8ED !important;
}}
[data-testid^="stBaseButton-secondary"] {{
    background: rgba(255, 255, 255, 0.10) !important;
    backdrop-filter: blur(16px) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.24) !important;
}}
[data-testid^="stBaseButton-secondary"]:hover {{
    background: rgba(255, 255, 255, 0.18) !important;
    border-color: rgba(255, 255, 255, 0.45) !important;
}}
.pill-link {{
    display: flex; align-items: center; justify-content: center;
    text-decoration: none !important;
    background: #FFFFFF; color: #000000 !important;
    margin-top: 16px;
}}

/* Landing Hero Centered */
.landing-wrap {{
    text-align: center;
    max-width: 780px;
    margin: 11vh auto 28px;
    padding: 0 16px;
}}
.landing-badge {{
    display: inline-block;
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.22);
    padding: 7px 18px;
    border-radius: 980px;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #FFFFFF;
    margin-bottom: 24px;
}}
.landing-title {{
    font-size: clamp(42px, 6vw, 72px);
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.04;
    color: #FFFFFF !important;
    margin: 0 0 22px 0;
}}
.landing-sub {{
    font-size: clamp(15px, 1.6vw, 18.5px);
    line-height: 1.6;
    color: rgba(245, 245, 247, 0.82);
    max-width: 54ch;
    margin: 0 auto 12px;
    font-weight: 400;
}}

/* Editorial Photographic Hero inside App */
.apple-hero {{
    background-size: cover;
    background-position: center;
    border-radius: 26px;
    border: 1px solid var(--border);
    padding: 42px 40px;
    margin: 14px 0 24px;
    box-shadow: 0 26px 55px -20px rgba(0, 0, 0, 0.75);
}}
.hero-inner {{
    display: flex; align-items: flex-end; justify-content: space-between;
    flex-wrap: wrap; gap: 20px;
}}
.hero-eyebrow {{
    font-size: 11px; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: rgba(255, 255, 255, 0.7); margin-bottom: 8px;
}}
.hero-h1 {{
    font-size: clamp(26px, 3.4vw, 42px); font-weight: 800;
    letter-spacing: -0.035em; line-height: 1.08; color: #FFFFFF !important; margin: 0;
}}
.hero-p {{
    font-size: 14.5px; color: rgba(245, 245, 247, 0.80);
    max-width: 52ch; margin: 10px 0 0; line-height: 1.55;
}}
.hero-pill {{
    background: rgba(255, 255, 255, 0.14);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.24);
    padding: 9px 18px; border-radius: 980px;
    font-size: 12.5px; font-weight: 700; color: #FFFFFF;
}}

/* Micro Components */
.apple-avatar {{
    flex: none; width: var(--s); height: var(--s); border-radius: 50%;
    background: var(--surface-2); border: 1px solid var(--border-strong);
    display: flex; align-items: center; justify-content: center;
    color: #FFFFFF; font-weight: 800; font-size: calc(var(--s) * 0.4);
}}
.pill-tag {{
    display: inline-block; background: rgba(255, 255, 255, 0.08);
    color: var(--ink); border: 1px solid var(--border);
    padding: 5px 13px; border-radius: 980px;
    font-size: 12px; font-weight: 600; margin: 3px 6px 3px 0;
    transition: background .15s ease, transform .1s ease;
}}
.pill-tag:hover {{ background: rgba(255, 255, 255, 0.16); transform: translateY(-1px); }}
.kv-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 12px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-size: 13.5px;
}}
.kv-row:last-child {{ border-bottom: none; }}
.bento-stat {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 22px; padding: 22px 26px;
}}
.bento-num {{
    font-size: 34px; font-weight: 800; letter-spacing: -0.03em;
    color: #FFFFFF; line-height: 1.1; margin-top: 6px;
}}
.bar-track {{ height: 6px; border-radius: 980px; background: rgba(255,255,255,.1); overflow: hidden; margin: 14px 0; }}
.bar-fill {{ display: block; height: 100%; background: #FFFFFF; border-radius: 980px; }}
</style>""")

# ==============================================================================
# STAGE 1: CENTERED LANDING PAGE (Slogan di Tengah + Tombol Kiri Log In, Kanan Sign Up)
# ==============================================================================
if curr_view == "landing":
    html("""
        <div class="landing-wrap">
            <span class="landing-badge">Cari Teman Lomba &nbsp;·&nbsp; Fasilkom UI</span>
            <h1 class="landing-title">Bangun Tim Terbaik.<br>Menangkan Kompetisi.</h1>
            <p class="landing-sub">
                Platform kolaborasi mahasiswa untuk menemukan rekan satu frekuensi di ajang Hackathon, Business Case, UI/UX Design, dan Data Science.
            </p>
        </div>
    """)

    # Bawah Slogan: Kiri Log In, Kanan Sign Up (Centered di Tengah)
    _, btn_left, btn_right, _ = st.columns([1.35, 0.65, 0.65, 1.35], gap="small")
    with btn_left:
        if st.button("Log In", width="stretch", type="primary"):
            set_view("login")
    with btn_right:
        if st.button("Sign Up", width="stretch", type="secondary"):
            set_view("signup")

    html("""
        <div style="text-align:center;margin-top:64px;font-size:12px;color:rgba(255,255,255,.55);letter-spacing:.08em;text-transform:uppercase;font-weight:600;">
            Hackathon &nbsp;·&nbsp; Business Case &nbsp;·&nbsp; UI/UX Design &nbsp;·&nbsp; Data Science &nbsp;·&nbsp; Competitive Programming
        </div>
    """)

# ==============================================================================
# STAGE 2A: DEDICATED LOG IN PAGE
# ==============================================================================
elif curr_view == "login":
    _, col_card, _ = st.columns([1, 1.15, 1])
    with col_card:
        if st.button("← Kembali", type="secondary"):
            set_view("landing")

        with st.form("login_form"):
            html("""
                <div style="text-align:center;margin-bottom:18px;">
                    <div style="font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;">Cari Teman Lomba</div>
                    <div style="font-size:28px;font-weight:800;letter-spacing:-0.03em;color:#fff;">Log In</div>
                    <div style="font-size:13.5px;color:var(--muted);margin-top:4px;">Masuk ke akun kolaborasimu untuk melanjutkan.</div>
                </div>
            """)
            email_in = st.text_input("Email atau Username", placeholder="nama@ui.ac.id")
            pass_in = st.text_input("Kata Sandi", type="password", placeholder="••••••••")

            if st.form_submit_button("Masuk ke Dashboard", width="stretch", type="primary"):
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
    _, col_card, _ = st.columns([0.95, 1.25, 0.95])
    with col_card:
        if st.button("← Kembali", type="secondary"):
            set_view("landing")

        with st.form("signup_form"):
            html("""
                <div style="text-align:center;margin-bottom:18px;">
                    <div style="font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;">Cari Teman Lomba</div>
                    <div style="font-size:28px;font-weight:800;letter-spacing:-0.03em;color:#fff;">Sign Up</div>
                    <div style="font-size:13.5px;color:var(--muted);margin-top:4px;">Buat akun baru untuk mulai mencari rekan tim lomba.</div>
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
# STAGE 3: MAIN WEBSITE DENGAN TOP NAVBAR BUTTONS (Setelah Login / Sign Up)
# ==============================================================================
else:
    prof = st.session_state.user_profile
    page = st.session_state.active_page

    # Top Horizontal Navbar menggunakan Pill Buttons (tanpa radio circle)
    nav_brand, n1, n2, n3, nav_user, nav_out = st.columns([1.25, 0.75, 0.95, 0.95, 1.05, 0.65], gap="small")
    with nav_brand:
        html("""
            <div style="display:flex;align-items:center;gap:11px;">
                <div style="width:32px;height:32px;border-radius:50%;background:#FFFFFF;color:#000000;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:12.5px;letter-spacing:-0.04em;">CT</div>
                <div>
                    <div style="font-size:14.5px;font-weight:800;letter-spacing:-0.02em;color:#fff;line-height:1.1">Cari Teman Lomba</div>
                    <div style="font-size:11px;color:var(--muted)">Fasilkom UI · Kelompok 17</div>
                </div>
            </div>
        """)
    for col_nav, p_name in zip((n1, n2, n3), PAGES):
        with col_nav:
            if st.button(p_name, key=f"nav_{p_name}", width="stretch", type="primary" if page == p_name else "secondary"):
                st.session_state.active_page = p_name
                st.rerun()
    with nav_user:
        html(f"""
            <div style="display:flex;align-items:center;justify-content:flex-end;gap:10px;">
                {avatar(prof['name'] or 'U', 32)}
                <div style="text-align:left;min-width:0;">
                    <div style="font-size:12.5px;font-weight:700;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{esc(prof['name'] or 'Mahasiswa')}</div>
                    <div style="font-size:11px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{esc(prof['campus'] or 'Kolaborator')}</div>
                </div>
            </div>
        """)
    with nav_out:
        if st.button("Log Out", width="stretch", type="secondary"):
            set_view("landing")

    # --------------------------------------------------------------------------
    # HALAMAN 1: PROFIL
    # --------------------------------------------------------------------------
    if page == "Profil":
        filled = sum(bool(prof[k]) for k in ("name", "campus", "major", "skills", "availability", "portfolio"))
        page_hero(
            "Profil Kolaborator",
            "Identitas & Keahlian.",
            "Lengkapi rekam jejak akademik dan keahlian utamamu agar calon rekan tim yang tepat dapat menemukanmu.",
            BG_PHOTOS["Profil"],
            f"Kelengkapan {int(filled / 6 * 100)}%",
        )

        col_form, col_prev = st.columns([1.18, 0.82], gap="medium")

        with col_form, st.form("profile_form"):
            st.markdown("#### Data Akademik & Keahlian")
            name = st.text_input("Nama Lengkap *", value=prof["name"], placeholder="Farraj Bagas")
            c1, c2, c3 = st.columns([1.25, 1.25, 0.8], gap="small")
            campus = c1.text_input("Universitas", value=prof["campus"], placeholder="Universitas Indonesia")
            major = c2.text_input("Program Studi", value=prof["major"], placeholder="Ilmu Komputer")
            year = c3.number_input("Angkatan", 2015, 2030, prof["year"])

            skills = st.multiselect("Keahlian Utama *", SKILL_OPTS, default=prof["skills"])
            level = st.select_slider("Tingkat Pengalaman", ["Pemula", "Menengah", "Mahir"], value=prof["level"])
            c4, c5 = st.columns(2, gap="small")
            portfolio = c4.text_input("Tautan Portofolio / GitHub", value=prof["portfolio"], placeholder="github.com/username")
            avail = c5.text_input("Ketersediaan Waktu", value=prof["availability"], placeholder="Weekday malam & weekend")

            if st.form_submit_button("Simpan Profil", width="stretch", type="primary"):
                if not name.strip() or not skills:
                    st.error("Nama lengkap dan minimal 1 keahlian wajib diisi.")
                else:
                    st.session_state.user_profile = {
                        "name": name.strip(), "major": major.strip(), "year": year, "campus": campus.strip(),
                        "skills": skills, "level": level, "availability": avail.strip(), "portfolio": portfolio.strip()
                    }
                    st.toast("Profil berhasil disimpan.")
                    st.rerun()

        with col_prev:
            skills_html = badges(prof["skills"]) if prof["skills"] else '<span style="font-size:13px;color:var(--subtle)">Belum ada keahlian dipilih</span>'
            port_btn = f'<a class="pill-link" href="{esc(safe_url(prof["portfolio"]))}" target="_blank">Buka Portofolio ↗</a>' if prof["portfolio"] else ""
            html(f"""
                <div class="glass-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
                        <span style="font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);">Kartu Profil Mahasiswa</span>
                        <span style="font-size:11.5px;font-weight:700;color:#FFFFFF;">
                            {'Siap Berkolaborasi' if prof['skills'] else 'Belum Lengkap'}
                        </span>
                    </div>
                    <div style="display:flex;align-items:center;gap:16px;margin-bottom:22px;">
                        {avatar(prof['name'] or '?', 56)}
                        <div>
                            <div style="font-size:21px;font-weight:800;letter-spacing:-0.025em;color:#fff;">{esc(prof['name'] or 'Nama Belum Diisi')}</div>
                            <div style="font-size:13px;color:var(--muted);margin-top:3px;">{esc(prof['major'] or 'Program Studi')} · {esc(prof['campus'] or 'Universitas')}</div>
                        </div>
                    </div>
                    <div style="border-top:1px solid rgba(255,255,255,.1);padding-top:6px;margin-bottom:18px;">
                        <div class="kv-row"><span style="color:var(--muted)">Angkatan</span><span style="font-weight:700;color:#fff">{prof['year']}</span></div>
                        <div class="kv-row"><span style="color:var(--muted)">Tingkat Pengalaman</span><span style="font-weight:700;color:#fff">{esc(prof['level'])}</span></div>
                        <div class="kv-row"><span style="color:var(--muted)">Ketersediaan Waktu</span><span style="font-weight:700;color:#fff">{esc(prof['availability'] or 'Fleksibel')}</span></div>
                    </div>
                    <div style="font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:10px;">
                        Keahlian ({len(prof['skills'])})
                    </div>
                    <div>{skills_html}</div>
                    {port_btn}
                </div>
            """)

    # --------------------------------------------------------------------------
    # HALAMAN 2: EKSPLORASI LOMBA
    # --------------------------------------------------------------------------
    elif page == "Eksplorasi Lomba":
        comps = st.session_state.competitions
        page_hero(
            "Katalog Kompetisi",
            "Eksplorasi Ajang Lomba.",
            "Temukan kompetisi teknologi, bisnis, dan desain untuk menguji kemampuan terbaik timmu.",
            BG_PHOTOS["Eksplorasi Lomba"],
            f"{len(comps)} Kompetisi",
        )

        c1, c2, c3 = st.columns([2.2, 1, 1], gap="small")
        q = c1.text_input("Cari", placeholder="Cari nama kompetisi atau penyelenggara...", label_visibility="collapsed").strip().lower()
        cat_f = c2.selectbox("Kategori", ["Semua Kategori", *CAT_OPTS], label_visibility="collapsed")
        sort_f = c3.selectbox("Urutan", ["Deadline Terdekat", "Nama (A-Z)", "Terbaru"], label_visibility="collapsed")

        with st.expander("+ Daftarkan Kompetisi Baru"):
            with st.form("add_comp", clear_on_submit=True):
                f1, f2 = st.columns(2, gap="small")
                title = f1.text_input("Nama Kompetisi *", placeholder="Gemastik XIX 2026")
                cat = f1.selectbox("Kategori Bidang", CAT_OPTS)
                org = f2.text_input("Penyelenggara", placeholder="Puspresnas / Kemendikbud")
                ddl = f2.date_input("Batas Pendaftaran")
                if st.form_submit_button("Simpan Kompetisi", width="stretch", type="primary"):
                    if title.strip():
                        comps.append({"title": title.strip(), "category": cat, "organizer": org.strip() or "-", "deadline": str(ddl)})
                        st.toast("Kompetisi berhasil ditambahkan.")
                        st.rerun()
                    else:
                        st.warning("Nama kompetisi wajib diisi.")

        filtered = [
            c for c in comps
            if (cat_f == "Semua Kategori" or c["category"] == cat_f)
            and (not q or q in c["title"].lower() or q in c["organizer"].lower())
        ]
        if sort_f == "Deadline Terdekat":
            filtered.sort(key=lambda x: x["deadline"])
        elif sort_f == "Nama (A-Z)":
            filtered.sort(key=lambda x: x["title"].lower())
        else:
            filtered = list(reversed(filtered))

        if not filtered:
            html("""
                <div class="glass-card" style="text-align:center;padding:52px 28px !important;margin-top:12px;">
                    <div style="font-size:20px;font-weight:800;letter-spacing:-0.02em;color:#fff;margin-bottom:8px;">Belum Ada Kompetisi Terdaftar</div>
                    <div style="font-size:14px;color:var(--muted);max-width:44ch;margin:0 auto;line-height:1.55;">
                        Klik panel <b>+ Daftarkan Kompetisi Baru</b> di atas untuk menambahkan ajang lomba yang sedang kamu incar.
                    </div>
                </div>
            """)
        else:
            cols = st.columns(2, gap="medium")
            for i, comp in enumerate(filtered):
                with cols[i % 2]:
                    html(f"""
                        <div class="glass-card hoverable" style="margin-bottom:16px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                                <span class="pill-tag" style="margin:0">{esc(comp['category'])}</span>
                                <span style="font-size:12.5px;color:var(--muted);font-weight:600;">Tenggat: <b style="color:#fff">{esc(comp['deadline'])}</b></span>
                            </div>
                            <div style="font-size:22px;font-weight:800;letter-spacing:-0.03em;color:#fff;margin-bottom:6px;">{esc(comp['title'])}</div>
                            <div style="font-size:13.5px;color:var(--muted);">Penyelenggara: {esc(comp['organizer'])}</div>
                        </div>
                    """)

    # --------------------------------------------------------------------------
    # HALAMAN 3: REKOMENDASI TIM
    # --------------------------------------------------------------------------
    else:
        candidates = st.session_state.candidates
        page_hero(
            "Rekomendasi Rekan",
            "Temukan Partner Terbaikmu.",
            "Rekomendasi kandidat rekan tim yang disusun berdasarkan komplementaritas keahlian dan jadwal.",
            BG_PHOTOS["Rekomendasi Tim"],
            f"{len(candidates)} Kandidat",
        )

        if not prof["name"] or not prof["skills"]:
            html("""
                <div class="glass-card" style="text-align:center;padding:52px 28px !important;">
                    <div style="font-size:21px;font-weight:800;letter-spacing:-0.02em;color:#fff;margin-bottom:8px;">Lengkapi Keahlianmu Terlebih Dahulu</div>
                    <div style="font-size:14px;color:var(--muted);max-width:46ch;margin:0 auto;line-height:1.55;">
                        Pilih minimal 1 keahlian utama pada halaman <b>Profil</b> agar sistem dapat mencocokkan profilmu dengan kandidat yang relevan.
                    </div>
                </div>
            """)
        else:
            s1, s2, s3 = st.columns(3, gap="medium")
            with s1:
                html(f'<div class="bento-stat"><div style="font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)">Keahlian Aktif</div><div class="bento-num">{len(prof["skills"])} Skill</div></div>')
            with s2:
                html(f'<div class="bento-stat"><div style="font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)">Tingkat Pengalaman</div><div class="bento-num">{esc(prof["level"])}</div></div>')
            with s3:
                html(f'<div class="bento-stat"><div style="font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)">Kandidat Tersedia</div><div class="bento-num">{len(candidates)} Rekan</div></div>')

            st.write("")
            if not candidates:
                html("""
                    <div class="glass-card" style="text-align:center;padding:52px 28px !important;">
                        <div style="font-size:20px;font-weight:800;letter-spacing:-0.02em;color:#fff;margin-bottom:8px;">Belum Ada Kandidat di Database</div>
                        <div style="font-size:14px;color:var(--muted);max-width:44ch;margin:0 auto;line-height:1.55;">
                            Daftar rekomendasi rekan tim akan otomatis muncul di sini saat data peserta telah tersedia.
                        </div>
                    </div>
                """)
            else:
                tab_cards, tab_table = st.tabs(["Tampilan Kartu", "Tabel Perbandingan"])
                with tab_cards:
                    cols = st.columns(3, gap="medium")
                    for i, c in enumerate(candidates):
                        avail_txt = c.get("availability") or c.get("avail", "Fleksibel")
                        contact_btn = f'<a class="pill-link" href="{esc(safe_url(c["contact"]))}" target="_blank">Hubungi {esc(c["name"].split()[0])} ↗</a>' if c.get("contact") else ""
                        with cols[i % 3]:
                            html(f"""
                                <div class="glass-card hoverable" style="margin-bottom:16px;">
                                    <div style="display:flex;justify-content:space-between;align-items:center;">
                                        <div style="display:flex;align-items:center;gap:12px;">
                                            {avatar(c['name'], 44)}
                                            <div>
                                                <div style="font-size:16.5px;font-weight:800;color:#fff;letter-spacing:-0.02em">{esc(c['name'])}</div>
                                                <div style="font-size:12.5px;color:var(--muted)">{esc(c['major'])}</div>
                                            </div>
                                        </div>
                                        <span style="font-size:15px;font-weight:800;color:#fff">{c['match']}%</span>
                                    </div>
                                    <div class="bar-track"><span class="bar-fill" style="width:{c['match']}%"></span></div>
                                    <div style="font-size:12.5px;color:var(--muted);margin-bottom:12px;">{esc(c['campus'])} · {esc(avail_txt)}</div>
                                    <div>{badges(c['skills'])}</div>
                                    {contact_btn}
                                </div>
                            """)

                with tab_table:
                    df = pd.DataFrame([{
                        "Nama": c["name"], "Universitas": c["campus"], "Program Studi": c["major"],
                        "Keahlian": ", ".join(c["skills"]), "Kecocokan": c["match"] / 100,
                        "Kontak": safe_url(c["contact"]) if c.get("contact") else ""
                    } for c in candidates])
                    st.dataframe(df, width="stretch", hide_index=True, column_config={
                        "Kecocokan": st.column_config.ProgressColumn("Skor Kecocokan", format="%.0f%%", min_value=0, max_value=1),
                        "Kontak": st.column_config.LinkColumn("Kontak")
                    })
