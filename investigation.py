"""Pure, deterministic helpers for evidence provenance and bounded AI suggestions.

Never interpret either user reports or model suggestions as sender authentication.
"""
import re

KINDS = frozenset({"company_careers", "company_contact", "other"})
ORIGINS = frozenset({"independent", "message", "ai"})
QUESTION_LIBRARY = {
    "employer": "Find the organization's official site without following the sender's links. Does an independently located channel acknowledge this specific sender?",
    "role": "On an independently located careers page, does this role exist? A listing by itself cannot authenticate the recruiter.",
    "payment": "Does the independently located employer explicitly require any payment? Stop before sending money.",
    "contact": "Can you reach the employer using contact details you found independently, not from the message or an AI response?",
    "other": "What independently obtained record would support or contradict this specific claim?",
}
_SIGNAL_HINTS = {
    "payment": "Treat requested payment as unverified until confirmed independently.",
    "credentials": "Do not share credentials or access codes with a recruiting contact.",
    "identity": "Do not provide identity documents through the unsolicited contact.",
    "urgency": "Avoid time pressure; verify the claimed deadline through a trusted channel.",
    "off_platform": "An off-platform move does not confirm who controls the new channel.",
    "impersonation": "A recognizable brand or job title does not authenticate the sender.",
}
# This deliberately small pattern list catches explicit denials; not a full
# semantic negation parser. Unusual wording remains uncertain, never 'safe'.
_DENIAL = re.compile(
    r"(?:\b(?:never|don't|do not|does not|won't|will not|would not|"
    r"must not|should not|cannot|can't|not required to|"
    r"no need to|not asked to)\b(?:\W+\w+){0,9})$"
    r"|\b(?:no|without|zero|free of)\b(?:\W+\w+){0,3}$",
    re.I,
)
_CONTRAST = re.compile(r"\b(?:but|however|instead|although|yet)\b", re.I)


def is_explicit_denial(text, start):
    """Recognize a nearby explicit denial, not arbitrary distant negations."""
    pre = text[max(0, start - 115):start]
    pre = re.split(r"(?<=[.;!?\n])", pre)[-1]
    pre = _CONTRAST.split(pre)[-1]
    return bool(_DENIAL.search(pre))


def quoted_questions(claims):
    """Model quotes are only *questions to verify*, never supporting evidence."""
    found = []
    for claim in claims[:5]:
        if isinstance(claim, dict) and claim.get("category") in QUESTION_LIBRARY:
            entry = {
                "quote": claim["snippet"],
                "question": QUESTION_LIBRARY[claim["category"]],
                "category": claim["category"],
            }
            if entry not in found:
                found.append(entry)
    return found


def bounded_model_signals(message, signals):
    """Drop invented excerpts and untrusted free-form model explanations."""
    accepted = []
    if not isinstance(signals, list):
        return accepted
    for item in signals[:6]:
        if not isinstance(item, dict):
            continue
        snippet, kind = item.get("snippet"), item.get("kind")
        if (
            isinstance(snippet, str) and 2 <= len(snippet) <= 200
            and snippet in message and kind in _SIGNAL_HINTS
            and {"snippet": snippet, "kind": kind} not in
            [{"snippet": a["snippet"], "kind": a["kind"]} for a in accepted]
        ):
            # Clear denials must not be displayed as positive risk requests.
            if kind in {"payment", "credentials", "identity"}:
                pos = message.find(snippet)
                if is_explicit_denial(message, pos):
                    continue
            accepted.append({
                "snippet": snippet,
                "kind": kind,
                "explanation": _SIGNAL_HINTS[kind],
                "interpretation": "hypothesis_only",
            })
        if len(accepted) == 3:
            break
    return accepted


def provenance_graph(items):
    """Compute ancestor sets for all valid directed edges in source notes.

    Supports a list of predecessors or a legacy derived_from index.
    Index 0 is the first note; 'message'/'ai' are separate untrusted roots.
    All independent labels remain self-reported and unauthenticated.
    """
    if not isinstance(items, list) or len(items) > 10:
        raise ValueError("Up to ten evidence notes are allowed")
    nodes, edges = [], []
    accepted, collapsed, dependent = [], [], []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError("Invalid evidence note")
        kind, source, observation = (item.get(k) for k in ("kind", "source", "observation"))
        if (kind not in KINDS or source not in ORIGINS or not isinstance(observation, str)
                or not observation.strip() or len(observation) > 300):
            raise ValueError("Invalid evidence note")
        parents = item.get("derived_from", [])
        if parents is None:
            parents = []
        if type(parents) is int:
            parents = [parents]
        if (not isinstance(parents, list) or len(parents) > 10 or
                any(type(p) is not int or p < 0 or p >= i for p in parents) or
                len(parents) != len(set(parents))):
            raise ValueError("Invalid evidence dependency")
        roots = ({source} if source != "independent" else set())
        if source in {"message", "ai"}:
            edges.append({"from": source, "to": i, "relation": "origin"})
        for p in parents:
            roots.update(dependent[p])
            edges.append({"from": p, "to": i, "relation": "derived"})
        dependent.append(roots)
        collapse = bool(roots)
        if collapse and source == "independent":
            collapsed.append(i)
        if not collapse:
            accepted.append({
                "kind": kind, "source": source, "observation": observation.strip(),
                "index": i, "qualification": "user_reported_only"
            })
        nodes.append({
            "id": i, "kind": kind, "observation": observation.strip(),
            "reported_origin": source,
            "parents": parents, "tainted_by": sorted(roots),
            "classification": ("source_collapse" if collapse and source == "independent"
                               else "dependent" if collapse
                               else "self_reported_independent")
        })
    return {
        "status": "unverified", "sender_authenticated": False,
        "nodes": nodes, "edges": edges,
        "accepted_evidence": accepted, "source_collapses": collapsed,
        "remaining_questions": [
            "Is this page or person authentic? A plausible URL or job listing is not proof.",
            "Can an independently located employer channel confirm this particular sender?"
        ],
        "method": "user_reported_provenance_not_source_authentication"
    }
