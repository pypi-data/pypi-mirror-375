"""Tests for the experimental normalizer."""

import unicodedata
from collections.abc import Callable
from typing import Any, TypeVar, cast

from hypothesis import given as _given
from hypothesis import strategies as st

from furlan_g2p.normalization.experimental_normalizer import ExperimentalNormalizer

F = TypeVar("F", bound=Callable[..., Any])


def given(*args: Any, **kwargs: Any) -> Callable[[F], F]:
    return cast(Callable[[F], F], _given(*args, **kwargs))


norm = ExperimentalNormalizer()


def test_apostrophes_and_tokenization() -> None:
    text = "L’cjase, ‘bêle’!"
    assert norm.normalize(text) == ["l'cjase", "_", "bêle", "__"]


def test_nfc_normalization() -> None:
    # "a" + COMBINING CIRCUMFLEX should collapse to single code point
    text = "a\u0302"
    tokens = norm.normalize(text)
    assert tokens == ["â"]
    # ensure the token is NFC
    assert unicodedata.is_normalized("NFC", tokens[0])


ALPHABET = "abcçdefghilmnopqrstuvzâêîôûàèìòù'’ \t.,!?;:"


@given(st.text(alphabet=ALPHABET, max_size=20))
def test_idempotence(s: str) -> None:
    tokens = norm.normalize(s)
    recombined = " ".join(tokens)
    assert norm.normalize(recombined) == tokens
