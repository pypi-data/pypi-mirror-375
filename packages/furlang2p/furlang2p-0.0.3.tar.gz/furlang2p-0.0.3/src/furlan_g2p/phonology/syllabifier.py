"""Syllabification helpers."""

from __future__ import annotations

from collections.abc import Iterable

from ..core.interfaces import ISyllabifier


def _is_vowel(ph: str) -> bool:
    return ph[0] in "aeiou"


class Syllabifier(ISyllabifier):
    """Basic syllabifier using onset maximization.

    Consonant clusters between vowels are split so that the last consonant
    begins the following syllable; clusters ending in ``r``, ``l`` or ``j`` are
    allowed as complex onsets.

    Examples
    --------
    >>> Syllabifier().syllabify(['o', 'r', 'e', 'l', 'e'])
    [['o'], ['r', 'e'], ['l', 'e']]
    """

    def syllabify(self, phonemes: Iterable[str]) -> list[list[str]]:
        """Split a phoneme sequence into syllables."""

        phs = list(phonemes)
        syllables: list[list[str]] = []
        onset: list[str] = []
        i = 0
        while i < len(phs):
            ph = phs[i]
            if _is_vowel(ph):
                nucleus = ph
                i += 1
                cluster: list[str] = []
                while i < len(phs) and not _is_vowel(phs[i]):
                    cluster.append(phs[i])
                    i += 1
                if i < len(phs):
                    if len(cluster) >= 2 and cluster[-1] in {"r", "l", "j"}:
                        coda = cluster[:-2]
                        next_onset = cluster[-2:]
                    else:
                        coda = cluster[:-1]
                        next_onset = cluster[-1:]
                    syllables.append(onset + [nucleus] + coda)
                    onset = next_onset
                else:
                    syllables.append(onset + [nucleus] + cluster)
                    onset = []
            else:
                onset.append(ph)
                i += 1
        if onset:
            if syllables:
                syllables[-1].extend(onset)
            else:
                syllables.append(onset)
        return syllables


__all__ = ["Syllabifier"]
