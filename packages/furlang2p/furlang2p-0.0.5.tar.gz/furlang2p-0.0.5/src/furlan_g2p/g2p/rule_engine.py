"""Experimental rule-based orthography to IPA converter.

This module implements a small ordered set of rules derived from the official
ARLeF orthography guidelines and a few cited lemmas.  It is intentionally
limited and exists in parallel to the unfinished public API.
"""

import unicodedata
from functools import lru_cache

from ..phonology import canonicalize_ipa

# Digraph precedence handled explicitly in the main loop to avoid regex backtracking.
# Vowel inventory for quick context checks.
_VOWELS = "aâeêiîoôuûàèìòù"
_LONG_VOWELS = {
    "â": "aː",
    "ê": "eː",
    "î": "iː",
    "ô": "oː",
    "û": "uː",
}


def _is_vowel(ch: str) -> bool:
    return ch in _VOWELS


def _between_vowels(word: str, i: int) -> bool:
    return 0 < i < len(word) - 1 and _is_vowel(word[i - 1]) and _is_vowel(word[i + 1])


class RuleEngine:
    """Convert Friulian orthography to a narrow subset of IPA.

    The rules are ordered roughly from longest match (digraphs) to single
    letters.  They cover only a handful of contrasts needed by the unit tests:

    - ``cj`` → ``c`` and ``gj`` → ``ɟ`` (palatal stops) [ARLeF GRAFIE].
    - ``ch``/``gh`` harden ``c``/``g`` before front vowels.
    - ``c`` before ``e i ê î`` → ``tʃ``; ``ç`` → ``tʃ`` elsewhere.
    - Intervocalic ``s`` → ``z`` but ``ss`` stays ``s``.
    - Long vowels with circumflex get a length mark.

    Stress assignment, sandhi and many other phenomena are intentionally out of
    scope for now.
    """

    def __init__(self) -> None:
        pass

    @lru_cache(maxsize=2048)  # noqa: B019 - deliberate cache on bound method
    def convert(self, word: str) -> str:
        """Return a best-effort IPA transcription of ``word``.

        The implementation is deterministic and side-effect free, making it safe
        to cache.
        """
        if not word:
            return "/"

        s = unicodedata.normalize("NFC", word.lower())
        out: list[str] = []
        i = 0
        while i < len(s):
            if s.startswith("cj", i):
                out.append("c")
                i += 2
                continue
            if s.startswith("gj", i):
                out.append("ɟ")
                i += 2
                continue
            if s.startswith("ch", i):
                out.append("k")
                i += 2
                continue
            if s.startswith("gh", i):
                out.append("g")
                i += 2
                continue
            if s.startswith("gn", i):
                out.append("ɲ")
                i += 2
                continue
            if s.startswith("ss", i):
                out.append("s")
                i += 2
                continue

            ch = s[i]
            if ch == "ç":
                out.append("tʃ")
            elif ch == "c":
                nxt = s[i + 1] if i + 1 < len(s) else ""
                out.append("tʃ" if nxt in "eêiî" else "k")
            elif ch == "s":
                out.append("z" if _between_vowels(s, i) else "s")
            elif ch in _LONG_VOWELS:
                out.append(_LONG_VOWELS[ch])
            elif ch in _VOWELS:
                out.append({"e": "e", "o": "o"}.get(ch, ch))
            elif ch == "j":
                out.append("j")
            elif ch == "g":
                out.append("g")
            elif ch == "r":
                out.append("r")
            else:
                out.append(ch)
            i += 1
        return canonicalize_ipa("".join(out))


__all__ = ["RuleEngine"]
