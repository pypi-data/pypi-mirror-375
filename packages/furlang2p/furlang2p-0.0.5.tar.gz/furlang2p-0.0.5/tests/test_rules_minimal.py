# ruff: noqa: I001
from __future__ import annotations

import pytest

from furlan_g2p.g2p.rules import orth_to_ipa_basic


# These smoke tests are intentionally narrow and only check the few patterns
# implemented in orth_to_ipa_basic. Gold authoritative checks remain in the lexicon tests.


@pytest.mark.parametrize(
    "word,expected",
    [
        ("cûr", "kuːr"),  # circumflex length + k
        ("glaç", "glatʃ"),  # ç -> tʃ
        ("glace", "glatʃe"),  # ce -> tʃe
        ("cjaval", "caˈval"),  # cj -> c, rough stress heuristic (optional)
    ],
)
def test_minimal_rules(word: str, expected: str) -> None:
    assert orth_to_ipa_basic(word) == expected
