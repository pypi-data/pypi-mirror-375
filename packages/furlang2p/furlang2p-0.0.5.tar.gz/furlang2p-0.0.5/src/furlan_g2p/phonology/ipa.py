"""IPA helpers for canonical symbol management."""

from __future__ import annotations

import re

_REPLACEMENTS: dict[str, str] = {
    "t͡ʃ": "tʃ",
    "ɡ": "g",
    "ɳ": "ɲ",
}


def canonicalize_ipa(ipa: str) -> str:
    """Return a canonical representation of ``ipa``.

    This helper normalizes a few symbol variants used in the seed data and
    rule-based converters:

    - removes leading/trailing slashes and syllable separators ``.``;
    - maps ``t͡ʃ`` → ``tʃ`` and ``ɡ`` → ``g``;
    - normalizes ``ɳ`` to ``ɲ``;
    - collapses multiple spaces.

    Parameters
    ----------
    ipa:
        Raw IPA string.

    Returns
    -------
    str
        Canonical IPA string.
    """

    s = ipa.strip()
    if s.startswith("/") and s.endswith("/"):
        s = s[1:-1]
    s = s.replace(".", "")
    for src, tgt in _REPLACEMENTS.items():
        s = s.replace(src, tgt)
    s = re.sub(r"\s+", " ", s).strip()
    return s


__all__ = ["canonicalize_ipa"]
