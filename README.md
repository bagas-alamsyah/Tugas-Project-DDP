# Tugas DDP1 - Kelompok 17
---
## Deskripsi:
Tugas akhir DPP1 (G) Fasilkom UI Kelompok 17

## Anggota:
- Haris Zidan
- Farraj Bagas Alamsyah
- Muhammad Nur Ataya

# Cari Teman Lomba

A web app that helps university students find teammates for competitions
(hackathons, business case, data science, UI/UX) based on skills, roles, and
availability.

## Features

- Register and log in
- Create a profile: name, major, year, campus, skills with levels
  (beginner / intermediate / advanced), availability, optional portfolio link
- Browse competitions: name, category, deadlines, team size, roles needed
- Get a ranked list of recommended teammates or teams for a competition
- Contact matches through the WhatsApp / LinkedIn link on their profile

## Project Structure

```
lomba_match/
├── README.md
├── requirements.txt
├── app.py              # Flask app setup and routes
├── models.py           # Database models: User, Skill, Competition, Team
├── matching.py         # Matching score logic (core feature)
├── matching_test.py    # Tests for the scoring function
├── templates/          # HTML pages
├── static/             # CSS and JS
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

Candidates are sorted by score, highest first. Weights are set at the top of
`matching.py` and can be tuned.

## Setup

```bash
git clone <repo-url>
cd lomba_match
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

## Running Tests

```bash
python -m pytest matching_test.py
```

## Scope and Limitations

This is an end-term project MVP, so:

- Competition data is loaded from a CSV, not scraped automatically
- No in-app chat; users contact each other externally
- Spam protection is limited to basic email validation
- Passwords are hashed, but the app is not production-hardened

## Future Work

- In-app chat
- Automatic competition data updates
- Email verification with campus domains
- Support for high school students
- Previous competition experience as a matching factor

## Tech Stack

Python, Streamlib, SQLite, SQLAlchemy, HTML/CSS
