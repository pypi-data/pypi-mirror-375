"""Smoke tests for importability."""

from __future__ import annotations

import furlan_g2p
from furlan_g2p import G2PPhonemizer, Normalizer, StressAssigner, Syllabifier, Tokenizer


def test_imports() -> None:
    assert furlan_g2p
    assert all([Normalizer, Tokenizer, G2PPhonemizer, Syllabifier, StressAssigner])
