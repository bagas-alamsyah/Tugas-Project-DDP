# Tugas DDP1 - Kelompok 17

---

## Deskripsi

Tugas akhir DDP1 (G) Fasilkom UI Kelompok 17

## Anggota

- Haris Zidan
- Farraj Bagas Alamsyah
- Muhammad Nur Ataya

# Cari Teman Lomba

A web app that helps university students find teammates for competitions (hackathons, business case, data science, UI/UX) based on skills, roles, and availability.

## Features

**MVP (must have)**

- Create a profile: name, major, year, campus, main team role, per-skill proficiency levels (Pemula / Menengah / Mahir), structured weekly availability slots, and optional portfolio link
- Browse & add competitions: pre-loaded seed competition catalog (`data/competitions.csv` + curated national competitions) combined with user-submitted competitions featuring **Smart Auto-Detect** for category, roles needed, and required skills
- Get a ranked list of recommended teammates for a competition with an explicit **50-30-20 score breakdown** (`Skill Overlap`, `Role Fit`, `Time Overlap`) on every candidate card

**If time permits**

- Register and log in (password hashed with bcrypt)
- Team model (create teams, join open teams, or 1-click invite recommended candidates directly into a team)
- Contact matches and teams through the WhatsApp / LinkedIn link on their card

## Project Structure

```
Tugas-Project-DDP/
├── README.md
├── requirements.txt
├── settings.toml       # Application & database settings
├── .gitignore
├── app.py              # Streamlit app (UI and page flow)
├── models.py           # SQLite tables and queries: User, Skill, Competition, Team
├── matching.py         # Matching score logic (core feature)
├── matching_test.py    # Tests for the scoring function
└── data/
    └── competitions.csv  # Seed data for competitions
```

## How Matching Works

Each candidate gets a score from 0 to 1 for a given competition:

```
score = skill_overlap * 0.5 + role_fit * 0.3 + time_overlap * 0.2
```

- **skill_overlap**: how many required/complementary skills the candidate has, weighted by each skill's proficiency level (Pemula 60%, Menengah 80%, Mahir 100%)
- **role_fit**: whether the candidate's primary role matches a role the competition/team needs and complements the user's role
- **time_overlap**: shared weekly availability time slots between the user and the candidate

Candidates are sorted by score, highest first, with individual `Skill (50%)`, `Role (30%)`, and `Time (20%)` percentages displayed on each card. Weights are set at the top of `matching.py` and can be tuned.

## Setup

```
git clone https://github.com/bagas-alamsyah/Tugas-Project-DDP.git
cd Tugas-Project-DDP
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501

## Running Tests

```
python -m pytest matching_test.py
```

## Contributing

- Never push directly to `main` (except small docs fixes); work on your own branch, e.g. `feat/matching`, `feat/storage`, `feat/ui`
- Merge into `main` through a Pull Request with at least one review
- Commit messages start with a type: `feat:`, `fix:`, `docs:`, `chore:`
- Follow PEP 8: `snake_case` for functions and variables, a one-line docstring for every function
- One person per module to avoid merge conflicts

## Scope and Limitations

This is an end-term project MVP, so:

- Competition data uses a hybrid seed catalog (`data/competitions.csv` + curated seed list) and supports manual user additions with keyword-based Smart Auto-Detect (not scraped live from external websites)
- No in-app chat; users contact each other externally via WhatsApp / LinkedIn links
- Spam protection is limited to basic validation
- Passwords are hashed, but the app is not production-hardened

## Future Work

- In-app chat
- Automatic competition data updates
- Email verification with campus domains
- Support for high school students
- Previous competition experience as a matching factor

## Tech Stack

Python, Streamlit, SQLite, pandas, bcrypt, pytest
