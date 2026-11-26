"""Matching score logic for Cari Teman Lomba (50-30-20 formula).

score = skill_overlap * 0.5 + role_fit * 0.3 + time_overlap * 0.2

Every sub-score and the final score are floats in the range 0..1.
Profiles are plain dicts with the same keys used in app.py:
    name, role, skills (list), skill_levels (dict), level (str),
    availability_slots (list of str), availability (legacy free text)
A competition is a dict with the keys "roles_needed" and "required_skills".
"""
from dataclasses import dataclass

# ---- Tunable weights (must sum to 1.0) -------------------------------------
SKILL_WEIGHT = 0.5
ROLE_WEIGHT = 0.3
TIME_WEIGHT = 0.2

# Proficiency level -> multiplier applied to a matched skill.
LEVEL_WEIGHTS = {"Pemula": 0.6, "Menengah": 0.8, "Mahir": 1.0}
DEFAULT_LEVEL = "Menengah"

# A slot that means "free at any time".
FLEXIBLE_SLOT = "Fleksibel Setiap Hari"

# Role fit values (0..1).
ROLE_NEEDED_COMPLEMENT = 1.0   # needed by competition and different from user's role
ROLE_NEEDED_SAME = 0.7         # needed by competition but same as user's role
ROLE_OTHER_COMPLEMENT = 0.4    # not needed, but different from user's role
ROLE_OTHER_SAME = 0.1          # not needed and same as user's role
ROLE_NO_COMP_COMPLEMENT = 1.0  # no competition chosen, different role
ROLE_NO_COMP_SAME = 0.5        # no competition chosen, same role

# Without a competition, a skill the user already has counts for half.
SHARED_SKILL_CREDIT = 0.5


@dataclass
class MatchResult:
    """Score breakdown of one candidate (all values in 0..1)."""

    candidate: dict
    score: float
    skill: float
    role: float
    time: float

    def percents(self) -> tuple[int, int, int, int]:
        """Return (score, skill, role, time) as whole percentages."""
        return tuple(round(v * 100) for v in (self.score, self.skill, self.role, self.time))


def _norm(text) -> str:
    """Normalize a label for case-insensitive comparison."""
    return str(text or "").strip().lower()


def _level_weight(cand: dict, skill: str) -> float:
    """Return the proficiency multiplier of one candidate skill."""
    levels = cand.get("skill_levels") or {}
    level = levels.get(skill, cand.get("level", DEFAULT_LEVEL))
    return LEVEL_WEIGHTS.get(level, LEVEL_WEIGHTS[DEFAULT_LEVEL])


def skill_overlap(user: dict, cand: dict, comp: dict | None = None) -> float:
    """Score how well the candidate's skills cover what the team still needs.

    With a competition: the target is the required skills the user does NOT
    have yet (the gap); if the user already covers all of them, the target is
    every required skill. Each matched skill counts by its proficiency weight.
    Without a competition: skills the user lacks count fully, skills the user
    already has count for SHARED_SKILL_CREDIT, averaged over the candidate's skills.
    """
    cand_skills = {_norm(s): s for s in cand.get("skills") or []}
    if not cand_skills:
        return 0.0
    user_skills = {_norm(s) for s in user.get("skills") or []}
    required = {_norm(s) for s in (comp or {}).get("required_skills") or []}

    if required:
        target = (required - user_skills) or required
        matched = target & cand_skills.keys()
        total = sum(_level_weight(cand, cand_skills[k]) for k in matched)
        return min(1.0, total / len(target))

    total = 0.0
    for key, original in cand_skills.items():
        credit = SHARED_SKILL_CREDIT if key in user_skills else 1.0
        total += credit * _level_weight(cand, original)
    return min(1.0, total / len(cand_skills))


def role_fit(user: dict, cand: dict, comp: dict | None = None) -> float:
    """Score whether the candidate's role is needed and complements the user's."""
    cand_role = _norm(cand.get("role"))
    user_role = _norm(user.get("role"))
    if not cand_role:
        return 0.0
    complement = cand_role != user_role
    needed = {_norm(r) for r in (comp or {}).get("roles_needed") or []}

    if not needed:
        return ROLE_NO_COMP_COMPLEMENT if complement else ROLE_NO_COMP_SAME
    if cand_role in needed:
        return ROLE_NEEDED_COMPLEMENT if complement else ROLE_NEEDED_SAME
    return ROLE_OTHER_COMPLEMENT if complement else ROLE_OTHER_SAME


def _slots(profile: dict) -> set:
    """Return a profile's availability slots, falling back to legacy free text."""
    slots = {s for s in profile.get("availability_slots") or [] if s}
    if not slots and "fleksibel" in _norm(profile.get("availability")):
        slots = {FLEXIBLE_SLOT}
    return slots


def time_overlap(user: dict, cand: dict) -> float:
    """Score shared weekly availability slots (0 if either has none).

    Result is shared slots / size of the smaller slot set, so a candidate who
    is free at every time the user is free (or vice versa) gets 1.0.
    A "Fleksibel Setiap Hari" slot on either side counts as full overlap.
    """
    u_slots, c_slots = _slots(user), _slots(cand)
    if not u_slots or not c_slots:
        return 0.0
    if FLEXIBLE_SLOT in u_slots or FLEXIBLE_SLOT in c_slots:
        return 1.0
    return len(u_slots & c_slots) / min(len(u_slots), len(c_slots))


def compute_match(user: dict, cand: dict, comp: dict | None = None) -> MatchResult:
    """Compute the full 50-30-20 score breakdown for one candidate."""
    skill = skill_overlap(user, cand, comp)
    role = role_fit(user, cand, comp)
    time = time_overlap(user, cand)
    score = skill * SKILL_WEIGHT + role * ROLE_WEIGHT + time * TIME_WEIGHT
    return MatchResult(candidate=cand, score=score, skill=skill, role=role, time=time)


def compute_match_score(user: dict, cand: dict, comp: dict | None = None) -> float:
    """Return only the final 0..1 score for one candidate."""
    return compute_match(user, cand, comp).score


def compute_match_breakdown(
    user: dict, cand: dict, comp: dict | None = None
) -> tuple[int, int, int, int]:
    """Return (final, skill, role, time) as 0..100 ints, ready for the UI cards."""
    return compute_match(user, cand, comp).percents()


def rank_candidates(
    user: dict,
    candidates: list[dict],
    comp: dict | None = None,
    role_filter: str | None = None,
    query: str = "",
) -> list[MatchResult]:
    """Score, filter, and sort candidates from highest to lowest score.

    role_filter keeps only candidates with exactly that role; query keeps
    candidates whose name, campus, major, or skills contain the text.
    Ties are broken alphabetically by name so the order is stable.
    """
    q = _norm(query)
    results = []
    for cand in candidates:
        if role_filter and cand.get("role") != role_filter:
            continue
        if q:
            haystack = " ".join([
                str(cand.get("name", "")),
                str(cand.get("campus", "")),
                str(cand.get("major", "")),
                " ".join(cand.get("skills") or []),
            ]).lower()
            if q not in haystack:
                continue
        results.append(compute_match(user, cand, comp))
    results.sort(key=lambda r: (-r.score, _norm(r.candidate.get("name"))))
    return results
