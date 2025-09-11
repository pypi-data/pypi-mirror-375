"""Grapheme-to-phoneme conversion utilities (skeleton)."""

from __future__ import annotations

from collections.abc import Iterable

from ..core.interfaces import IG2PPhonemizer
from .lexicon import Lexicon
from .rules import PhonemeRules, orth_to_ipa_basic


def _segment_ipa(ipa: str) -> list[str]:
    """Split a canonical IPA string into phoneme symbols."""

    digraphs = ["tʃ", "dʒ", "aː", "eː", "iː", "oː", "uː"]
    segments: list[str] = []
    i = 0
    while i < len(ipa):
        for d in digraphs:
            if ipa.startswith(d, i):
                segments.append(d)
                i += len(d)
                break
        else:
            segments.append(ipa[i])
            i += 1
    return segments


class G2PPhonemizer(IG2PPhonemizer):
    """Phonemizer that combines a lexicon and simple rule fallback.

    Examples
    --------
    >>> G2PPhonemizer().to_phonemes(["cjase"])
    ['c', 'a', 'z', 'e']
    """

    def __init__(self, lexicon: Lexicon | None = None, rules: PhonemeRules | None = None) -> None:
        self.lexicon = lexicon or Lexicon()
        self.rules = rules or PhonemeRules()

    def to_phonemes(self, tokens: Iterable[str]) -> list[str]:
        """Convert token strings into a flat list of phoneme symbols.

        Tokens are looked up in the lexicon; if a token is absent, a minimal
        orthography-to-IPA mapping is applied as a fallback.  Stress marks are
        stripped before the sequence is segmented into individual phonemes.
        """

        phonemes: list[str] = []
        for tok in tokens:
            ipa = self.lexicon.get(tok)
            if ipa is None:
                ipa = orth_to_ipa_basic(tok)
            ipa = ipa.replace("ˈ", "")
            phonemes.extend(_segment_ipa(ipa))
        return phonemes


__all__ = ["G2PPhonemizer"]
