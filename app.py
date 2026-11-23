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

# 2. UI Helpers
def render_html(markup: str) -> None:
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()), unsafe_allow_html=True)

def card(key: str):
    return st.container(key=f"card-{key}", border=True)

def avatar(name: str, size: int = 40, variant: str = "") -> str:
    return f'<div class="avatar {variant}" style="--s:{size}px">{esc(name[:1].upper())}</div>'

def skill_badges(skills: list) -> str:
    return "".join(f'<span class="skill-badge">{esc(s)}</span>' for s in skills)

def safe_url(url: str) -> str:
    url = url.strip()
    return url if url.startswith(("http://", "https://")) else f"https://{url}"

def hero(tag: str, title: str, subtitle: str) -> None:
    render_html(f"""
        <div class="hero-banner">
            <span class="hero-tag">{esc(tag)}</span>
            <h1 class="hero-title">{esc(title)}</h1>
            <p class="hero-subtitle">{esc(subtitle)}</p>
        </div>
    """)

def empty_box(icon: str, title: str, desc: str) -> None:
    render_html(f"""
        <div class="empty-box">
            <div class="empty-icon">{icon}</div>
            <div class="empty-title">{title}</div>
            <div class="empty-desc">{desc}</div>
        </div>
    """)

# 3. Compact CSS
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
:root {
    color-scheme: dark; --bg: #0F1020; --surface: #1B1C36; --border: #2E3055;
    --ink: #F1F5F9; --muted: #94A3B8; --primary: #6366F1; --violet: #8B5CF6;
    --cyan: #22D3EE; --gold: #FBBF24; --success: #34D399; --tint: rgba(99, 102, 241, .16);
}
html, body, .stApp, [data-testid="stMarkdownContainer"], input, textarea, button, label { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: var(--bg); color: var(--ink); }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1180px; padding-top: 1.25rem; }
[data-testid="stVerticalBlock"] { gap: .9rem !important; }
[data-testid="stMarkdownContainer"] h4 { margin: 0 !important; padding: 0 !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }
[data-testid="stSidebar"] [role="radiogroup"] label { padding: 10px 12px; border-radius: 10px; transition: .2s; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background: var(--tint); box-shadow: inset 3px 0 0 var(--primary); font-weight: 700; }

/* Hero */
.hero-banner {
    background: linear-gradient(120deg, #1E1B5E, #3730A3, #5B21B6); border-radius: 20px;
    padding: 28px 36px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,.1);
    box-shadow: 0 18px 40px -24px rgba(99, 102, 241, .6);
}
.hero-tag { display: inline-block; background: rgba(255,255,255,.14); padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; margin-bottom: 10px; }
.hero-title { font-size: clamp(22px, 3vw, 32px); font-weight: 800; margin: 0; color: #fff !important; }
.hero-subtitle { font-size: 14px; color: #CBD1FF; margin: 8px 0 0; }

/* Kartu & Form */
[class*="st-key-card-"] > [data-testid="stVerticalBlock"],
[class*="st-key-card-"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stForm"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.4rem !important;
    transition: .25s;
}
[class*="st-key-card-sidebar"] > [data-testid="stVerticalBlock"],
[class*="st-key-card-sidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(15, 16, 32, .45) !important;
    padding: 14px 16px !important;
    border-radius: 14px !important;
}
[class*="st-key-card-"] [data-testid="stMarkdownContainer"] p:last-child { margin-bottom: 0 !important; }
[class*="st-key-card-"]:not([class*="st-key-card-sidebar"]):hover > [data-testid="stVerticalBlock"] {
    transform: translateY(-3px); border-color: rgba(129, 140, 248, .55) !important;
}
[data-testid="stMetric"] {
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 14px 18px;
}
[data-testid^="stBaseButton-primary"] { background: linear-gradient(135deg, var(--primary), var(--violet)); border: none; color: #fff; font-weight: 700; }

/* Komponen Kecil */
.avatar { flex: none; width: var(--s); height: var(--s); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: calc(var(--s)*.42); background: linear-gradient(135deg, var(--primary), var(--violet)); }
.avatar.cyan { background: linear-gradient(135deg, #0891B2, #6366F1); }
.skill-badge { display: inline-block; background: var(--tint); color: #C7CCFF; border: 1px solid rgba(129,140,248,.35); padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; margin: 2px 4px 2px 0; }
.match-badge { background: rgba(52,211,153,.14); color: #6EE7B7; border: 1px solid rgba(52,211,153,.35); padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.match-badge.top { background: rgba(251,191,36,.14); color: #FCD34D; border-color: rgba(251,191,36,.4); }
.match-bar { height: 6px; border-radius: 999px; background: rgba(255,255,255,.08); overflow: hidden; margin: 10px 0 12px; }
.match-bar span { display: block; height: 100%; background: linear-gradient(90deg, var(--primary), var(--cyan)); }

.name { font-size: 15px; font-weight: 700; line-height: 1.3; }
.sub { font-size: 12px; color: var(--muted); line-height: 1.45; }
.row { display: flex; align-items: center; gap: 12px; }
.row.between { justify-content: space-between; }
.status-on { margin-top: 10px; font-size: 12px; color: var(--success); font-weight: 600; }
.empty-box { text-align: center; padding: 32px 20px; border: 2px dashed rgba(129,140,248,.35); border-radius: 14px; background: rgba(99,102,241,.05); }
.empty-icon { font-size: 38px; margin-bottom: 10px; }
.empty-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
.empty-desc { font-size: 13px; color: var(--muted); line-height: 1.45; max-width: 45ch; margin: 0 auto; }
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# 4. Sidebar
prof = st.session_state.user_profile
with st.sidebar:
    render_html('<div class="row" style="margin-bottom:16px"><span style="font-size:28px">🏆</span><div><div style="font-size:18px;font-weight:800;line-height:1.15">Cari Teman Lomba</div><div class="sub">Kelompok 17 • DDP 1 Fasilkom UI</div></div></div>')
    page = st.radio("Navigasi", ["👤 Profil Saya", "📅 Eksplorasi Lomba", "🤝 Rekomendasi Teman"], label_visibility="collapsed")
    st.divider()
    with card("sidebar"):
        if prof["name"]:
            render_html(f'<div class="row">{avatar(prof["name"], 36)}<div><div class="name" style="font-size:13px">{esc(prof["name"])}</div><div class="sub">{esc(prof["campus"] or "Mahasiswa")}</div></div></div><div class="status-on">● Profil aktif ({len(prof["skills"])} skill)</div>')
        else:
            render_html('<div style="font-size:13px;font-weight:700;color:#FBBF24;margin-bottom:4px">Profil belum lengkap</div><div class="sub">Isi nama & minimal 1 skill di Profil Saya.</div>')
    st.caption("Fasilkom UI © 2026")

# 5. Pages
if "Profil Saya" in page:
    hero("Langkah 1", "Atur Profil Kolaborasimu", "Isi data diri dan keahlianmu agar sistem bisa mencocokkanmu dengan calon rekan tim.")
    col_form, col_prev = st.columns([1.25, 0.75], gap="large")

    with col_form, st.form("profile_form"):
        st.markdown("#### 📝 Data Diri & Skill")
        name = st.text_input("Nama Lengkap*", value=prof["name"], placeholder="Contoh: Farraj Bagas")
        c1, c2 = st.columns(2)
        campus = c1.text_input("Kampus / Universitas", value=prof["campus"], placeholder="Universitas Indonesia")
        major = c2.text_input("Jurusan", value=prof["major"], placeholder="Ilmu Komputer")
        year = st.number_input("Angkatan", 2015, 2030, prof["year"])

        skill_opts = ["Python", "Machine Learning", "UI/UX", "Frontend/Web", "Business Analysis", "Finance", "Public Speaking", "Pitching", "Backend", "Cyber Security"]
        skills = st.multiselect("Skill Utama*", skill_opts, default=prof["skills"])
        level = st.select_slider("Level Pengalaman", ["Pemula", "Menengah", "Mahir"], value=prof["level"])
        portfolio = st.text_input("Tautan Portofolio / GitHub", value=prof["portfolio"], placeholder="https://github.com/username")
        avail = st.text_area("Ketersediaan Waktu", value=prof["availability"], placeholder="Weekday malam & weekend", height=70)

        if st.form_submit_button("💾 Simpan Profil", width="stretch", type="primary"):
            if not name.strip() or not skills:
                st.error("Nama lengkap dan minimal 1 skill wajib diisi.")
            else:
                st.session_state.user_profile = {
                    "name": name.strip(), "major": major.strip(), "year": year, "campus": campus.strip(),
                    "skills": skills, "level": level, "availability": avail.strip(), "portfolio": portfolio.strip()
                }
                st.toast("Profil tersimpan", icon="🎉")
                st.rerun()

    with col_prev, card("preview"):
        st.markdown("#### 🎴 Preview Kartu")
        if prof["name"]:
            render_html(f"""
                <div class="row" style="margin:4px 0 12px">{avatar(prof['name'], 48)}
                    <div><div class="name" style="font-size:17px">{esc(prof['name'])}</div>
                    <div class="sub">{esc(prof['major'] or 'Jurusan')} • {esc(prof['campus'] or 'Kampus')} ({prof['year']})</div></div>
                </div>
                <div class="sub" style="margin-bottom:6px">Level: <b style="color:var(--ink)">{esc(prof['level'])}</b></div>
                <div style="margin-bottom:10px">{skill_badges(prof['skills'])}</div>
            """)
            if prof["availability"]: st.markdown(f"⏱️ **Waktu:** {prof['availability']}")
            if prof["portfolio"]: st.link_button("🌐 Buka Portofolio", safe_url(prof["portfolio"]), width="stretch")
        else:
            empty_box("👤", "Kartu profil masih kosong", "Isi form di samping lalu simpan.")

elif "Eksplorasi Lomba" in page:
    hero("Eksplorasi", "Daftar Lomba & Kompetisi", "Jelajahi ajang kompetisi mahasiswa atau tambahkan lomba incaranmu.")
    c1, c2, c3 = st.columns([2, 1, 1])
    c1.text_input("Cari", placeholder="🔍 Cari kompetisi...", label_visibility="collapsed")
    c2.selectbox("Kategori", ["Semua Kategori", "Hackathon", "Business Case", "UI/UX Design", "Data Science", "Competitive Programming"], label_visibility="collapsed")
    c3.selectbox("Urutan", ["Deadline Terdekat", "Terbaru", "Paling Populer"], label_visibility="collapsed")

    with st.expander("➕ Tambah Lomba Baru"):
        with st.form("add_comp"):
            col1, col2 = st.columns(2)
            title = col1.text_input("Nama Kompetisi", placeholder="Gemastik 2026")
            cat = col1.selectbox("Kategori", ["Hackathon", "Business Case", "UI/UX Design", "Data Science", "Competitive Programming"])
            org = col2.text_input("Penyelenggara", placeholder="Puspresnas")
            ddl = col2.date_input("Batas Pendaftaran")
            if st.form_submit_button("Tambah Lomba", width="stretch"):
                if title.strip():
                    st.session_state.competitions.append({"title": title.strip(), "category": cat, "organizer": org.strip() or "-", "deadline": str(ddl)})
                    st.toast("Lomba ditambahkan", icon="✅")
                    st.rerun()
                else:
                    st.warning("Nama kompetisi wajib diisi.")

    if not st.session_state.competitions:
        empty_box("🎯", "Belum ada lomba", "Buka 'Tambah Lomba Baru' di atas untuk memasukkan lomba pertamamu.")
    else:
        cols = st.columns(2)
        for i, comp in enumerate(st.session_state.competitions):
            with cols[i % 2], card(f"comp-{i}"):
                render_html(f"""
                    <span class="skill-badge">{esc(comp['category'])}</span>
                    <div class="name" style="font-size:17px;margin-top:8px">{esc(comp['title'])}</div>
                    <div class="sub">Penyelenggara: {esc(comp['organizer'])}</div>
                    <div style="margin-top:12px;font-size:13px">📅 <b>Deadline:</b> {esc(comp['deadline'])}</div>
                """)

else:
    hero("Smart Matching", "Rekomendasi Rekan Tim", "Profilmu dicocokkan dengan kandidat berdasarkan keahlian yang saling melengkapi.")
    candidates = st.session_state.candidates

    if not prof["name"]:
        empty_box("⚠️", "Profilmu belum diisi", "Isi nama dan skill utama di menu <b>Profil Saya</b> dulu.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Skill Utama", f"{len(prof['skills'])} Skill")
        m2.metric("Level", prof["level"])
        m3.metric("Kandidat Cocok", f"{len(candidates)} Rekan")

        if not candidates:
            empty_box("🔍", "Belum ada kandidat rekan tim", "Data kandidat masih kosong. Daftar rekomendasi akan muncul di sini setelah ada data peserta.")
        else:
            tab_cards, tab_table = st.tabs(["🎴 Kartu", "📊 Tabel"])
            with tab_cards:
                for col, c in zip(st.columns(len(candidates)), candidates):
                    with col, card(f"cand-{c['name']}"):
                        badge = "match-badge top" if c["match"] >= 90 else "match-badge"
                        render_html(f"""
                            <div class="row between">
                                <div class="row">{avatar(c['name'], 40, 'cyan')}<div><div class="name">{esc(c['name'])}</div><div class="sub">{esc(c['major'])}</div></div></div>
                                <span class="{badge}">{c['match']}% cocok</span>
                            </div>
                            <div class="match-bar"><span style="width:{c['match']}%"></span></div>
                            <div class="sub" style="margin-bottom:8px">🏛️ {esc(c['campus'])}</div>
                            <div style="margin-bottom:10px">{skill_badges(c['skills'])}</div>
                            <div class="sub" style="margin-bottom:12px">⏱️ {esc(c['avail'])}</div>
                        """)
                        st.link_button(f"💬 Hubungi {c['name'].split()[0]}", c["contact"], width="stretch")

            with tab_table:
                df = pd.DataFrame([{"Nama": c["name"], "Kampus": c["campus"], "Jurusan": c["major"], "Skill": ", ".join(c["skills"]), "Kecocokan": c["match"]/100, "Kontak": c["contact"]} for c in candidates])
                st.dataframe(df, width="stretch", hide_index=True, column_config={
                    "Kecocokan": st.column_config.ProgressColumn("Skor Kecocokan", format="%.0f%%", min_value=0, max_value=1),
                    "Kontak": st.column_config.LinkColumn("Tautan Kontak")
                })