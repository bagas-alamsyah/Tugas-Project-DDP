import sqlite3 as sql
from contextlib import contextmanager
from pathlib import Path

import re
from datetime import date
from enum import IntEnum

def _try_get_db_config(cfg) -> dict:
    accepted_acronyms = ['db', 'database']

    for section, v in cfg.items():
        if section in accepted_acronyms:
            return v
        elif isinstance(v, dict):
            result = _try_get_db_config(v)
            if result:
                return result

    return {}


class ColumnExistError(Exception):
    pass

# --------------------------------------------------------------------------
# Weekday class | Time utils
# --------------------------------------------------------------------------
class Weekday(IntEnum):
    # Monday-first, same as date.weekday(). 
    # NOT the Sunday-first numbering; use from_sunday_zero() for those.
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
 
    @classmethod
    def from_sunday_zero(cls, n: int) -> "Weekday":
        if isinstance(n, bool) or not isinstance(n, int) or not 0 <= n <= 6:
            raise ValueError(
                f"Sunday-indexed weekday must be an int 0..6, got {n!r}")
        return cls((n - 1) % 7)
 
    @classmethod
    def from_date(cls, d: date) -> "Weekday":
        return cls(d.weekday())
 
 
# [0-9] instead of \d (which matches non-ASCII digits); fullmatch rejects "\n".
_TIME_RE = re.compile(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]")
END_OF_DAY = "24:00"

def _coerce_weekday(value) -> Weekday:
    """Return a Weekday; raise ValueError for non-int, bool, or out-of-range values."""
    if isinstance(value, Weekday):
        return value
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"weekday must be a Weekday or int 0 (Monday)..6 (Sunday), "
            f"got {type(value).__name__}: {value!r}")
    try:
        return Weekday(value)
    except ValueError:
        raise ValueError(
            f"weekday must be 0 (Monday)..6 (Sunday), got {value!r}. "
            f"For strftime('%w') / getDay() values use Weekday.from_sunday_zero()."
        ) from None
    
def _validate_time(value: str, field: str) -> str:
    """Check a zero-padded 'HH:MM' string; '24:00' is allowed only as end_time."""
    if not isinstance(value, str):
        raise ValueError(
            f"{field} must be a zero-padded 'HH:MM' string, "
            f"got {type(value).__name__}: {value!r}")
    if value == END_OF_DAY:
        if field != "end_time":
            raise ValueError(f"{field} cannot be '24:00' (only valid as end_time)")
        return value
    if not _TIME_RE.fullmatch(value):
        raise ValueError(
            f"{field} must be 'HH:MM' from '00:00' to '23:59' "
            f"(or '24:00' for end_time), got {value!r}")
    return value
 
 
def _validate_slot(start_time: str, end_time: str) -> tuple[str, str]:
    """Validate both times and that end is after start. Returns (start, end)."""
    start = _validate_time(start_time, "start_time")
    end = _validate_time(end_time, "end_time")
    if end == "00:00":
        raise ValueError("end_time '00:00' is ambiguous; use '24:00' for end-of-day")
    if end <= start:
        raise ValueError(
            f"end_time ({end}) must be later than start_time ({start}); "
            f"slots cannot cross midnight, split them across two weekdays")
    return start, end
 
 
def _merge_intervals(intervals):
    """Merge overlapping or touching (start, end) pairs into sorted, disjoint ones."""
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    return merged
 
 
def _intersect(a, b):
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        start = max(a[i][0], b[j][0])
        end = min(a[i][1], b[j][1])
        if start < end:
            out.append((start, end))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out

# --------------------------------------------------------------------------
# Base class
# --------------------------------------------------------------------------
class Database:
    """
    One subclass = one table.

    Subclasses define:
        table_name       : str
        schema           : the body of CREATE TABLE (columns + constraints)
        required_columns : {name: (type, constraints)} added later with
                           ALTER TABLE. Use for columns added AFTER release.
                           (ALTER cannot add UNIQUE or non-constant defaults.)
    """
    table_name = None
    schema = "id INTEGER PRIMARY KEY AUTOINCREMENT"
    required_columns = {}

    def __init__(self, cfg):
        self.cfg = _try_get_db_config(cfg)
        assert self.cfg, "Cannot find database configuration."
        self.path = self.cfg["path"]

        if not (self.table_name and self.table_name.isidentifier()):
            raise ValueError(f"Invalid table name: {self.table_name}")

        self.columns = []
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._sync_columns()

    # ---- connection ------------------------------------------------------
    @contextmanager
    def _connect(self):
        conn = sql.connect(self.path)
        conn.row_factory = sql.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ---- schema ----------------------------------------------------------
    def _init_db(self):
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode = WAL")  # persistent, set once
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {self.table_name} ({self.schema})"
            )

    def _get_columns(self):
        with self._connect() as conn:
            rows = conn.execute(
                f"PRAGMA table_info({self.table_name})").fetchall()
        self.columns = [r["name"] for r in rows]
        return self.columns

    def new_column(self, column_name, data_type, constraints=""):
        if not column_name.isidentifier():
            raise ValueError(f"Invalid column name: {column_name}")
        if column_name in self._get_columns():
            raise ColumnExistError(
                f"Failed to append new column: duplicate column '{column_name}'")

        with self._connect() as conn:
            conn.execute(
                f"ALTER TABLE {self.table_name} "
                f"ADD COLUMN {column_name} {data_type} {constraints}"
            )
        self._get_columns()

    def _sync_columns(self):
        existing = set(self._get_columns())
        for name, (typ, cons) in self.required_columns.items():
            if name not in existing:
                self.new_column(name, typ, cons)

    def _check_columns(self, names):
        bad = set(names) - set(self.columns)
        if bad:
            raise ValueError(f"Unknown columns for {self.table_name}: {bad}")

    # ---- shared CRUD -----------------------------------------------------
    def get(self, id):
        try:
            id = int(id)
        except (TypeError, ValueError):
            return None
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT * FROM {self.table_name} WHERE id = ?", (id,)
            ).fetchone()
        return dict(row) if row else None

    def all(self):
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM {self.table_name} ORDER BY id").fetchall()
        return [dict(r) for r in rows]

    def find(self, **conditions):
        """find(user_id=3, is_active=1) -> list of dicts (AND-ed equality)."""
        if not conditions:
            return self.all()
        self._check_columns(conditions)
        where = " AND ".join(f"{k} = ?" for k in conditions)
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM {self.table_name} WHERE {where} ORDER BY id",
                tuple(conditions.values()),
            ).fetchall()
        return [dict(r) for r in rows]

    def find_one(self, **conditions):
        rows = self.find(**conditions)
        return rows[0] if rows else None

    def insert(self, **fields):
        self._check_columns(fields)
        cols = ", ".join(fields)
        marks = ", ".join("?" * len(fields))
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO {self.table_name} ({cols}) VALUES ({marks})",
                tuple(fields.values()),
            )
            return cur.lastrowid

    def update(self, id, **fields):
        if not fields:
            return False
        self._check_columns(fields)
        if "id" in fields:
            raise ValueError("Cannot update id")
        sets = ", ".join(f"{k} = ?" for k in fields)
        with self._connect() as conn:
            cur = conn.execute(
                f"UPDATE {self.table_name} SET {sets} WHERE id = ?",
                (*fields.values(), id),
            )
            return cur.rowcount > 0

    def set(self, id, column_name, value):
        return self.update(id, **{column_name: value})

    def delete(self, id):
        with self._connect() as conn:
            cur = conn.execute(
                f"DELETE FROM {self.table_name} WHERE id = ?", (id,))
            return cur.rowcount > 0


# --------------------------------------------------------------------------
# users
# --------------------------------------------------------------------------
class UserDB(Database):
    table_name = "users"
    schema = """
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT NOT NULL UNIQUE,
        display_name  TEXT NOT NULL DEFAULT '',
        email         TEXT UNIQUE,
        whatsapp      TEXT UNIQUE,
        affiliation   TEXT,
        is_active     INTEGER NOT NULL DEFAULT 1,
        is_admin      INTEGER NOT NULL DEFAULT 0,
        created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    """
    # Columns added after first release go here, e.g.:
    # required_columns = {
    #     "salt":    ("BLOB", ""),
    #     "pw_hash": ("BLOB", ""),
    # }

    def register(self, username, display_name="", email=None,
                 whatsapp=None, affiliation=None):
        # Store NULL, not '', for optional UNIQUE columns
        return self.insert(
            username=username.strip(),
            display_name=display_name.strip() or username.strip(),
            email=(email or "").strip() or None,
            whatsapp=(whatsapp or "").strip() or None,
            affiliation=(affiliation or "").strip() or None,
        )

    def get_by_username(self, username):
        return self.find_one(username=username.strip())

    def deactivate(self, user_id):
        return self.set(user_id, "is_active", 0)


# --------------------------------------------------------------------------
# competitions
# --------------------------------------------------------------------------
class CompetitionDB(Database):
    table_name = "competitions"
    schema = """
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        name                  TEXT NOT NULL UNIQUE,
        description           TEXT NOT NULL DEFAULT '',
        created_by            INTEGER REFERENCES users(id) ON DELETE SET NULL,
        created_at            TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        registration_deadline TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        is_open               INTEGER NOT NULL DEFAULT 1,
        min_team_size         INTEGER NOT NULL DEFAULT 2
                              CHECK (min_team_size >= 2),
        team_size_range       INTEGER NOT NULL DEFAULT 0
                              CHECK (team_size_range >= 0)
    """

    @staticmethod
    def max_team_size(comp) -> int:
        """
        Return the largest allowed team size for a competition.

        A competition stores a minimum size and a range on top of it, so
        max = min_team_size + team_size_range.

        Args:
            comp (dict): a competition row, e.g. from CompetitionDB.get().
                Must contain "min_team_size" and "team_size_range".

        Returns:
            int: maximum number of members per team.

        Example:
            min_team_size=3, team_size_range=2  ->  5  (teams of 3 to 5)
        """
        return comp["min_team_size"] + comp["team_size_range"]

    def get_open_competition(self):
        """Open and before the deadline (both stored as UTC 'YYYY-MM-DD HH:MM:SS')."""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM competitions
                WHERE is_open = 1 AND registration_deadline > CURRENT_TIMESTAMP
                ORDER BY registration_deadline
            """).fetchall()
        return [dict(r) for r in rows]

    def can_register(self, competition_id):
        with self._connect() as conn:
            row = conn.execute("""
                SELECT 1 FROM competitions
                WHERE id = ? AND is_open = 1
                  AND registration_deadline > CURRENT_TIMESTAMP
            """, (competition_id,)).fetchone()
        return row is not None

    def close(self, competition_id):
        return self.set(competition_id, "is_open", 0)


# --------------------------------------------------------------------------
# participants  (link: user <-> competition)
# --------------------------------------------------------------------------
class ParticipantDB(Database):
    table_name = "participants"
    schema = """
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id        INTEGER NOT NULL
                       REFERENCES users(id) ON DELETE CASCADE,
        competition_id INTEGER NOT NULL
                       REFERENCES competitions(id) ON DELETE CASCADE,
        is_in_team     INTEGER NOT NULL DEFAULT 0,
        created_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (user_id, competition_id)
    """

    def join(self, user_id, competition_id):
        """Raises sqlite3.IntegrityError if already joined."""
        return self.insert(user_id=user_id, competition_id=competition_id)

    def leave(self, user_id, competition_id):
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM participants WHERE user_id = ? AND competition_id = ?",
                (user_id, competition_id),
            )
            return cur.rowcount > 0

    def is_joined(self, user_id, competition_id):
        return self.find_one(user_id=user_id,
                             competition_id=competition_id) is not None

    def list_for_competition(self, competition_id, only_unteamed=False):
        """Participants joined with user info."""
        query = """
            SELECT p.id AS participant_id, p.user_id, p.is_in_team,
                   u.username, u.display_name, u.affiliation
            FROM participants p
            JOIN users u ON u.id = p.user_id
            WHERE p.competition_id = ?
        """
        if only_unteamed:
            query += " AND p.is_in_team = 0"
        with self._connect() as conn:
            rows = conn.execute(query + " ORDER BY p.id",
                                (competition_id,)).fetchall()
        return [dict(r) for r in rows]

    def competitions_of_user(self, user_id):
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT c.* FROM competitions c
                JOIN participants p ON p.competition_id = c.id
                WHERE p.user_id = ?
                ORDER BY c.registration_deadline
            """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


# --------------------------------------------------------------------------
# skills  (what each user can do, 1-4)
# --------------------------------------------------------------------------
class SkillDB(Database):
    table_name = "skills"
    schema = """
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL
                    REFERENCES users(id) ON DELETE CASCADE,
        skill_name  TEXT NOT NULL COLLATE NOCASE,
        proficiency INTEGER NOT NULL DEFAULT 1
                    CHECK (proficiency BETWEEN 1 AND 4),
        UNIQUE (user_id, skill_name)
    """

    def set_skill(self, user_id, skill_name, proficiency):
        """Add the skill, or update its level if the user already has it."""
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO skills (user_id, skill_name, proficiency)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, skill_name)
                DO UPDATE SET proficiency = excluded.proficiency
            """, (user_id, skill_name.strip(), proficiency))

    def for_user(self, user_id):
        """
        Return all skills belonging to one user.

        Shortcut for self.find(user_id=user_id).

        Args:
            user_id (int): id of the user in the users table.

        Returns:
            list[dict]: one dict per skill row, ordered by id, e.g.
                [{"id": 1, "user_id": 3, "skill_name": "python", "proficiency": 3}]
                Empty list if the user has no skills.
        """
        return self.find(user_id=user_id)

    def remove_skill(self, user_id, skill_name):
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM skills WHERE user_id = ? AND skill_name = ?",
                (user_id, skill_name.strip()),
            )
            return cur.rowcount > 0

    def users_with_skill(self, skill_name, min_level=1):
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT s.user_id, u.username, s.proficiency
                FROM skills s JOIN users u ON u.id = s.user_id
                WHERE s.skill_name = ? AND s.proficiency >= ?
                ORDER BY s.proficiency DESC
            """, (skill_name.strip(), min_level)).fetchall()
        return [dict(r) for r in rows]


# --------------------------------------------------------------------------
# availability  (weekly recurring slots)
# TODO(@hariszidan-ui): review class
# --------------------------------------------------------------------------
class TimeAvailabilityDB(Database):
    table_name = "availabilities"
    schema = """
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL
                   REFERENCES users(id) ON DELETE CASCADE,
        weekday    INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
        start_time TEXT NOT NULL,              -- 'HH:MM' 24h
        end_time   TEXT NOT NULL,              -- 'HH:MM' 24h
        CHECK (end_time > start_time),
        UNIQUE (user_id, weekday, start_time, end_time)
    """
    # weekday: 0 = Monday ... 6 = Sunday

    def add_slot(self, user_id, weekday, start_time, end_time):
        return self.insert(user_id=user_id, weekday=weekday,
                           start_time=start_time, end_time=end_time)

    def for_user(self, user_id):
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM availabilities
                WHERE user_id = ? ORDER BY weekday, start_time
            """, (user_id,)).fetchall()
        return [dict(r) for r in rows]

    def clear_user(self, user_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM availabilities WHERE user_id = ?",
                         (user_id,))

    def overlap(self, user_a, user_b):
        """Shared time windows: [(weekday, start, end), ...]."""
        result = []
        slots_b = self.for_user(user_b)
        for a in self.for_user(user_a):
            for b in slots_b:
                if a["weekday"] != b["weekday"]:
                    continue
                start = max(a["start_time"], b["start_time"])
                end = min(a["end_time"], b["end_time"])
                if start < end:
                    result.append((a["weekday"], start, end))
        return sorted(result)

    def common_overlap(self, user_ids):
        """Windows where ALL given users are free (for whole-team matching)."""
        user_ids = list(user_ids)
        if not user_ids:
            return []
        windows = [(s["weekday"], s["start_time"], s["end_time"])
                   for s in self.for_user(user_ids[0])]
        for uid in user_ids[1:]:
            theirs = self.for_user(uid)
            merged = []
            for wd, st, en in windows:
                for t in theirs:
                    if t["weekday"] != wd:
                        continue
                    s, e = max(st, t["start_time"]), min(en, t["end_time"])
                    if s < e:
                        merged.append((wd, s, e))
            windows = merged
        return sorted(windows)


# --------------------------------------------------------------------------
# teams
# TODO(@hariszidan-ui): review class
# --------------------------------------------------------------------------
class TeamDB(Database):
    table_name = "teams"
    schema = """
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        competition_id INTEGER NOT NULL
                       REFERENCES competitions(id) ON DELETE CASCADE,
        name           TEXT NOT NULL,
        created_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (competition_id, name)
    """

    def create(self, competition_id, name):
        return self.insert(competition_id=competition_id, name=name.strip())

    def for_competition(self, competition_id):
        return self.find(competition_id=competition_id)


# --------------------------------------------------------------------------
# team members  (link: participant <-> team)
# TODO(@hariszidan-ui): review class
# --------------------------------------------------------------------------
class TeamMemberDB(Database):
    table_name = "team_members"
    schema = """
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id        INTEGER NOT NULL
                       REFERENCES teams(id) ON DELETE CASCADE,
        participant_id INTEGER NOT NULL UNIQUE
                       REFERENCES participants(id) ON DELETE CASCADE,
        role           TEXT NOT NULL DEFAULT 'member',
        joined_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    """
    # participant_id is UNIQUE: a participant (user in ONE competition)
    # can only be in one team.

    def add_member(self, team_id, participant_id, role="member"):
        """
        Adds the member and flags participants.is_in_team in ONE transaction.
        Raises ValueError if the team is full or the competitions differ.
        """
        with self._connect() as conn:
            team = conn.execute("""
                SELECT t.competition_id, c.min_team_size, c.team_size_range
                FROM teams t JOIN competitions c ON c.id = t.competition_id
                WHERE t.id = ?
            """, (team_id,)).fetchone()
            if team is None:
                raise ValueError("Team not found")

            part = conn.execute(
                "SELECT competition_id FROM participants WHERE id = ?",
                (participant_id,),
            ).fetchone()
            if part is None or part["competition_id"] != team["competition_id"]:
                raise ValueError("Participant is not in this team's competition")

            size = conn.execute(
                "SELECT COUNT(*) AS n FROM team_members WHERE team_id = ?",
                (team_id,),
            ).fetchone()["n"]
            if size >= team["min_team_size"] + team["team_size_range"]:
                raise ValueError("Team is full")

            conn.execute(
                "INSERT INTO team_members (team_id, participant_id, role) "
                "VALUES (?, ?, ?)", (team_id, participant_id, role))
            conn.execute(
                "UPDATE participants SET is_in_team = 1 WHERE id = ?",
                (participant_id,))

    def remove_member(self, participant_id):
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM team_members WHERE participant_id = ?",
                (participant_id,))
            conn.execute(
                "UPDATE participants SET is_in_team = 0 WHERE id = ?",
                (participant_id,))
            return cur.rowcount > 0

    def members(self, team_id):
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT tm.participant_id, tm.role, p.user_id,
                       u.username, u.display_name
                FROM team_members tm
                JOIN participants p ON p.id = tm.participant_id
                JOIN users u ON u.id = p.user_id
                WHERE tm.team_id = ?
                ORDER BY tm.id
            """, (team_id,)).fetchall()
        return [dict(r) for r in rows]

    def is_complete(self, team_id):
        """True once the team has at least min_team_size members."""
        with self._connect() as conn:
            row = conn.execute("""
                SELECT (SELECT COUNT(*) FROM team_members WHERE team_id = t.id)
                       >= c.min_team_size AS ok
                FROM teams t JOIN competitions c ON c.id = t.competition_id
                WHERE t.id = ?
            """, (team_id,)).fetchone()
        return bool(row["ok"]) if row else False


# --------------------------------------------------------------------------
# Create everything in dependency order
# --------------------------------------------------------------------------
def init_all(cfg) -> dict:
    """
    Parents first, children after (foreign keys point at the parents).

        @st.cache_resource
        def get_dbs():
            return init_all(load_settings())
    """
    users = UserDB(cfg)
    competitions = CompetitionDB(cfg)
    participants = ParticipantDB(cfg)
    skills = SkillDB(cfg)
    availability = TimeAvailabilityDB(cfg)
    teams = TeamDB(cfg)
    team_members = TeamMemberDB(cfg)
    return {
        "users": users,
        "competitions": competitions,
        "participants": participants,
        "skills": skills,
        "availability": availability,
        "teams": teams,
        "team_members": team_members,
    }


# TODO(@hariszidan-ui): build the data
# TODO(@hariszidan-ui): run test
if __name__ == "__main__":
    # Quick smoke test using a throwaway database
    demo_cfg = {"database": {"path": "data/demo_test.db"}}
    dbs = init_all(demo_cfg)

    uid = dbs["users"].register("ada", "Ada", email="ada@example.com")
    cid = dbs["competitions"].insert(
        name="Hack Night", registration_deadline="2099-01-01 00:00:00")
    pid = dbs["participants"].join(uid, cid)
    dbs["skills"].set_skill(uid, "python", 3)
    dbs["availability"].add_slot(uid, 0, "18:00", "21:00")
    tid = dbs["teams"].create(cid, "Team A")
    dbs["team_members"].add_member(tid, pid)

    print(dbs["team_members"].members(tid))
    print(dbs["competitions"].get_open_competition())