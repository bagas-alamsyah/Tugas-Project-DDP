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
    layout=cfg["default_layout"],
    initial_sidebar_state=cfg["default_sidebar_state"],
)

# 1. State Initialization (tanpa data dummy)
st.session_state.setdefault("user_profile", {
    "name": "", "major": "", "year": 2026, "campus": "",
    "skills": [], "level": "Menengah", "availability": "", "portfolio": ""
})
st.session_state.setdefault("competitions", [])
st.session_state.setdefault("candidates", [])

SKILL_OPTS = ["Python", "Machine Learning", "UI/UX", "Frontend/Web", "Business Analysis", "Finance", "Public Speaking", "Pitching", "Backend", "Cyber Security"]
CAT_OPTS = ["Hackathon", "Business Case", "UI/UX Design", "Data Science", "Competitive Programming"]

PAGE_THEMES = {
    "👤 Profil Saya": {
        "p1": "#6366F1", "p2": "#A855F7", "tint": "rgba(99, 102, 241, .15)",
        "hero": "linear-gradient(130deg, #1E1B4B 0%, #312E81 50%, #581C87 100%)",
        "wm": "👤", "tag": "STEP 01 • IDENTITY STUDIO",
    },
    "📅 Eksplorasi Lomba": {
        "p1": "#06B6D4", "p2": "#10B981", "tint": "rgba(6, 182, 212, .15)",
        "hero": "linear-gradient(130deg, #042F2E 0%, #0F766E 50%, #155E75 100%)",
        "wm": "🏆", "tag": "STEP 02 • COMPETITION HUB",
    },
    "🤝 Rekomendasi Teman": {
        "p1": "#F59E0B", "p2": "#EC4899", "tint": "rgba(245, 158, 11, .15)",
        "hero": "linear-gradient(130deg, #451A03 0%, #831843 55%, #7C2D12 100%)",
        "wm": "⚡", "tag": "STEP 03 • SMART MATCHING",
    },
}

# 2. UI Helpers
def html(markup: str) -> None:
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()), unsafe_allow_html=True)

def avatar(name: str, size: int = 40) -> str:
    return f'<div class="avatar" style="--s:{size}px">{esc((name or "?")[:1].upper())}</div>'

def badges(items: list) -> str:
    return "".join(f'<span class="skill-badge">{esc(s)}</span>' for s in items)

def safe_url(url: str) -> str:
    u = url.strip()
    return u if u.startswith(("http://", "https://")) else f"https://{u}"

def hero(title: str, subtitle: str, extra_html: str = "") -> None:
    t = PAGE_THEMES[page]
    html(f"""
        <div class="hero-banner" data-wm="{t['wm']}">
            <div class="row between" style="flex-wrap:wrap;gap:16px">
                <div>
                    <span class="hero-tag">{esc(t['tag'])}</span>
                    <h1 class="hero-title">{esc(title)}</h1>
                    <p class="hero-subtitle">{esc(subtitle)}</p>
                </div>
                {extra_html}
            </div>
        </div>
    """)

def empty_box(icon: str, title: str, desc: str) -> None:
    html(f'<div class="empty-box"><div class="empty-icon">{icon}</div><div class="empty-title">{title}</div><div class="empty-desc">{desc}</div></div>')

# 3. Sidebar Navigation
prof = st.session_state.user_profile
with st.sidebar:
    html('<div class="row" style="margin-bottom:14px"><span style="font-size:28px">🏆</span><div><div style="font-size:18px;font-weight:800;line-height:1.15">Cari Teman Lomba</div><div class="sub">Kelompok 17 • DDP 1 Fasilkom UI</div></div></div>')
    page = st.radio("Navigasi", list(PAGE_THEMES.keys()), label_visibility="collapsed")
    st.divider()
    if prof["name"]:
        html(f"""
            <div class="side-card ok">
                <div class="row">
                    {avatar(prof["name"], 38)}
                    <div style="min-width:0">
                        <div class="name" style="font-size:13.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{esc(prof["name"])}</div>
                        <div class="sub" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{esc(prof["campus"] or "Mahasiswa")}</div>
                    </div>
                </div>
                <div class="status-on">● Profil aktif ({len(prof["skills"])} skill)</div>
            </div>
        """)
    else:
        html("""
            <div class="side-card warn">
                <div class="row" style="align-items:flex-start;gap:10px">
                    <div class="side-warn-icon">⚠️</div>
                    <div>
                        <div style="font-size:13px;font-weight:700;color:#FBBF24;line-height:1.25">Profil Belum Lengkap</div>
                        <div class="sub" style="margin-top:4px;line-height:1.45">Isi nama & minimal 1 skill di menu Profil Saya.</div>
                    </div>
                </div>
            </div>
        """)
    st.caption("Fasilkom UI © 2026")

# 4. Dynamic Theme, Spacing & Click Animations CSS
t = PAGE_THEMES[page]
html(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root {{
    color-scheme: dark; --bg: #0D0E1C; --surface: #171930; --border: #282B4E;
    --ink: #F8FAFC; --muted: #94A3B8; --success: #34D399;
    --primary: {t['p1']}; --accent: {t['p2']}; --tint: {t['tint']}; --hero-bg: {t['hero']};
}}
@keyframes pageIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes growBar {{ from {{ width: 0; }} }}
@keyframes pulseRing {{ 0% {{ box-shadow: 0 0 0 0 var(--tint); }} 70% {{ box-shadow: 0 0 0 10px transparent; }} 100% {{ box-shadow: 0 0 0 0 transparent; }} }}

html, body, .stApp, [data-testid="stMarkdownContainer"], input, textarea, button, label {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
.stApp {{ background: radial-gradient(circle at 85% 0%, var(--tint), transparent 45%), var(--bg); color: var(--ink); }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ max-width: 1160px; padding-top: 1.5rem; padding-bottom: 2.5rem; animation: pageIn .35s cubic-bezier(.22, 1, .36, 1); }}
[data-testid="stHorizontalBlock"] {{ gap: 1.35rem !important; align-items: stretch; }}
[data-testid="stMarkdownContainer"] h4 {{ margin: 0 0 .5rem 0 !important; padding: 0 !important; font-weight: 700 !important; }}

/* Sidebar & Radio Click Animation */
[data-testid="stSidebar"] {{ background: var(--surface); border-right: 1px solid var(--border); }}
[data-testid="stSidebar"] [role="radiogroup"] label {{
    padding: 11px 14px; border-radius: 12px; border: 1px solid transparent;
    transition: transform .15s cubic-bezier(.34,1.56,.64,1), background .2s, border-color .2s, box-shadow .2s;
    cursor: pointer; user-select: none;
}}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background: rgba(255,255,255,.04); transform: translateX(3px); }}
[data-testid="stSidebar"] [role="radiogroup"] label:active {{ transform: scale(.95) !important; background: var(--tint); }}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{
    background: var(--tint); border-color: var(--primary);
    box-shadow: inset 4px 0 0 var(--primary), 0 6px 20px -8px var(--primary); font-weight: 700;
}}

/* Sidebar Status Card (Anti-nabrak, padding simetris) */
.side-card {{
    background: rgba(10, 11, 24, .6); border: 1px solid var(--border);
    border-radius: 14px; padding: 14px 15px; margin: 2px 0 10px;
}}
.side-card.warn {{ border-color: rgba(251, 191, 36, .3); background: rgba(251, 191, 36, .05); }}
.side-card.ok {{ border-color: rgba(52, 211, 153, .3); }}
.side-warn-icon {{
    flex: none; width: 30px; height: 30px; border-radius: 8px;
    background: rgba(251, 191, 36, .14); display: flex; align-items: center; justify-content: center; font-size: 14px;
}}

/* Tactile Click Animations for Buttons, Links, Tabs & Expanders */
.stButton > button, .stFormSubmitButton > button, .stLinkButton > a, .btn-link, [data-baseweb="tab"], [data-testid="stExpander"] summary {{
    transition: transform .14s cubic-bezier(.34, 1.56, .64, 1), box-shadow .2s ease, border-color .2s ease, filter .2s !important;
    border-radius: 12px !important;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stLinkButton > a:hover, .btn-link:hover {{
    transform: translateY(-2px); box-shadow: 0 8px 22px -6px var(--primary) !important; border-color: var(--primary) !important;
}}
.stButton > button:active, .stFormSubmitButton > button:active, .stLinkButton > a:active, .btn-link:active,
[data-baseweb="tab"]:active, [data-testid="stExpander"] summary:active {{
    transform: scale(.95) translateY(1px) !important;
    box-shadow: 0 0 0 5px var(--tint), 0 2px 10px var(--primary) !important;
    filter: brightness(1.12);
}}
[data-testid^="stBaseButton-primary"] {{
    background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
    border: none !important; color: #fff !important; font-weight: 700 !important;
    margin-top: .4rem !important;
}}
.btn-link {{
    display: block; text-align: center; text-decoration: none !important;
    background: rgba(255,255,255,.05); border: 1px solid var(--border);
    color: var(--ink) !important; padding: 10px 16px; font-size: 13.5px; font-weight: 600; margin-top: 12px;
}}

/* Hero Banner */
.hero-banner {{
    position: relative; overflow: hidden; background: var(--hero-bg); border-radius: 20px;
    padding: 26px 32px; margin-bottom: 14px; border: 1px solid rgba(255,255,255,.14);
    box-shadow: 0 18px 40px -24px var(--primary);
}}
.hero-banner::after {{
    content: attr(data-wm); position: absolute; right: 24px; bottom: -18px;
    font-size: 108px; opacity: .09; pointer-events: none;
}}
.hero-tag {{ display: inline-block; background: rgba(255,255,255,.15); padding: 4px 12px; border-radius: 999px; font-size: 11px; font-weight: 800; letter-spacing: .7px; margin-bottom: 8px; }}
.hero-title {{ font-size: clamp(22px, 2.6vw, 30px); font-weight: 800; margin: 0; color: #fff !important; }}
.hero-subtitle {{ font-size: 13.5px; color: rgba(255,255,255,.82); margin: 6px 0 0; max-width: 58ch; }}
.hero-stat {{ background: rgba(13, 14, 28, .38); border: 1px solid rgba(255,255,255,.16); border-radius: 14px; padding: 12px 18px; min-width: 185px; backdrop-filter: blur(8px); }}

/* Self-Contained UI Card & Form (Padding simetris, bebas nabrak border) */
.ui-card, [data-testid="stForm"] {{
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 18px !important; padding: 24px 26px !important;
    box-sizing: border-box;
    transition: transform .22s cubic-bezier(.34,1.56,.64,1), border-color .22s, box-shadow .22s;
}}
.ui-card:hover {{
    transform: translateY(-3px); border-color: var(--primary) !important; box-shadow: 0 14px 30px -18px var(--primary);
}}
.ui-card:active {{ transform: scale(.985); }}
.card-title {{ font-size: 18px; font-weight: 700; margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px; color: var(--ink); }}

[data-testid="stMetric"] {{
    background: linear-gradient(180deg, var(--tint), var(--surface));
    border: 1px solid var(--border); border-top: 3px solid var(--primary);
    border-radius: 16px; padding: 14px 18px; transition: transform .2s;
}}
[data-testid="stMetric"]:hover {{ transform: translateY(-2px); border-color: var(--primary); }}

/* Components & Badges */
.avatar {{ flex: none; width: var(--s); height: var(--s); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 800; font-size: calc(var(--s)*.42); background: linear-gradient(135deg, var(--primary), var(--accent)); box-shadow: 0 4px 14px -4px var(--primary); }}
.skill-badge {{ display: inline-block; background: var(--tint); color: #E2E8F0; border: 1px solid rgba(255,255,255,.18); padding: 4px 11px; border-radius: 999px; font-size: 12px; font-weight: 600; margin: 3px 6px 3px 0; transition: transform .15s, border-color .15s; cursor: pointer; }}
.skill-badge:hover {{ transform: scale(1.05); border-color: var(--primary); }}
.skill-badge:active {{ transform: scale(.93); }}
.match-badge {{ background: rgba(52,211,153,.15); color: #6EE7B7; border: 1px solid rgba(52,211,153,.4); padding: 4px 11px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
.match-badge.top {{ background: rgba(251,191,36,.18); color: #FDE68A; border-color: #F59E0B; animation: pulseRing 2s infinite; }}
.bar-track {{ height: 7px; border-radius: 999px; background: rgba(255,255,255,.1); overflow: hidden; margin: 10px 0 12px; }}
.bar-fill {{ display: block; height: 100%; background: linear-gradient(90deg, var(--primary), var(--accent)); animation: growBar .7s ease-out; }}

/* Page 1: ID Pass Elements */
.id-header {{
    background: linear-gradient(90deg, var(--primary), var(--accent));
    border-radius: 12px; padding: 10px 14px; margin-bottom: 16px;
    display: flex; align-items: center; justify-content: space-between;
    font-size: 11px; font-weight: 800; letter-spacing: .8px; color: #fff;
}}
.id-meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 16px 0; }}
.id-meta-box {{
    background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.07);
    border-radius: 12px; padding: 11px 13px;
}}
.id-section {{
    background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.06);
    border-radius: 12px; padding: 13px 15px;
}}
.check-item {{ display: flex; align-items: center; gap: 8px; font-size: 12.5px; color: var(--muted); padding: 5px 0; }}

/* Page 2: Ticket Elements */
.ticket-head {{ border-left: 4px solid var(--primary); padding-left: 12px; margin-top: 10px; }}
.ddl-pill {{ background: rgba(16, 185, 129, .14); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, .35); padding: 3px 10px; border-radius: 8px; font-size: 11px; font-weight: 700; }}

.name {{ font-size: 15.5px; font-weight: 700; line-height: 1.3; }}
.sub {{ font-size: 12px; color: var(--muted); line-height: 1.45; }}
.row {{ display: flex; align-items: center; gap: 12px; }}
.row.between {{ justify-content: space-between; }}
.status-on {{ margin-top: 10px; font-size: 12px; color: var(--success); font-weight: 600; }}
.empty-box {{ text-align: center; padding: 34px 22px; border: 1.5px dashed rgba(148, 163, 184, .28); border-radius: 14px; background: rgba(255,255,255,.018); }}
.empty-icon {{ font-size: 36px; margin-bottom: 10px; }}
.empty-title {{ font-size: 15.5px; font-weight: 700; margin-bottom: 6px; color: var(--ink); }}
.empty-desc {{ font-size: 12.5px; color: var(--muted); max-width: 38ch; margin: 0 auto; line-height: 1.55; }}
</style>""")

# ==============================================================================
# HALAMAN 1: PROFIL SAYA (Tema Indigo-Violet • Layout Studio & Digital ID Pass)
# ==============================================================================
if "Profil Saya" in page:
    filled = sum(bool(prof[k]) for k in ("name", "campus", "major", "skills", "availability", "portfolio"))
    pct = int(filled / 6 * 100)
    hero(
        "Atur Profil Kolaborasimu",
        "Bangun kartu identitas akademik & keahlianmu untuk mempermudah pencocokan tim.",
        f'<div class="hero-stat"><div class="sub" style="color:#E2E8F0">Kelengkapan Profil</div><div style="font-size:20px;font-weight:800;margin:2px 0">{pct}% Lengkap</div><div class="bar-track" style="margin:6px 0 0"><span class="bar-fill" style="width:{pct}%"></span></div></div>'
    )
    col_form, col_prev = st.columns([1.15, 0.85], gap="medium")

    with col_form, st.form("profile_form"):
        st.markdown("#### 📝 Studio Data Diri & Keahlian")
        name = st.text_input("Nama Lengkap*", value=prof["name"], placeholder="Contoh: Farraj Bagas")
        c1, c2, c3 = st.columns([1.25, 1.25, 0.8], gap="small")
        campus = c1.text_input("Kampus / Universitas", value=prof["campus"], placeholder="Universitas Indonesia")
        major = c2.text_input("Jurusan", value=prof["major"], placeholder="Ilmu Komputer")
        year = c3.number_input("Angkatan", 2015, 2030, prof["year"])

        skills = st.multiselect("Skill Utama*", SKILL_OPTS, default=prof["skills"])
        level = st.select_slider("Level Pengalaman", ["Pemula", "Menengah", "Mahir"], value=prof["level"])
        c4, c5 = st.columns(2, gap="small")
        portfolio = c4.text_input("Tautan Portofolio / GitHub", value=prof["portfolio"], placeholder="https://github.com/username")
        avail = c5.text_input("Ketersediaan Waktu", value=prof["availability"], placeholder="Weekday malam & weekend")

        if st.form_submit_button("💾 Simpan & Perbarui Kartu ID", width="stretch", type="primary"):
            if not name.strip() or not skills:
                st.error("Nama lengkap dan minimal 1 skill wajib diisi.")
            else:
                st.session_state.user_profile = {
                    "name": name.strip(), "major": major.strip(), "year": year, "campus": campus.strip(),
                    "skills": skills, "level": level, "availability": avail.strip(), "portfolio": portfolio.strip()
                }
                st.toast("Kartu profil berhasil diperbarui!", icon="🎉")
                st.rerun()

    with col_prev:
        if prof["name"]:
            avail_val = esc(prof["availability"]) if prof["availability"] else "Fleksibel / Belum diatur"
            port_btn = f'<a class="btn-link" href="{esc(safe_url(prof["portfolio"]))}" target="_blank">🌐 Buka Portofolio</a>' if prof["portfolio"] else ""
            html(f"""
                <div class="ui-card">
                    <div class="card-title">🪪 Preview Kartu ID Pass</div>
                    <div class="id-header">
                        <span>✦ STUDENT COLLAB PASS</span>
                        <span>ANGKATAN {prof['year']}</span>
                    </div>
                    <div class="row" style="gap:14px">
                        {avatar(prof['name'], 54)}
                        <div>
                            <div class="name" style="font-size:18px">{esc(prof['name'])}</div>
                            <div class="sub" style="margin-top:2px">{esc(prof['major'] or 'Jurusan belum diisi')}</div>
                            <div class="sub">🏛️ {esc(prof['campus'] or 'Kampus belum diisi')}</div>
                        </div>
                    </div>
                    <div class="id-meta-grid">
                        <div class="id-meta-box">
                            <div class="sub" style="font-size:11px">Level Pengalaman</div>
                            <div style="font-size:13.5px;font-weight:700;color:#C4B5FD;margin-top:3px">⚡ {esc(prof['level'])}</div>
                        </div>
                        <div class="id-meta-box">
                            <div class="sub" style="font-size:11px">Ketersediaan Waktu</div>
                            <div style="font-size:13px;font-weight:600;margin-top:3px">⏱️ {avail_val}</div>
                        </div>
                    </div>
                    <div class="id-section">
                        <div class="sub" style="font-size:11.5px;margin-bottom:8px">Keahlian Utama ({len(prof['skills'])} Skill)</div>
                        <div>{badges(prof['skills'])}</div>
                    </div>
                    {port_btn}
                </div>
            """)
        else:
            html("""
                <div class="ui-card">
                    <div class="card-title">🪪 Preview Kartu ID Pass</div>
                    <div class="empty-box" style="margin-bottom:16px">
                        <div class="empty-icon">🪪</div>
                        <div class="empty-title">ID Pass Belum Aktif</div>
                        <div class="empty-desc">Lengkapi data di sebelah kiri lalu klik simpan untuk mencetak kartu kolaborasimu.</div>
                    </div>
                    <div class="id-section">
                        <div style="font-size:12px;font-weight:700;color:var(--ink);margin-bottom:6px">Syarat Aktivasi Kartu:</div>
                        <div class="check-item"><span>⭕</span><span>Isi <b>Nama Lengkap</b> kamu</span></div>
                        <div class="check-item"><span>⭕</span><span>Pilih minimal <b>1 Skill Utama</b></span></div>
                        <div class="check-item"><span>✨</span><span>Kampus & Portofolio (Opsional)</span></div>
                    </div>
                </div>
            """)

# ==============================================================================
# HALAMAN 2: EKSPLORASI LOMBA (Tema Cyan-Emerald • Layout Arena & Event Ticket)
# ==============================================================================
elif "Eksplorasi Lomba" in page:
    comps = st.session_state.competitions
    active_cats = len({c["category"] for c in comps})
    hero(
        "Arena Lomba & Kompetisi",
        "Temukan ajang kompetisi mahasiswa terbaik atau tambahkan target lomba timmu.",
        f'<div class="hero-stat"><div class="sub" style="color:#CCFBF1">Status Arena</div><div style="font-size:20px;font-weight:800;margin-top:2px">{len(comps)} Lomba • {active_cats} Bidang</div></div>'
    )

    c1, c2, c3 = st.columns([2, 1, 1], gap="small")
    q = c1.text_input("Cari", placeholder="🔍 Ketik nama lomba atau penyelenggara...", label_visibility="collapsed").strip().lower()
    cat_f = c2.selectbox("Kategori", ["Semua Kategori", *CAT_OPTS], label_visibility="collapsed")
    sort_f = c3.selectbox("Urutan", ["Deadline Terdekat", "Nama (A-Z)", "Terbaru Ditambahkan"], label_visibility="collapsed")

    with st.expander("➕ Daftarkan Lomba Baru ke Arena"):
        with st.form("add_comp", clear_on_submit=True):
            f1, f2 = st.columns(2, gap="small")
            title = f1.text_input("Nama Kompetisi*", placeholder="Contoh: Gemastik 2026")
            cat = f1.selectbox("Kategori Bidang", CAT_OPTS)
            org = f2.text_input("Penyelenggara", placeholder="Contoh: Puspresnas")
            ddl = f2.date_input("Batas Pendaftaran")
            if st.form_submit_button("🚀 Tambahkan ke Daftar Lomba", width="stretch", type="primary"):
                if title.strip():
                    comps.append({"title": title.strip(), "category": cat, "organizer": org.strip() or "-", "deadline": str(ddl)})
                    st.toast("Kompetisi berhasil ditambahkan!", icon="🏆")
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
        empty_box("🎯", "Belum Ada Lomba yang Sesuai", "Buka panel 'Daftarkan Lomba Baru' di atas atau ubah filter pencarianmu.")
    else:
        cols = st.columns(2, gap="medium")
        for i, comp in enumerate(filtered):
            with cols[i % 2]:
                html(f"""
                    <div class="ui-card" style="margin-bottom:14px">
                        <div class="row between">
                            <span class="skill-badge">{esc(comp['category'])}</span>
                            <span class="ddl-pill">📅 {esc(comp['deadline'])}</span>
                        </div>
                        <div class="ticket-head">
                            <div class="name" style="font-size:18px">{esc(comp['title'])}</div>
                            <div class="sub" style="margin-top:4px">🏛️ Penyelenggara: {esc(comp['organizer'])}</div>
                        </div>
                    </div>
                """)

# ==============================================================================
# HALAMAN 3: REKOMENDASI TEMAN (Tema Amber-Rose • Layout Radar Match Dashboard)
# ==============================================================================
else:
    candidates = st.session_state.candidates
    status_txt = "⚡ Radar Aktif" if prof["name"] else "⏳ Menunggu Profil"
    hero(
        "Radar Rekomendasi Rekan Tim",
        "Pencocokan cerdas berdasarkan irisan keahlian komplementer dan ketersediaan waktu.",
        f'<div class="hero-stat"><div class="sub" style="color:#FDE68A">Status Engine</div><div style="font-size:19px;font-weight:800;margin-top:2px">{status_txt}</div></div>'
    )

    if not prof["name"]:
        html("""
            <div class="ui-card" style="padding:36px 28px !important">
                <div class="empty-box" style="border-color:rgba(245,158,11,.35);background:rgba(245,158,11,.04)">
                    <div class="empty-icon">⚠️</div>
                    <div class="empty-title">Profil Kolaborasi Belum Diisi</div>
                    <div class="empty-desc">Untuk melihat rekomendasi rekan tim yang cocok, silakan isi <b>Nama Lengkap</b> dan <b>Skill Utama</b> kamu di menu <b>👤 Profil Saya</b> terlebih dahulu.</div>
                </div>
            </div>
        """)
    else:
        m1, m2, m3 = st.columns(3, gap="medium")
        m1.metric("Skill Aktif Kamu", f"{len(prof['skills'])} Keahlian")
        m2.metric("Level Pengalaman", prof["level"])
        m3.metric("Kandidat Ditemukan", f"{len(candidates)} Rekan")

        if not candidates:
            empty_box("🔍", "Belum Ada Kandidat di Radar", "Daftar rekomendasi rekan tim akan otomatis tampil di sini saat data kandidat tersedia.")
        else:
            tab_cards, tab_table = st.tabs(["🎴 Kartu Radar Kandidat", "📊 Tabel Perbandingan"])
            with tab_cards:
                cols = st.columns(3, gap="medium")
                for i, c in enumerate(candidates):
                    avail_txt = c.get("availability") or c.get("avail", "-")
                    badge = "match-badge top" if c["match"] >= 90 else "match-badge"
                    contact_btn = f'<a class="btn-link" href="{esc(safe_url(c["contact"]))}" target="_blank">💬 Hubungi {esc(c["name"].split()[0])}</a>' if c.get("contact") else ""
                    with cols[i % 3]:
                        html(f"""
                            <div class="ui-card" style="margin-bottom:14px">
                                <div class="row between">
                                    <div class="row">{avatar(c['name'], 42)}<div><div class="name">{esc(c['name'])}</div><div class="sub">{esc(c['major'])}</div></div></div>
                                    <span class="{badge}">{c['match']}% cocok</span>
                                </div>
                                <div class="bar-track"><span class="bar-fill" style="width:{c['match']}%"></span></div>
                                <div class="sub" style="margin-bottom:8px">🏛️ {esc(c['campus'])}</div>
                                <div style="margin-bottom:10px">{badges(c['skills'])}</div>
                                <div class="sub">⏱️ {esc(avail_txt)}</div>
                                {contact_btn}
                            </div>
                        """)

            with tab_table:
                df = pd.DataFrame([{
                    "Nama": c["name"], "Kampus": c["campus"], "Jurusan": c["major"],
                    "Skill": ", ".join(c["skills"]), "Kecocokan": c["match"] / 100,
                    "Kontak": safe_url(c["contact"]) if c.get("contact") else ""
                } for c in candidates])
                st.dataframe(df, width="stretch", hide_index=True, column_config={
                    "Kecocokan": st.column_config.ProgressColumn("Skor Kecocokan", format="%.0f%%", min_value=0, max_value=1),
                    "Kontak": st.column_config.LinkColumn("Tautan Kontak")
                })
