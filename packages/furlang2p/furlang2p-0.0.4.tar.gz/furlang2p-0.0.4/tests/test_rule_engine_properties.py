"""Property tests for the experimental rule engine."""

from collections.abc import Callable
from typing import Any, TypeVar, cast

from hypothesis import given as _given
from hypothesis import strategies as st

from furlan_g2p.g2p.rule_engine import RuleEngine

F = TypeVar("F", bound=Callable[..., Any])


def given(*args: Any, **kwargs: Any) -> Callable[[F], F]:
    return cast(Callable[[F], F], _given(*args, **kwargs))


ALPHABET = "abcçdefghijlmnoprstuvzâêîôûàèìòù"
IPA_CHARS = set("abcdefhijklmnoprstuvzàèìòùɟɲʃːˈɛɔg")


@given(st.text(alphabet=ALPHABET, min_size=1, max_size=10))
def test_outputs_are_ipa_only(s: str) -> None:
    eng = RuleEngine()
    out = eng.convert(s)
    assert all(ch in IPA_CHARS for ch in out)
