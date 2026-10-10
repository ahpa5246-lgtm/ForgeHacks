"""Offline source-lead extraction. No URL browsing, DNS or authentication."""
import re
from urllib.parse import urlsplit

URL_RE = re.compile(r"https?://[^\s<>'\"]+", re.I)
SAFE_HOST = re.compile(r"^[a-z0-9.-]{1,253}$", re.I)
SAFE_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.I)


def message_source_seeds(message):
    if not isinstance(message, str):
        return []
    hosts, notes = set(), []
    for match in URL_RE.finditer(message):
        candidate=match.group(0).rstrip(".,;!?)]}")
        try:
            parsed=urlsplit(candidate)
            host=(parsed.hostname or "").strip(".").lower()
        except ValueError:
            continue
        if (parsed.scheme.lower() not in {"http","https"} or
            not host or not SAFE_HOST.fullmatch(host) or
            not all(SAFE_LABEL.fullmatch(x) for x in host.split(".")) or
            host in hosts):
            continue
        hosts.add(host)
        notes.append({
            "kind": "other",
            "source": "message",
            "observation": "The unverified recruiter message supplied a link on host "
                           +host+". Domain text only; not visited or authenticated.",
        })
        if len(notes)==3:
            break
    return notes
