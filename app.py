from html import escape as esc
from pathlib import Path

import pandas as pd
import streamlit as st
import tomllib

BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "settings.toml", "rb") as f:
    cfg = tomllib.load(f)

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title=cfg["title"],
    page_icon=cfg["icon"],
    layout=cfg["default_layout"],
    initial_sidebar_state=cfg["default_sidebar_state"],
)

# 2. Inisialisasi Session State
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "",
        "major": "",
        "year": 2026,
        "campus": "",
        "skills": [],
        "level": "Menengah",
        "availability": "",
        "portfolio": "",
    }

if "competitions" not in st.session_state:
    st.session_state.competitions = []


# 3. Helper kecil supaya HTML rapi dan aman
def render_html(markup: str) -> None:
    """Render HTML. Baris dirapatkan agar Markdown tidak menganggapnya code-block."""
    flat = " ".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(flat, unsafe_allow_html=True)


def avatar(name: str, size: int = 40, variant: str = "") -> str:
    return (
        f'<div class="avatar {variant}" style="--s:{size}px">'
        f"{esc(name[:1].upper())}</div>"
    )


def skill_badges(skills: list) -> str:
    return "".join(f'<span class="skill-badge">{esc(s)}</span>' for s in skills)


def safe_url(url: str) -> str:
    url = url.strip()
    return url if url.startswith(("http://", "https://")) else f"https://{url}"


def hero(tag: str, title: str, subtitle: str) -> None:
    render_html(
        f"""
        <div class="hero-banner">
            <span class="hero-tag">{esc(tag)}</span>
            <h1 class="hero-title">{esc(title)}</h1>
            <p class="hero-subtitle">{esc(subtitle)}</p>
        </div>
        """
    )


# 4. CSS: tema gelap, responsif, animasi
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    color-scheme: dark;
    --bg: #0F1020;
    --surface: #1B1C36;
    --border: #2E3055;
    --ink: #F1F5F9;
    --muted: #94A3B8;
    --primary: #6366F1;
    --violet: #8B5CF6;
    --cyan: #22D3EE;
    --gold: #FBBF24;
    --success: #34D399;
    --tint: rgba(99, 102, 241, .16);
    --ease: cubic-bezier(.22, 1, .36, 1);
}

html, body, .stApp,
[data-testid="stMarkdownContainer"], input, textarea, button, label {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.stApp { background: var(--bg); color: var(--ink); }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1180px; padding-top: 1.25rem; padding-bottom: 3rem; }

/* ---------- Ritme spasi (satu skala, biar rapi) ---------- */
[data-testid="stVerticalBlock"] { gap: .9rem !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .75rem !important; }
[data-testid="stSidebarUserContent"] { padding-top: .5rem; }
hr { margin: .75rem 0 !important; }
[data-testid="stMarkdownContainer"] h4 { margin: 0 !important; padding: .25rem 0 !important; }
[data-testid="stWidgetLabel"] { margin-bottom: .25rem; }
[data-testid="stForm"] { padding: 1.25rem; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }
[data-testid="stSidebar"] [role="radiogroup"] { gap: 4px; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    width: 100%;
    padding: 10px 12px;
    border-radius: 10px;
    transition: background .25s var(--ease), box-shadow .25s var(--ease), padding-left .25s var(--ease);
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: var(--tint); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: var(--tint);
    box-shadow: inset 3px 0 0 var(--primary);
    padding-left: 16px;
    font-weight: 700;
}

/* ---------- Hero ---------- */
.hero-banner {
    position: relative;
    overflow: hidden;
    color: #fff;
    border-radius: 20px;
    padding: clamp(20px, 3.5vw, 32px) clamp(20px, 4vw, 40px);
    margin-bottom: 20px;
    background: linear-gradient(120deg, #1E1B5E, #3730A3, #5B21B6, #1E1B5E);
    background-size: 300% 300%;
    animation: gradientShift 18s ease infinite;
    border: 1px solid rgba(255, 255, 255, .1);
    box-shadow: 0 18px 40px -24px rgba(99, 102, 241, .6);
}
.hero-banner::after {
    content: "";
    position: absolute;
    right: -70px; top: -100px;
    width: 280px; height: 280px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(251, 191, 36, .35), transparent 68%);
    animation: drift 9s ease-in-out infinite;
    pointer-events: none;
}
.hero-tag {
    display: inline-block;
    background: rgba(255, 255, 255, .14);
    border: 1px solid rgba(255, 255, 255, .25);
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 10px;
}
.hero-banner .hero-title {
    font-size: clamp(22px, 3.2vw, 32px);
    font-weight: 800;
    line-height: 1.15;
    margin: 0;
    padding: 0;
    color: #fff !important;
}
.hero-banner .hero-subtitle {
    font-size: clamp(13px, 1.6vw, 15px);
    color: #CBD1FF;
    margin: 8px 0 0;
    max-width: 62ch;
}

/* ---------- Kartu & container ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 12px 30px -22px rgba(0, 0, 0, .8);
    animation: riseIn .55s var(--ease) backwards;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] { animation: none; box-shadow: none; background: transparent; }
[data-testid="stColumn"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] { animation-delay: .08s; }
[data-testid="stColumn"]:nth-child(3) [data-testid="stVerticalBlockBorderWrapper"] { animation-delay: .16s; }

[data-testid="stForm"] { border: 1px solid var(--border); border-radius: 16px; background: var(--surface); }

[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px 18px;
}

/* ---------- Input ---------- */
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
    border-radius: 10px !important;
    transition: box-shadow .2s var(--ease), border-color .2s var(--ease);
}
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within,
[data-baseweb="select"] > div:focus-within {
    box-shadow: 0 0 0 3px rgba(99, 102, 241, .3);
    border-color: var(--primary) !important;
}

/* ---------- Tombol ---------- */
[data-testid^="stBaseButton"], [data-testid^="stBaseLinkButton"] {
    border-radius: 10px;
    font-weight: 700;
    transition: transform .18s var(--ease), box-shadow .25s var(--ease), border-color .2s, background .2s;
}
[data-testid^="stBaseButton-secondary"], [data-testid^="stBaseLinkButton"] {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--ink);
}
[data-testid^="stBaseButton-primary"] {
    background: linear-gradient(135deg, var(--primary), var(--violet));
    border: none;
    color: #fff;
    box-shadow: 0 10px 22px -12px rgba(99, 102, 241, .9);
}
[data-testid^="stBaseButton"]:hover, [data-testid^="stBaseLinkButton"]:hover {
    transform: translateY(-2px);
    border-color: var(--primary);
}
[data-testid^="stBaseButton-primary"]:hover { box-shadow: 0 16px 28px -12px rgba(99, 102, 241, 1); }
[data-testid^="stBaseButton"]:active, [data-testid^="stBaseLinkButton"]:active { transform: scale(.97); }

/* ---------- Tab ---------- */
[data-baseweb="tab"] { transition: background .2s var(--ease), color .2s; border-radius: 10px 10px 0 0; }
[data-baseweb="tab"]:hover { background: var(--tint); }

/* ---------- Avatar, badge, bar ---------- */
.avatar {
    flex: none;
    width: var(--s, 40px);
    height: var(--s, 40px);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: 700;
    font-size: calc(var(--s, 40px) * .42);
    background: linear-gradient(135deg, var(--primary), var(--violet));
}
.avatar.cyan { background: linear-gradient(135deg, #0891B2, #6366F1); }

.skill-badge {
    display: inline-block;
    background: var(--tint);
    color: #C7CCFF;
    border: 1px solid rgba(129, 140, 248, .35);
    padding: 4px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    margin: 3px 5px 3px 0;
}
.match-badge {
    flex: none;
    display: inline-block;
    background: rgba(52, 211, 153, .14);
    color: #6EE7B7;
    border: 1px solid rgba(52, 211, 153, .35);
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}
.match-badge.top { background: rgba(251, 191, 36, .14); color: #FCD34D; border-color: rgba(251, 191, 36, .4); }

.match-bar { height: 6px; border-radius: 999px; background: rgba(255, 255, 255, .08); overflow: hidden; margin: 10px 0 12px; }
.match-bar span {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, var(--primary), var(--cyan));
    transform-origin: left;
    animation: grow 1.1s var(--ease) .25s both;
}

.name { font-size: 15px; font-weight: 700; line-height: 1.25; }
.sub { font-size: 12px; color: var(--muted); }
.row { display: flex; align-items: center; gap: 12px; }
.row.between { justify-content: space-between; align-items: flex-start; }
.status-on { margin-top: 10px; font-size: 12px; color: var(--success); font-weight: 600; }
.status-on::before {
    content: "";
    display: inline-block;
    width: 8px; height: 8px;
    margin-right: 6px;
    border-radius: 50%;
    background: var(--success);
    animation: pulse 2s ease-out infinite;
}

/* ---------- Empty state ---------- */
.empty-box {
    text-align: center;
    padding: 40px 24px;
    border: 2px dashed rgba(129, 140, 248, .35);
    border-radius: 16px;
    background: rgba(99, 102, 241, .05);
    margin: 4px 0;
}
.empty-icon { font-size: 44px; margin-bottom: 10px; display: inline-block; animation: drift 5s ease-in-out infinite; }
.empty-title { font-size: 17px; font-weight: 700; margin-bottom: 6px; }
.empty-desc { font-size: 13px; color: var(--muted); max-width: 46ch; margin: 0 auto; }

/* ---------- Animasi ---------- */
@keyframes riseIn { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes drift { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(-14px, 10px); } }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(52, 211, 153, .5); } 100% { box-shadow: 0 0 0 9px rgba(52, 211, 153, 0); } }
@keyframes pageIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }

/* ---------- Fluid: transisi halaman, grid menyesuaikan lebar, hover halus ---------- */
html { scroll-behavior: smooth; }

[class*="st-key-page-"] { animation: pageIn .5s var(--ease) backwards; }
[data-baseweb="tab-panel"] { animation: pageIn .35s var(--ease) backwards; }

[class*="st-key-grid-"] [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: 1rem; }
[class*="st-key-grid-"] [data-testid="stColumn"] {
    flex: 1 1 260px !important;
    width: auto !important;
    min-width: min(100%, 260px) !important;
}

[class*="st-key-grid-"] [data-testid="stVerticalBlockBorderWrapper"] {
    transition: transform .3s var(--ease), box-shadow .3s var(--ease), border-color .3s var(--ease);
}
[class*="st-key-grid-"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-4px);
    border-color: rgba(129, 140, 248, .55);
    box-shadow: 0 22px 40px -24px rgba(99, 102, 241, .6);
}

/* ---------- Layar kecil ---------- */
@media (max-width: 640px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    .hero-banner { border-radius: 16px; margin-bottom: 16px; }
}

/* ---------- Hormati pengguna yang mematikan animasi ---------- */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# --- SIDEBAR ---
with st.sidebar:
    render_html(
        """
        <div class="row" style="margin-bottom: 18px;">
            <span style="font-size: 30px;">🏆</span>
            <div>
                <div style="font-size: 18px; font-weight: 800; line-height: 1.1;">Cari Teman Lomba</div>
                <div class="sub">Kelompok 17 • DDP 1 Fasilkom UI</div>
            </div>
        </div>
        """
    )

    page = st.radio(
        "Menu Navigasi",
        ["👤 Profil Saya", "📅 Eksplorasi Lomba", "🤝 Rekomendasi Teman"],
        label_visibility="collapsed",
    )

    st.divider()

    profile = st.session_state.user_profile
    with st.container(border=True):
        if profile["name"]:
            render_html(
                f"""
                <div class="row">
                    {avatar(profile['name'], 36)}
                    <div style="overflow: hidden;">
                        <div class="name" style="font-size: 13px; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{esc(profile['name'])}</div>
                        <div class="sub">{esc(profile['campus'] or 'Mahasiswa')}</div>
                    </div>
                </div>
                <div class="status-on">Profil aktif ({len(profile['skills'])} skill)</div>
                """
            )
        else:
            render_html(
                """
                <div style="font-size: 13px; font-weight: 700; color: #FBBF24; margin-bottom: 4px;">Profil belum lengkap</div>
                <div class="sub">Isi nama dan minimal 1 skill di menu Profil Saya supaya rekomendasi tim muncul.</div>
                """
            )

    st.caption("Fasilkom UI © 2026")


slug = "profil" if "Profil Saya" in page else "lomba" if "Eksplorasi Lomba" in page else "reco"

with st.container(key=f"page-{slug}"):
    # ========================================================
    # --- HALAMAN 1: PROFIL ---
    # ========================================================
    if "Profil Saya" in page:
        hero(
            "Langkah 1",
            "Atur Profil Kolaborasimu",
            "Isi data diri dan keahlianmu agar sistem bisa mencocokkanmu dengan calon rekan tim.",
        )

        col_form, col_preview = st.columns([1.25, 0.75], gap="large")

        with col_form:
            with st.form("profile_form"):
                st.markdown("#### 📝 Data Diri & Akademik")
                name = st.text_input("Nama Lengkap*", value=st.session_state.user_profile["name"], placeholder="Contoh: Farraj Bagas")

                c_camp, c_maj = st.columns(2)
                with c_camp:
                    campus = st.text_input("Kampus / Universitas", value=st.session_state.user_profile["campus"], placeholder="Contoh: Universitas Indonesia")
                with c_maj:
                    major = st.text_input("Jurusan", value=st.session_state.user_profile["major"], placeholder="Contoh: Ilmu Komputer")

                year = st.number_input("Angkatan", min_value=2015, max_value=2030, value=st.session_state.user_profile["year"])

                st.divider()
                st.markdown("#### ⚡ Skill & Pengalaman")

                skill_options = ["Python", "Machine Learning", "UI/UX", "Frontend/Web", "Business Analysis", "Finance", "Public Speaking", "Pitching", "Backend", "Cyber Security"]
                skills = st.multiselect("Skill Utama*", skill_options, default=st.session_state.user_profile["skills"], help="Pilih minimal 1 skill yang kamu kuasai")

                level_options = ["Pemula", "Menengah", "Mahir"]
                level = st.select_slider("Level Pengalaman Skill", options=level_options, value=st.session_state.user_profile["level"])

                portfolio = st.text_input("Tautan Portofolio / LinkedIn / GitHub (Opsional)", value=st.session_state.user_profile["portfolio"], placeholder="https://github.com/username")
                availability = st.text_area("Ketersediaan Waktu", value=st.session_state.user_profile["availability"], placeholder="Contoh: Aktif di weekday malam & weekend full", height=75)

                submitted = st.form_submit_button("💾 Simpan Profil", width="stretch", type="primary")

                if submitted:
                    if not name.strip() or not skills:
                        st.error("Nama lengkap dan minimal 1 skill utama wajib diisi.")
                    else:
                        st.session_state.user_profile = {
                            "name": name.strip(),
                            "major": major.strip(),
                            "year": year,
                            "campus": campus.strip(),
                            "skills": skills,
                            "level": level,
                            "availability": availability.strip(),
                            "portfolio": portfolio.strip(),
                        }
                        st.toast("Profil tersimpan", icon="🎉")
                        st.rerun()

        with col_preview:
            prof = st.session_state.user_profile
            with st.container(border=True):
                st.markdown("#### 🎴 Preview Kartu Profil")
                st.caption("Kartu ini yang akan dilihat calon rekan tim:")
                if prof["name"]:
                    render_html(
                        f"""
                        <div class="row" style="margin-bottom: 14px;">
                            {avatar(prof['name'], 48)}
                            <div>
                                <div class="name" style="font-size: 17px;">{esc(prof['name'])}</div>
                                <div class="sub">{esc(prof['major'] or 'Jurusan')} • {esc(prof['campus'] or 'Kampus')} ({prof['year']})</div>
                            </div>
                        </div>
                        <div class="sub" style="margin-bottom: 6px;">Level skill: <b style="color: var(--ink);">{esc(prof['level'])}</b></div>
                        <div style="margin-bottom: 10px;">{skill_badges(prof['skills'])}</div>
                        """
                    )
                    if prof["availability"]:
                        st.markdown(f"⏱️ **Waktu:** {prof['availability']}")
                    if prof["portfolio"]:
                        st.link_button("🌐 Buka Portofolio", safe_url(prof["portfolio"]), width="stretch")
                else:
                    render_html(
                        """
                        <div class="empty-box" style="padding: 32px 14px; margin: 0;">
                            <div class="empty-icon" style="font-size: 36px;">👤</div>
                            <div class="empty-title" style="font-size: 15px;">Kartu profil masih kosong</div>
                            <div class="empty-desc">Isi form di samping lalu simpan, kartumu langsung muncul di sini.</div>
                        </div>
                        """
                    )

    # ========================================================
    # --- HALAMAN 2: DAFTAR LOMBA ---
    # ========================================================
    elif "Eksplorasi Lomba" in page:
        hero(
            "Eksplorasi",
            "Daftar Lomba & Kompetisi",
            "Jelajahi ajang kompetisi mahasiswa atau tambahkan lomba yang ingin kamu ikuti.",
        )

        c_search, c_cat, c_sort = st.columns([2, 1, 1])
        with c_search:
            st.text_input("Cari Lomba", placeholder="🔍 Ketik nama kompetisi atau kata kunci...", label_visibility="collapsed")
        with c_cat:
            st.selectbox("Kategori", ["Semua Kategori", "Hackathon", "Business Case", "UI/UX Design", "Data Science", "Competitive Programming"], label_visibility="collapsed")
        with c_sort:
            st.selectbox("Urutan", ["Deadline Terdekat", "Terbaru", "Paling Populer"], label_visibility="collapsed")

        with st.expander("➕ Tambah Lomba Baru (uji coba tampilan)"):
            with st.form("add_competition_form"):
                c1, c2 = st.columns(2)
                with c1:
                    new_title = st.text_input("Nama Kompetisi", placeholder="Contoh: Gemastik 2026")
                    new_category = st.selectbox("Kategori Bidang", ["Hackathon", "Business Case", "UI/UX Design", "Data Science", "Competitive Programming"])
                with c2:
                    new_organizer = st.text_input("Penyelenggara", placeholder="Contoh: Puspresnas / Kemdikbud")
                    new_deadline = st.date_input("Batas Pendaftaran")

                btn_add = st.form_submit_button("Tambah Lomba", width="stretch")
                if btn_add:
                    if new_title.strip():
                        st.session_state.competitions.append(
                            {
                                "title": new_title.strip(),
                                "category": new_category,
                                "organizer": new_organizer.strip() or "-",
                                "deadline": str(new_deadline),
                            }
                        )
                        st.toast("Lomba ditambahkan", icon="✅")
                        st.rerun()
                    else:
                        st.warning("Nama kompetisi wajib diisi.")

        if not st.session_state.competitions:
            render_html(
                """
                <div class="empty-box">
                    <div class="empty-icon">🎯</div>
                    <div class="empty-title">Belum ada lomba</div>
                    <div class="empty-desc">Buka "Tambah Lomba Baru" di atas untuk memasukkan lomba pertamamu, kartunya langsung tampil di sini.</div>
                </div>
                """
            )
        else:
            cols = st.container(key="grid-lomba").columns(2)
            for i, comp in enumerate(st.session_state.competitions):
                with cols[i % 2]:
                    with st.container(border=True):
                        render_html(
                            f"""
                            <span class="skill-badge">{esc(comp['category'])}</span>
                            <div class="name" style="font-size: 17px; margin-top: 6px;">{esc(comp['title'])}</div>
                            <div class="sub">Penyelenggara: {esc(comp['organizer'])}</div>
                            <div style="margin-top: 12px; font-size: 13px;">📅 <b>Deadline:</b> {esc(comp['deadline'])}</div>
                            """
                        )

    # ========================================================
    # --- HALAMAN 3: REKOMENDASI TEMAN ---
    # ========================================================
    else:
        hero(
            "Smart Matching",
            "Rekomendasi Rekan Tim",
            "Profilmu dicocokkan dengan kandidat berdasarkan keahlian yang saling melengkapi.",
        )

        profile = st.session_state.user_profile

        if not profile["name"]:
            render_html(
                """
                <div class="empty-box">
                    <div class="empty-icon">⚠️</div>
                    <div class="empty-title">Profilmu belum diisi</div>
                    <div class="empty-desc">Isi nama dan skill utama di menu <b>Profil Saya</b> dulu, lalu rekomendasi rekan tim muncul di sini.</div>
                </div>
                """
            )
        else:
            m1, m2, m3 = st.container(key="grid-metrics").columns(3)
            with m1:
                st.metric("Skill Utama Kamu", f"{len(profile['skills'])} Skill")
            with m2:
                st.metric("Level Pengalaman", profile["level"])
            with m3:
                st.metric("Kandidat Cocok", "3 Rekan")

            st.markdown("<br>", unsafe_allow_html=True)

            tab_cards, tab_table = st.tabs(["🎴 Kartu", "📊 Tabel"])

            candidates = [
                {
                    "name": "Ani Wijaya",
                    "campus": "Universitas Indonesia",
                    "major": "Sistem Informasi",
                    "skills": ["UI/UX", "Public Speaking", "Pitching"],
                    "match": 92,
                    "availability": "Weekday malam & Weekend",
                    "contact": "https://t.me/aniwijaya",
                },
                {
                    "name": "Budi Pratama",
                    "campus": "Institut Teknologi Bandung",
                    "major": "Manajemen Bisnis",
                    "skills": ["Business Analysis", "Finance", "Pitching"],
                    "match": 85,
                    "availability": "Fleksibel setiap hari",
                    "contact": "https://linkedin.com",
                },
                {
                    "name": "Citra Lestari",
                    "campus": "Universitas Gadjah Mada",
                    "major": "Ilmu Komputer",
                    "skills": ["Frontend/Web", "Python", "Machine Learning"],
                    "match": 78,
                    "availability": "Weekend full",
                    "contact": "https://github.com",
                },
            ]

            with tab_cards:
                cols = st.container(key="grid-reco").columns(len(candidates))
                for col, cand in zip(cols, candidates):
                    with col:
                        with st.container(border=True):
                            badge_class = "match-badge top" if cand["match"] >= 90 else "match-badge"
                            render_html(
                                f"""
                                <div class="row between">
                                    <div class="row">
                                        {avatar(cand['name'], 40, 'cyan')}
                                        <div>
                                            <div class="name">{esc(cand['name'])}</div>
                                            <div class="sub">{esc(cand['major'])}</div>
                                        </div>
                                    </div>
                                    <span class="{badge_class}">{cand['match']}% cocok</span>
                                </div>
                                <div class="match-bar"><span style="width: {cand['match']}%"></span></div>
                                <div class="sub" style="margin-bottom: 8px;">🏛️ {esc(cand['campus'])}</div>
                                <div class="sub" style="margin-bottom: 4px;">Skill yang melengkapi:</div>
                                <div style="margin-bottom: 10px;">{skill_badges(cand['skills'])}</div>
                                <div class="sub" style="margin-bottom: 12px;">⏱️ {esc(cand['availability'])}</div>
                                """
                            )
                            st.link_button(f"💬 Hubungi {cand['name'].split()[0]}", cand["contact"], width="stretch")

            with tab_table:
                df_rekomendasi = pd.DataFrame(
                    [
                        {
                            "Nama": c["name"],
                            "Kampus": c["campus"],
                            "Jurusan": c["major"],
                            "Skill": ", ".join(c["skills"]),
                            "Kecocokan": c["match"] / 100.0,
                            "Kontak": c["contact"],
                        }
                        for c in candidates
                    ]
                )

                st.dataframe(
                    df_rekomendasi,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Kecocokan": st.column_config.ProgressColumn(
                            "Skor Kecocokan",
                            help="Dihitung dari kesesuaian skill yang saling melengkapi",
                            format="%.0f%%",
                            min_value=0,
                            max_value=1,
                        ),
                        "Kontak": st.column_config.LinkColumn("Tautan Kontak"),
                    },
                )