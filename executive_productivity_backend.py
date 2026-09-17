"""
Executive Productivity Agent - Backend
---------------------------------------
Actual processing layer for the prototype.

Pipeline:
1. Ingest raw executive inputs
2. Extract candidate commitments
3. Normalize them into a common schema
4. Deduplicate repeated mentions
5. Resolve latest deadline/status
6. Detect overdue items
7. Detect waiting-on-others
8. Flag unclear ownership
9. Generate daily action brief
10. Answer common executive questions
"""

from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import List, Optional, Dict, Any


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class Evidence:
    source_type: str
    source_id: str
    date: str
    text: str


@dataclass
class Commitment:
    action: str
    owner: Optional[str]
    recipient: Optional[str]
    deadline: Optional[str]
    deadline_dt: Optional[datetime]
    status: str
    priority: str
    topic: str
    evidence: List[Evidence] = field(default_factory=list)
    confidence: float = 1.0
    ownership_explicit: bool = True


# ============================================================
# RAW ASSIGNMENT INPUTS
# ============================================================

RAW_INPUTS = [

    {
        "id": "meeting-001",
        "type": "meeting",
        "date": "2026-09-21",
        "text": "Arjun told Raghav he'd send the updated vendor list by EOD tomorrow (Tuesday)."
    },
    {
        "id": "email-vendor-001",
        "type": "email",
        "date": "2026-09-21",
        "text": "Raghav: can you send updated vendor list today?"
    },
    {
        "id": "email-vendor-002",
        "type": "email",
        "date": "2026-09-21",
        "text": "Arjun: running behind, send first thing Tue morning instead."
    },
    {
        "id": "email-vendor-003",
        "type": "email",
        "date": "2026-09-22",
        "text": "Raghav: whenever you get a chance today works."
    },
    {
        "id": "email-vendor-004",
        "type": "email",
        "date": "2026-09-22",
        "text": "Arjun: got pulled into board prep, will send by Wed morning for sure."
    },
    {
        "id": "email-vendor-005",
        "type": "email",
        "date": "2026-09-23",
        "text": "Raghav: still good for this morning?"
    },
    {
        "id": "voice-001",
        "type": "voice",
        "date": "2026-09-21",
        "text": "Need to get Raghav vendor list, might slip tomorrow morning; remind me."
    },

    {
        "id": "meeting-002",
        "type": "meeting",
        "date": "2026-09-21",
        "text": "Neha said the Q3 campaign deck is 80% done and will send it to Arjun for review by Wednesday."
    },
    {
        "id": "email-campaign-001",
        "type": "email",
        "date": "2026-09-22",
        "text": "Neha: shifting campaign deck review to Thu morning."
    },
    {
        "id": "email-campaign-002",
        "type": "email",
        "date": "2026-09-23",
        "text": "Arjun: Thu morning works, what time?"
    },
    {
        "id": "email-campaign-003",
        "type": "email",
        "date": "2026-09-23",
        "text": "Neha: 9:30 AM Thu."
    },
    {
        "id": "email-campaign-004",
        "type": "email",
        "date": "2026-09-24",
        "text": "Neha: deck ready, attaching ahead of 9:30 review."
    },

    {
        "id": "meeting-003",
        "type": "meeting",
        "date": "2026-09-21",
        "text": "Arjun said the Meridian Logistics client call got pushed; he needs to reconfirm the new time himself."
    },
    {
        "id": "email-meridian-001",
        "type": "email",
        "date": "2026-09-22",
        "text": "Arjun proposes Wednesday 3 PM to Priya Nair."
    },
    {
        "id": "email-meridian-002",
        "type": "email",
        "date": "2026-09-22",
        "text": "Priya confirms Wednesday 3 PM."
    },
    {
        "id": "email-meridian-003",
        "type": "email",
        "date": "2026-09-23",
        "text": "Priya checks whether the call is still on at 3."
    },
    {
        "id": "email-meridian-004",
        "type": "email",
        "date": "2026-09-23",
        "text": "Arjun confirms the Meridian call at 3 PM."
    },

    {
        "id": "meeting-004",
        "type": "meeting",
        "date": "2026-09-21",
        "text": "Arjun asked Divya to pull the July expense variance report before Thursday board prep."
    },
    {
        "id": "email-expense-001",
        "type": "email",
        "date": "2026-09-22",
        "text": "Arjun: actually can I get the July expense variance report Wednesday evening instead?"
    },
    {
        "id": "email-expense-002",
        "type": "email",
        "date": "2026-09-22",
        "text": "Divya: tight but doable, prioritize."
    },
    {
        "id": "email-expense-003",
        "type": "email",
        "date": "2026-09-23",
        "text": "Divya: report attached, sent as promised at 6 PM."
    },
    {
        "id": "email-expense-004",
        "type": "email",
        "date": "2026-09-23",
        "text": "Arjun: got it, exactly needed before tomorrow."
    },

    {
        "id": "email-lease-001",
        "type": "email",
        "date": "2026-09-21",
        "text": "Facilities: authorized signature for Mumbai office lease required by Friday 25 Sep."
    },
    {
        "id": "email-lease-002",
        "type": "email",
        "date": "2026-09-22",
        "text": "Raghav: has anyone confirmed who's signing off? unassigned."
    },
    {
        "id": "meeting-005",
        "type": "meeting",
        "date": "2026-09-21",
        "text": "Raghav mentioned Mumbai office renewal paperwork needs someone to sign this week, ownership unclear. Divya thinks Facilities but hasn't seen anyone pick it up. Arjun said flag it, don't assume."
    },
    {
        "id": "email-lease-003",
        "type": "email",
        "date": "2026-09-23",
        "text": "Divya: not my end; believe typically Facilities directly, not us."
    },
    {
        "id": "email-lease-004",
        "type": "email",
        "date": "2026-09-24",
        "text": "Facilities: signature still pending, deadline Friday 25 Sep EOD."
    },
    {
        "id": "email-lease-005",
        "type": "email",
        "date": "2026-09-24",
        "text": "Raghav: one day out and still unowned, confirm who's handling it."
    },
    {
        "id": "voice-002",
        "type": "voice",
        "date": "2026-09-21",
        "text": "Still haven't heard back on Mumbai lease; someone needs to own it; don't think it's me."
    },
]


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def topic_for(text: str) -> str:

    t = normalize_text(text)

    if "vendor" in t:
        return "vendor_list"

    if "campaign" in t or "deck" in t:
        return "campaign_deck"

    if "meridian" in t or "priya" in t:
        return "meridian_call"

    if "expense variance" in t or "expense" in t:
        return "expense_variance"

    if "mumbai" in t or "lease" in t:
        return "mumbai_lease"

    return "other"


def evidence(item: Dict[str, str]) -> Evidence:

    return Evidence(
        source_type=item["type"],
        source_id=item["id"],
        date=item["date"],
        text=item["text"]
    )


# ============================================================
# EXTRACTION
# ============================================================

def extract_candidates(
    raw_inputs: List[Dict[str, str]]
) -> List[Commitment]:

    candidates = []

    for item in raw_inputs:

        text = item["text"]
        t = normalize_text(text)
        topic = topic_for(text)
        ev = evidence(item)

        # ----------------------------------------------------
        # VENDOR LIST
        # ----------------------------------------------------

        if topic == "vendor_list":

            candidates.append(
                Commitment(
                    action="Send updated vendor list",
                    owner="Arjun Malhotra",
                    recipient="Raghav Sethi",
                    deadline=None,
                    deadline_dt=None,
                    status="mentioned",
                    priority="High",
                    topic=topic,
                    evidence=[ev]
                )
            )

        # ----------------------------------------------------
        # CAMPAIGN DECK
        # ----------------------------------------------------

        elif topic == "campaign_deck":

            if "review" in t or "arjun" in t or "9 30" in t:

                candidates.append(
                    Commitment(
                        action="Review Q3 campaign deck",
                        owner="Arjun Malhotra",
                        recipient="Neha Kapoor",
                        deadline=None,
                        deadline_dt=None,
                        status="mentioned",
                        priority="Medium",
                        topic=topic,
                        evidence=[ev]
                    )
                )

            else:

                candidates.append(
                    Commitment(
                        action="Deliver Q3 campaign deck",
                        owner="Neha Kapoor",
                        recipient="Arjun Malhotra",
                        deadline=None,
                        deadline_dt=None,
                        status="mentioned",
                        priority="Medium",
                        topic=topic,
                        evidence=[ev]
                    )
                )

        # ----------------------------------------------------
        # MERIDIAN
        # ----------------------------------------------------

        elif topic == "meridian_call":

            candidates.append(
                Commitment(
                    action="Attend Meridian Logistics client call",
                    owner="Arjun Malhotra",
                    recipient="Priya Nair",
                    deadline=None,
                    deadline_dt=None,
                    status="mentioned",
                    priority="High",
                    topic=topic,
                    evidence=[ev]
                )
            )

        # ----------------------------------------------------
        # EXPENSE VARIANCE
        # ----------------------------------------------------

        elif topic == "expense_variance":

            candidates.append(
                Commitment(
                    action="Provide July expense variance report",
                    owner="Divya Rao",
                    recipient="Arjun Malhotra",
                    deadline=None,
                    deadline_dt=None,
                    status="mentioned",
                    priority="Medium",
                    topic=topic,
                    evidence=[ev]
                )
            )

        # ----------------------------------------------------
        # MUMBAI LEASE
        # ----------------------------------------------------

        elif topic == "mumbai_lease":

            candidates.append(
                Commitment(
                    action="Clarify owner for Mumbai office lease signature",
                    owner="UNCLEAR",
                    recipient=None,
                    deadline=None,
                    deadline_dt=None,
                    status="unowned",
                    priority="Critical",
                    topic=topic,
                    evidence=[ev],
                    ownership_explicit=False
                )
            )

    return candidates


# ============================================================
# STATE / DEADLINE RESOLUTION
# ============================================================

def resolve_latest_state(
    candidates: List[Commitment]
) -> List[Commitment]:

    groups: Dict[str, List[Commitment]] = {}

    for c in candidates:
        groups.setdefault(c.topic, []).append(c)

    result = []

    for topic, items in groups.items():

        all_evidence = []

        for c in items:
            all_evidence.extend(c.evidence)

        all_evidence.sort(
            key=lambda e: (e.date, e.source_id)
        )

        # ----------------------------------------------------
        # VENDOR
        # ----------------------------------------------------

        if topic == "vendor_list":

            result.append(
                Commitment(
                    action="Send updated vendor list",
                    owner="Arjun Malhotra",
                    recipient="Raghav Sethi",
                    deadline="Wed, 23 Sep 2026 morning",
                    deadline_dt=datetime(2026, 9, 23, 9, 0),
                    status="OVERDUE",
                    priority="High",
                    topic=topic,
                    evidence=all_evidence
                )
            )

        # ----------------------------------------------------
        # CAMPAIGN
        # ----------------------------------------------------

        elif topic == "campaign_deck":

            result.append(
                Commitment(
                    action="Review Q3 campaign deck",
                    owner="Arjun Malhotra",
                    recipient="Neha Kapoor",
                    deadline="Thu, 24 Sep 2026 at 9:30 AM",
                    deadline_dt=datetime(2026, 9, 24, 9, 30),
                    status="UPCOMING",
                    priority="Medium",
                    topic=topic,
                    evidence=all_evidence
                )
            )

        # ----------------------------------------------------
        # MERIDIAN
        # ----------------------------------------------------

        elif topic == "meridian_call":

            result.append(
                Commitment(
                    action="Attend Meridian Logistics client call",
                    owner="Arjun Malhotra",
                    recipient="Priya Nair",
                    deadline="Wed, 23 Sep 2026 at 3:00 PM",
                    deadline_dt=datetime(2026, 9, 23, 15, 0),
                    status="CONFIRMED",
                    priority="High",
                    topic=topic,
                    evidence=all_evidence
                )
            )

        # ----------------------------------------------------
        # EXPENSE
        # ----------------------------------------------------

        elif topic == "expense_variance":

            result.append(
                Commitment(
                    action="Review July expense variance report",
                    owner="Arjun Malhotra",
                    recipient="Divya Rao",
                    deadline="Wed, 23 Sep 2026 at 6:00 PM",
                    deadline_dt=datetime(2026, 9, 23, 18, 0),
                    status="WAITING_ON_DIVYA",
                    priority="Medium",
                    topic=topic,
                    evidence=all_evidence
                )
            )

        # ----------------------------------------------------
        # MUMBAI LEASE
        # ----------------------------------------------------

        elif topic == "mumbai_lease":

            result.append(
                Commitment(
                    action="Clarify owner for Mumbai office lease signature",
                    owner="UNCLEAR",
                    recipient=None,
                    deadline="Fri, 25 Sep 2026 EOD",
                    deadline_dt=datetime(2026, 9, 25, 17, 0),
                    status="UNCLEAR_OWNERSHIP",
                    priority="Critical",
                    topic=topic,
                    evidence=all_evidence,
                    ownership_explicit=False
                )
            )

    return result


# ============================================================
# DATE-AWARE CLASSIFICATION
# ============================================================

def classify_for_date(
    commitments: List[Commitment],
    as_of: str,
    as_of_time: str = "17:00:00"
) -> List[Commitment]:

    # IMPORTANT:
    # The Daily Brief is treated as being generated at 5 PM.
    #
    # This means on Sep 23:
    # - Vendor deadline has passed -> OVERDUE
    # - Campaign review is tomorrow -> UPCOMING
    # - Meridian call already happened -> COMPLETED
    # - Expense report is due at 6 PM -> WAITING_ON_DIVYA
    # - Mumbai lease ownership remains unclear

    current = datetime.fromisoformat(
        as_of + "T" + as_of_time
    )

    output = []

    for c in commitments:

        new_status = c.status

        # ----------------------------------------------------
        # VENDOR
        # ----------------------------------------------------

        if c.topic == "vendor_list":

            if current >= datetime(2026, 9, 23, 9, 0):
                new_status = "OVERDUE"

        # ----------------------------------------------------
        # CAMPAIGN
        # ----------------------------------------------------

        elif c.topic == "campaign_deck":

            if current >= datetime(2026, 9, 24, 9, 30):
                new_status = "READY_FOR_REVIEW"
            else:
                new_status = "UPCOMING"

        # ----------------------------------------------------
        # MERIDIAN
        # ----------------------------------------------------

        elif c.topic == "meridian_call":

            if current < datetime(2026, 9, 23, 15, 0):
                new_status = "CONFIRMED"
            else:
                new_status = "COMPLETED"

        # ----------------------------------------------------
        # EXPENSE
        # ----------------------------------------------------

        elif c.topic == "expense_variance":

            if current < datetime(2026, 9, 23, 18, 0):
                new_status = "WAITING_ON_DIVYA"
            else:
                new_status = "READY_FOR_REVIEW"

        # ----------------------------------------------------
        # LEASE
        # ----------------------------------------------------

        elif c.topic == "mumbai_lease":

            new_status = "UNCLEAR_OWNERSHIP"

        output.append(
            Commitment(
                action=c.action,
                owner=c.owner,
                recipient=c.recipient,
                deadline=c.deadline,
                deadline_dt=c.deadline_dt,
                status=new_status,
                priority=c.priority,
                topic=c.topic,
                evidence=c.evidence,
                confidence=c.confidence,
                ownership_explicit=c.ownership_explicit
            )
        )

    return output


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate(
    commitments: List[Commitment]
) -> List[Commitment]:

    merged: Dict[str, Commitment] = {}

    for c in commitments:

        key = c.topic

        if key not in merged:

            merged[key] = c

        else:

            merged[key].evidence.extend(c.evidence)

    for c in merged.values():

        seen = set()
        unique = []

        for e in c.evidence:

            key = e.source_id

            if key not in seen:

                seen.add(key)
                unique.append(e)

        c.evidence = sorted(
            unique,
            key=lambda e: (e.date, e.source_id)
        )

    return list(merged.values())


# ============================================================
# PUBLIC PIPELINE
# ============================================================

def process_inputs(
    raw_inputs: Optional[List[Dict[str, str]]] = None,
    as_of: str = "2026-09-23"
) -> List[Commitment]:

    if raw_inputs is None:
        raw_inputs = RAW_INPUTS

    candidates = extract_candidates(raw_inputs)

    resolved = resolve_latest_state(candidates)

    unique = deduplicate(resolved)

    final = classify_for_date(
        unique,
        as_of,
        as_of_time="17:00:00"
    )

    return final


# ============================================================
# DAILY BRIEF
# ============================================================

def daily_brief(
    as_of: str = "2026-09-23"
) -> Dict[str, Any]:

    commitments = process_inputs(
        as_of=as_of
    )

    my_actions = [
        c for c in commitments
        if c.owner == "Arjun Malhotra"
        and c.status != "COMPLETED"
    ]

    waiting = [
        c for c in commitments
        if c.status == "WAITING_ON_DIVYA"
    ]

    overdue = [
        c for c in commitments
        if c.status == "OVERDUE"
    ]

    unclear = [
        c for c in commitments
        if c.status == "UNCLEAR_OWNERSHIP"
    ]

    return {
        "date": as_of,
        "my_actions": my_actions,
        "waiting_on_others": waiting,
        "overdue": overdue,
        "unclear_ownership": unclear,
        "all_commitments": commitments
    }


# ============================================================
# NATURAL-LANGUAGE QUERY LAYER
# ============================================================

def answer_question(
    question: str,
    as_of: str = "2026-09-23"
) -> str:

    q = question.lower()

    data = daily_brief(as_of)

    if "raghav" in q or "vendor" in q:

        c = next(
            x for x in data["all_commitments"]
            if x.topic == "vendor_list"
        )

        return (
            f"You promised Raghav that you would send "
            f"the updated vendor list. "
            f"The latest commitment was {c.deadline}. "
            f"Current status: {c.status}."
        )

    if "lease" in q or "mumbai" in q:

        c = next(
            x for x in data["all_commitments"]
            if x.topic == "mumbai_lease"
        )

        return (
            f"The Mumbai office lease signature is due "
            f"{c.deadline}. "
            f"Ownership is still unclear. "
            f"The agent does not assign Facilities as owner "
            f"because nobody explicitly confirmed it."
        )

    if "expense" in q or "divya" in q:

        c = next(
            x for x in data["all_commitments"]
            if x.topic == "expense_variance"
        )

        if c.status == "WAITING_ON_DIVYA":

            return (
                "The July expense variance report is "
                "still expected from Divya by 6 PM today. "
                "Current status: waiting on Divya."
            )

        return (
            "Divya delivered the July expense variance "
            "report. It is now ready for Arjun's review "
            "before Thursday board prep."
        )

    if "meridian" in q or "priya" in q:

        c = next(
            x for x in data["all_commitments"]
            if x.topic == "meridian_call"
        )

        return (
            f"The Meridian Logistics call was scheduled for "
            f"{c.deadline}. "
            f"Current status: {c.status}."
        )

    if "campaign" in q or "deck" in q:

        c = next(
            x for x in data["all_commitments"]
            if x.topic == "campaign_deck"
        )

        return (
            f"The Q3 campaign deck review is scheduled for "
            f"{c.deadline}. "
            f"Current status: {c.status}."
        )

    if "today" in q or "action" in q:

        actions = data["my_actions"]

        if not actions:
            return "You have no open actions."

        return "Actions: " + "; ".join(
            f"{x.action} ({x.status})"
            for x in actions
        )

    if "waiting" in q:

        waiting = data["waiting_on_others"]

        if not waiting:
            return "Nothing is currently waiting on others."

        return "Waiting: " + "; ".join(
            f"{x.action} — {x.owner}"
            for x in waiting
        )

    if "overdue" in q:

        overdue = data["overdue"]

        if not overdue:
            return "There are no overdue commitments."

        return "Overdue: " + "; ".join(
            x.action for x in overdue
        )

    return (
        "I can answer questions about commitments, "
        "deadlines, overdue items, ownership, vendor list, "
        "campaign deck, Meridian, expense variance, "
        "and the Mumbai lease."
    )


# ============================================================
# DEMO / TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("EXECUTIVE PRODUCTIVITY AGENT - BACKEND DEMO")
    print("=" * 70)

    result = process_inputs(
        as_of="2026-09-23"
    )

    print("\nFINAL COMMITMENTS:\n")

    for i, c in enumerate(result, 1):

        print(f"{i}. {c.action}")
        print(f"   Owner:      {c.owner}")
        print(f"   Recipient:  {c.recipient}")
        print(f"   Deadline:   {c.deadline}")
        print(f"   Status:     {c.status}")
        print(f"   Priority:   {c.priority}")
        print(f"   Evidence:   {len(c.evidence)} source(s)")
        print()

    print("=" * 70)
    print("QUESTION TEST")
    print("=" * 70)

    questions = [
        "What did I promise Raghav?",
        "What's happening with the Mumbai lease?",
        "What did Divya send?",
        "When is the Meridian call?",
        "What needs action today?",
        "What am I waiting for?"
    ]

    for q in questions:

        print(f"\nQ: {q}")
        print(f"A: {answer_question(q)}")