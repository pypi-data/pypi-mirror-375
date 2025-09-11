"""Common type aliases used across the project."""

from __future__ import annotations

from collections.abc import Sequence
from typing import NewType

Phoneme = NewType("Phoneme", str)
PhonemeSeq = NewType("PhonemeSeq", str)
Token = NewType("Token", str)

StrSequence = Sequence[str]
StrList = list[str]
StrTuple = tuple[str, ...]
StrDict = dict[str, str]

__all__ = [
    "Phoneme",
    "PhonemeSeq",
    "Token",
    "StrSequence",
    "StrList",
    "StrTuple",
    "StrDict",
]
