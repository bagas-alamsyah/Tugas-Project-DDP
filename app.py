from pathlib import Path

import streamlit as st
import pandas as pd

import tomllib

BASE_DIR = Path(__file__).parent

with open(BASE_DIR / 'config' / "settings.toml", "rb") as f:
    cfg = tomllib.load(f)

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title=cfg['title'],
    page_icon=cfg['icon'],
    layout=cfg['default_layout'],
    initial_sidebar_state=cfg['default_sidebar_state']
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
        "portfolio": ""
    }

if "competitions" not in st.session_state:
    st.session_state.competitions = []

# 3. Custom CSS untuk Tampilan Modern & Estetik
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Hero Banner */
.hero-banner {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
    border-radius: 16px;
    padding: 26px 32px;
    margin-bottom: 24px;
    color: #ffffff;
    box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.12);
}
.hero-tag {
    display: inline-block;
    background: rgba(255, 255, 255, 0.16);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    margin-bottom: 8px;
    text-transform: uppercase;
}
.hero-title {
    font-size: 24px;
    font-weight: 800;
    margin: 0;
    color: #ffffff !important;
}
.hero-subtitle {
    font-size: 13px;
    color: #c7d2fe;
    margin-top: 6px;
    margin-bottom: 0;
}

/* Skill Badge Pills */
.skill-badge {
    display: inline-block;
    background-color: #EEF2FF;
    color: #4338CA;
    border: 1px solid #C7D2FE;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px 4px 2px 0;
}

/* Match Score Badge */
.match-badge {
    background: linear-gradient(135deg, #10B981, #059669);
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    display: inline-block;
}

/* Empty State Container */
.empty-box {
    text-align: center;
    padding: 48px 24px;
    border: 2px dashed rgba(128, 128, 128, 0.25);
    border-radius: 16px;
    background: rgba(128, 128, 128, 0.03);
    margin: 16px 0;
}
.empty-icon {
    font-size: 46px;
    margin-bottom: 12px;
}
.empty-title {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 6px;
}
.empty-desc {
    font-size: 13px;
    opacity: 0.75;
    max-width: 480px;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR MODERN ---
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 18px;">
        <span style="font-size: 30px;">🏆</span>
        <div>
            <div style="font-size: 18px; font-weight: 800; line-height: 1.1;">Cari Teman Lomba</div>
            <div style="font-size: 11px; opacity: 0.65;">Kelompok 17 • DDP 1 Fasilkom UI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Menu Navigasi",
        ["👤 Profil Saya", "📅 Eksplorasi Lomba", "🤝 Rekomendasi Teman"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Status Profil di Sidebar
    profile = st.session_state.user_profile
    if profile["name"]:
        initial = profile["name"][0].upper()
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 15px;">
                    {initial}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-size: 13px; font-weight: 700; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{profile['name']}</div>
                    <div style="font-size: 11px; opacity: 0.7;">{profile['campus'] or 'Mahasiswa'}</div>
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 11px; color: #10B981; font-weight: 600;">
                ● Profil Aktif ({len(profile['skills'])} Skill)
            </div>
            """, unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.markdown("""
            <div style="font-size: 12px; font-weight: 700; color: #F59E0B; margin-bottom: 4px;">⚠️ Profil Belum Lengkap</div>
            <div style="font-size: 11px; opacity: 0.75;">Lengkapi profil kamu untuk mendapatkan pencocokan rekan tim yang optimal.</div>
            """, unsafe_allow_html=True)
            
    st.caption("Fasilkom UI © 2026")


# ========================================================
# --- HALAMAN 1: PROFIL ---
# ========================================================
if "Profil Saya" in page:
    st.markdown("""
    <div class="hero-banner">
        <span class="hero-tag">Langkah 1</span>
        <h1 class="hero-title">Atur Profil Kolaborasimu</h1>
        <p class="hero-subtitle">Isi data diri dan keahlianmu agar sistem dapat mencocokkanmu dengan calon rekan tim terbaik.</p>
    </div>
    """, unsafe_allow_html=True)

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

            submitted = st.form_submit_button("💾 Simpan & Perbarui Profil", use_container_width=True, type="primary")
            
            if submitted:
                if not name.strip() or not skills:
                    st.error("Nama lengkap dan minimal 1 skill utama wajib diisi!")
                else:
                    st.session_state.user_profile = {
                        "name": name.strip(),
                        "major": major.strip(),
                        "year": year,
                        "campus": campus.strip(),
                        "skills": skills,
                        "level": level,
                        "availability": availability.strip(),
                        "portfolio": portfolio.strip()
                    }
                    st.toast("Profil berhasil diperbarui!", icon="🎉")
                    st.rerun()

    with col_preview:
        st.markdown("#### 🎴 Preview Kartu Profil")
        st.caption("Kartu ini yang akan dilihat oleh calon rekan tim:")
        
        prof = st.session_state.user_profile
        if prof["name"]:
            with st.container(border=True):
                initial = prof["name"][0].upper()
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 14px;">
                    <div style="background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);">
                        {initial}
                    </div>
                    <div>
                        <div style="font-size: 17px; font-weight: 700;">{prof['name']}</div>
                        <div style="font-size: 12px; opacity: 0.75;">{prof['major'] or 'Jurusan'} • {prof['campus'] or 'Kampus'} ({prof['year']})</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**Level Skill:** `{prof['level']}`")
                
                st.markdown("**Skill:**")
                skill_badges_html = "".join([f'<span class="skill-badge">{s}</span>' for s in prof["skills"]])
                st.markdown(f'<div style="margin-bottom: 12px;">{skill_badges_html}</div>', unsafe_allow_html=True)
                
                if prof["availability"]:
                    st.markdown(f"⏱️ **Waktu:** {prof['availability']}")
                
                if prof["portfolio"]:
                    st.divider()
                    st.link_button("🌐 Buka Tautan Portofolio", prof["portfolio"], use_container_width=True)
        else:
            with st.container(border=True):
                st.markdown("""
                <div class="empty-box" style="padding: 35px 15px;">
                    <div class="empty-icon" style="font-size: 38px;">👤</div>
                    <div class="empty-title" style="font-size: 15px;">Kartu Profil Belum Terisi</div>
                    <div class="empty-desc" style="font-size: 12px;">Isi form di samping lalu simpan untuk melihat preview kartu profilmu secara langsung.</div>
                </div>
                """, unsafe_allow_html=True)


# ========================================================
# --- HALAMAN 2: DAFTAR LOMBA ---
# ========================================================
elif "Eksplorasi Lomba" in page:
    st.markdown("""
    <div class="hero-banner">
        <span class="hero-tag">Eksplorasi</span>
        <h1 class="hero-title">Daftar Lomba & Kompetisi</h1>
        <p class="hero-subtitle">Jelajahi berbagai ajang kompetisi mahasiswa atau daftarkan kompetisi yang ingin kamu ikuti.</p>
    </div>
    """, unsafe_allow_html=True)

    # Toolbar Pencarian & Filter (UI Shell)
    c_search, c_cat, c_sort = st.columns([2, 1, 1])
    with c_search:
        st.text_input("Cari Lomba", placeholder="🔍 Ketik nama kompetisi atau kata kunci...", label_visibility="collapsed")
    with c_cat:
        st.selectbox("Kategori", ["Semua Kategori", "Hackathon", "Business Case", "UI/UX Design", "Data Science", "Competitive Programming"], label_visibility="collapsed")
    with c_sort:
        st.selectbox("Urutan", ["Deadline Terdekat", "Terbaru", "Paling Populer"], label_visibility="collapsed")

    # Fitur Opsional Tambah Lomba untuk Uji Tampilan UI (Tanpa data dummy bawaan)
    with st.expander("➕ Daftarkan Lomba Baru (Uji Coba Tampilan UI)"):
        with st.form("add_competition_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_title = st.text_input("Nama Kompetisi", placeholder="Contoh: Gemastik 2026")
                new_category = st.selectbox("Kategori Bidang", ["Hackathon", "Business Case", "UI/UX Design", "Data Science", "Competitive Programming"])
            with c2:
                new_organizer = st.text_input("Penyelenggara", placeholder="Contoh: Puspresnas / Kemdikbud")
                new_deadline = st.date_input("Batas Pendaftaran")
            
            btn_add = st.form_submit_button("Tambah Lomba ke Daftar", use_container_width=True)
            if btn_add:
                if new_title.strip():
                    st.session_state.competitions.append({
                        "title": new_title.strip(),
                        "category": new_category,
                        "organizer": new_organizer.strip() or "-",
                        "deadline": str(new_deadline)
                    })
                    st.success("Kompetisi berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.warning("Nama kompetisi wajib diisi.")

    # Tampilan Lomba
    if not st.session_state.competitions:
        # Tampilan Kosong (Empty State Modern)
        st.markdown("""
        <div class="empty-box">
            <div class="empty-icon">🎯</div>
            <div class="empty-title">Belum Ada Lomba yang Terdaftar</div>
            <div class="empty-desc">
                Saat ini daftar lomba masih kosongan. Kamu bisa menggunakan fitur <b>"+ Daftarkan Lomba Baru"</b> di atas untuk menguji tampilan antarmuka kartu lomba.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Jika ada lomba yang diinputkan oleh user
        cols = st.columns(2)
        for i, comp in enumerate(st.session_state.competitions):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <span class="skill-badge" style="background: #EEF2FF; color: #4338CA;">{comp['category']}</span>
                            <div style="font-size: 17px; font-weight: 700; margin-top: 6px;">{comp['title']}</div>
                            <div style="font-size: 12px; opacity: 0.7;">Penyelenggara: {comp['organizer']}</div>
                        </div>
                    </div>
                    <div style="margin-top: 12px; font-size: 12px;">
                        📅 <b>Deadline:</b> {comp['deadline']}
                    </div>
                    """, unsafe_allow_html=True)


# ========================================================
# --- HALAMAN 3: REKOMENDASI TEMAN ---
# ========================================================
else:
    st.markdown("""
    <div class="hero-banner">
        <span class="hero-tag">Smart Matching</span>
        <h1 class="hero-title">Rekomendasi Rekan Tim</h1>
        <p class="hero-subtitle">Algoritma cerdas mencocokkan profilmu dengan kandidat terbaik berdasarkan keahlian komplementer.</p>
    </div>
    """, unsafe_allow_html=True)
    
    profile = st.session_state.user_profile
    
    if not profile["name"]:
        with st.container(border=True):
            st.markdown("""
            <div class="empty-box" style="padding: 40px 20px;">
                <div class="empty-icon">⚠️</div>
                <div class="empty-title">Profil Kamu Belum Dilengkapi</div>
                <div class="empty-desc">
                    Untuk mendapatkan rekomendasi rekan tim yang relevan dan akurat, silakan isi profil serta skill utamamu terlebih dahulu di menu <b>Profil Saya</b>.
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Ringkasan Profil Pengguna di Header Matching
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Skill Utama Kamu", f"{len(profile['skills'])} Skill", "Terverifikasi")
        with m2:
            st.metric("Level Pengalaman", profile['level'])
        with m3:
            st.metric("Kandidat Cocok", "3 Rekan", "Algoritma Siap")
            
        st.markdown("<br>", unsafe_allow_html=True)

        # Tab Pilihan Tampilan: Kartu (Card View) & Tabel (Dataframe)
        tab_cards, tab_table = st.tabs(["🎴 Tampilan Kartu (Card View)", "📊 Tampilan Tabel"])

        # Data kandidat rekomendasi
        candidates = [
            {
                "name": "Ani Wijaya",
                "campus": "Universitas Indonesia",
                "major": "Sistem Informasi",
                "skills": ["UI/UX", "Public Speaking", "Pitching"],
                "match": 92,
                "availability": "Weekday malam & Weekend",
                "contact": "https://t.me/aniwijaya"
            },
            {
                "name": "Budi Pratama",
                "campus": "Institut Teknologi Bandung",
                "major": "Manajemen Bisnis",
                "skills": ["Business Analysis", "Finance", "Pitching"],
                "match": 85,
                "availability": "Fleksibel setiap hari",
                "contact": "https://linkedin.com"
            },
            {
                "name": "Citra Lestari",
                "campus": "Universitas Gadjah Mada",
                "major": "Ilmu Komputer",
                "skills": ["Frontend/Web", "Python", "Machine Learning"],
                "match": 78,
                "availability": "Weekend full",
                "contact": "https://github.com"
            }
        ]

        with tab_cards:
            cols = st.columns(3)
            for i, cand in enumerate(candidates):
                with cols[i]:
                    with st.container(border=True):
                        # Header Card
                        initial = cand["name"][0].upper()
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="background: linear-gradient(135deg, #3B82F6, #1D4ED8); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: bold;">
                                    {initial}
                                </div>
                                <div>
                                    <div style="font-size: 15px; font-weight: 700;">{cand['name']}</div>
                                    <div style="font-size: 11px; opacity: 0.7;">{cand['major']}</div>
                                </div>
                            </div>
                            <span class="match-badge">{cand['match']}% Match</span>
                        </div>
                        <div style="font-size: 11px; opacity: 0.75; margin-bottom: 8px;">🏛️ {cand['campus']}</div>
                        """, unsafe_allow_html=True)

                        # Skill Badges
                        st.markdown("**Skill Komplementer:**")
                        cand_skills_html = "".join([f'<span class="skill-badge">{s}</span>' for s in cand["skills"]])
                        st.markdown(f'<div style="margin-bottom: 10px;">{cand_skills_html}</div>', unsafe_allow_html=True)

                        st.markdown(f"<div style='font-size: 11px; opacity: 0.8; margin-bottom: 12px;'>⏱️ {cand['availability']}</div>", unsafe_allow_html=True)
                        
                        st.link_button(f"💬 Hubungi {cand['name'].split()[0]}", cand["contact"], use_container_width=True)

        with tab_table:
            df_rekomendasi = pd.DataFrame([
                {
                    "Nama": c["name"],
                    "Kampus": c["campus"],
                    "Jurusan": c["major"],
                    "Skill": ", ".join(c["skills"]),
                    "Kecocokan": c["match"] / 100.0,
                    "Kontak": c["contact"]
                }
                for c in candidates
            ])

            st.dataframe(
                df_rekomendasi,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Kecocokan": st.column_config.ProgressColumn(
                        "Skor Kecocokan",
                        help="Dihitung berdasarkan kesesuaian skill komplementer",
                        format="%.0f%%",
                        min_value=0,
                        max_value=1,
                    ),
                    "Kontak": st.column_config.LinkColumn("Tautan Kontak")
                }
            )
