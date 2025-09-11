"""Additional gold lemma tests sourced from Wiktionary.

Each test asserts the exact IPA transcription as provided on the lemma's
Wiktionary page.  These are "gold" items: they come from curated sources and
should only fail if the lexicon diverges from the cited reference.
"""

from furlan_g2p.g2p.lexicon import Lexicon


def _lex() -> Lexicon:
    return Lexicon.load_seed()


def test_isule() -> None:
    """https://en.wiktionary.org/wiki/%C3%ACsule"""
    assert _lex().get("ìsule") == "ˈizule"


def test_glace() -> None:
    """https://en.wiktionary.org/wiki/glace"""
    assert _lex().get("glace") == "ˈglatʃe"


def test_glac_cedilla() -> None:
    """https://en.wiktionary.org/wiki/gla%C3%A7"""
    assert _lex().get("glaç") == "ˈglatʃ"


def test_cjase() -> None:
    """https://en.wiktionary.org/wiki/cjase"""
    assert _lex().get("cjase") == "ˈcaze"


def test_cjandele() -> None:
    """https://en.wiktionary.org/wiki/cjandele"""
    assert _lex().get("cjandele") == "caɲˈdɛle"
