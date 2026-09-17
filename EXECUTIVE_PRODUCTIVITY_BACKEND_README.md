# Executive Productivity Agent — Backend

This is the actual processing/backend layer for the Executive Productivity Agent assignment.

## Pipeline

Raw emails/meeting notes/calendar/voice notes
-> commitment extraction
-> normalization
-> deduplication
-> latest-state resolution
-> deadline/status classification
-> ownership ambiguity detection
-> daily brief
-> question answering

## Important behaviors demonstrated

- Same vendor-list commitment mentioned in meeting, emails and voice note becomes ONE commitment.
- Latest vendor-list deadline becomes Wednesday morning.
- Vendor-list item becomes OVERDUE on Wednesday after the deadline.
- Meridian scheduling changes into a CONFIRMED attendance action after both sides confirm.
- Expense report changes from WAITING_ON_DIVYA to READY_FOR_REVIEW after delivery.
- Mumbai lease is explicitly marked UNCLEAR_OWNERSHIP rather than assigning Facilities automatically.
- Source evidence is retained for explainability.

## Run

```bash
python executive_productivity_backend.py
```

No OpenAI API key is required for this prototype backend.

The extraction function is intentionally separated from the state engine, so an LLM can later be plugged into `extract_candidates()` without rewriting deduplication, deadline tracking, ownership logic, or the UI.
