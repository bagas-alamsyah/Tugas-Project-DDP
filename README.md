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

- Create a profile: name, major, year, campus, skills with levels (beginner / intermediate / advanced), availability, optional portfolio link
- Browse competitions: name, category, deadlines, team size, roles needed
- Get a ranked list of recommended teammates for a competition

**If time permits**

- Register and log in (password hashed with bcrypt)
- Team model (create and join teams)
- Contact matches through the WhatsApp / LinkedIn link on their profile

## Project Structure

```
Tugas-Project-DDP/
├── README.md
├── requirements.txt
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

- **skill_overlap**: how many required skills the user has, weighted by level
- **role_fit**: whether the user's role matches a role the team needs
- **time_overlap**: shared availability between the user and the team

Candidates are sorted by score, highest first. Weights are set at the top of `matching.py` and can be tuned.

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

- Competition data is loaded from a CSV, not scraped automatically
- No in-app chat; users contact each other externally
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
