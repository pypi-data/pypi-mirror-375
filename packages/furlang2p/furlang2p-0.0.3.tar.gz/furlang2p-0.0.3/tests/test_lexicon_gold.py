from __future__ import annotations

import pytest

from furlan_g2p.g2p.lexicon import Lexicon

# These tests assert exact IPA from Wiktionary for specific Friulian lemmas.
# Citations:
# - cûr: https://en.wiktionary.org/wiki/c%C3%BBr
# - fûc: https://en.wiktionary.org/wiki/f%C3%BBc
# - pôc: https://en.wiktionary.org/wiki/p%C3%B4c
# - sêt: https://en.wiktionary.org/wiki/s%C3%AAt
# - fâ:  https://en.wiktionary.org/wiki/f%C3%A2
# - fîl: https://en.wiktionary.org/wiki/f%C3%AEl
# - patî: https://en.wiktionary.org/wiki/pat%C3%AE
# - sufrî: https://en.wiktionary.org/wiki/sufr%C3%AE
# - nemâl: https://en.wiktionary.org/wiki/nem%C3%A2l
# - ìsule: https://en.wiktionary.org/wiki/%C3%ACsule
# - orele: https://en.wiktionary.org/wiki/orele
# - strie: https://en.wiktionary.org/wiki/strie
# - glace: https://en.wiktionary.org/wiki/glace
# - glaç: https://en.wiktionary.org/wiki/gla%C3%A7
# - cjaval: https://en.wiktionary.org/wiki/cjaval
# - pît: https://en.wiktionary.org/wiki/p%C3%AEt
# - mûr: https://en.wiktionary.org/wiki/m%C3%BBr
# - côr: https://en.wiktionary.org/wiki/c%C3%B4r

GOLD = {
    "cûr": "kuːr",
    "fûc": "fuːk",
    "pôc": "poːk",
    "sêt": "seːt",
    "fâ": "ˈfaː",
    "fîl": "fiːl",
    "patî": "paˈti",
    "sufrî": "suˈfriː",
    "nemâl": "neˈmaːl",
    "ìsule": "ˈizule",
    "orele": "oˈrɛle",
    "strie": "ˈstriɛ",
    "glace": "ˈglatʃe",
    "glaç": "ˈglatʃ",
    "cjaval": "caˈval",
    "pît": "piːt",
    "mûr": "muːr",
    "côr": "kɔːr",
}


@pytest.fixture(scope="module")
def lex() -> Lexicon:
    return Lexicon.load_seed()


@pytest.mark.parametrize("word,ipa", GOLD.items())
def test_seed_lexicon_contains_gold(word: str, ipa: str, lex: Lexicon) -> None:
    assert lex.get(word) == ipa


def test_variants_present_for_selected(lex: Lexicon) -> None:
    # a few with known dialectal alternations
    entry = lex.get_entry("fûc")
    assert entry is not None and "fouk" in entry.variants
    entry = lex.get_entry("pôc")
    assert entry is not None and "pouk" in entry.variants
    entry = lex.get_entry("sêt")
    assert entry is not None and "seit" in entry.variants
    entry = lex.get_entry("pît")
    assert entry is not None and "peit" in entry.variants


def test_unknown_returns_none(lex: Lexicon) -> None:
    assert lex.get("nonexistent") is None
