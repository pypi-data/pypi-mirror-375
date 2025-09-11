"""Stress assignment helpers (skeleton)."""

from __future__ import annotations

from ..core.interfaces import IStressAssigner


class StressAssigner(IStressAssigner):
    """Very small stress assignment helper.

    Friulian words are generally stressed on the penultimate syllable and a
    grave accent is used to mark exceptions, while a circumflex indicates a
    long stressed vowel [1] [2].  This helper applies primary stress to the
    penultimate syllable as a simple heuristic.

    Examples
    --------
    >>> StressAssigner().assign_stress([['o'], ['r', 'e'], ['l', 'e']])
    [['o'], ['ˈr', 'e'], ['l', 'e']]
    """

    # References
    # ----------
    # [1] ARLeF. (2017). *La grafie uficiâl de lenghe furlane*, §10.
    # [2] Omniglot. Friulian language.

    def assign_stress(self, syllables: list[list[str]]) -> list[list[str]]:
        """Apply stress markers to ``syllables`` using a penultimate rule."""

        if not syllables:
            return []
        out = [list(s) for s in syllables]
        idx = max(0, len(out) - 2)
        out[idx][0] = "ˈ" + out[idx][0]
        return out


__all__ = ["StressAssigner"]
