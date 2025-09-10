"""Non-gold composition tests.

These tests only verify that IPA strings from gold lemmas compose without sandhi
when forming short phrases.  The resulting phrase pronunciations are *not*
authoritative.
"""

from furlan_g2p.g2p.lexicon import Lexicon


def test_isule_cjase_phrase() -> None:
    lex = Lexicon.load_seed()
    words = ["ìsule", "cjase"]
    ipa = [lex.get(w) or "" for w in words]
    assert all(ipa)
    assert " ".join(ipa) == "ˈizule ˈcaze"


def test_glace_cjandele_phrase() -> None:
    lex = Lexicon.load_seed()
    words = ["glace", "cjandele"]
    ipa = [lex.get(w) or "" for w in words]
    assert all(ipa)
    assert " ".join(ipa) == "ˈglatʃe caɲˈdɛle"
