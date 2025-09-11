"""Canonical phoneme inventory used by FurlanG2P."""

from __future__ import annotations

PHONEME_INVENTORY: list[str] = [
    # vowels
    "a",
    "e",
    "i",
    "o",
    "u",
    "ɛ",
    "ɔ",
    # length and stress markers
    "ː",
    "ˈ",
    # consonants
    "p",
    "b",
    "t",
    "d",
    "k",
    "g",
    "c",
    "ɟ",
    "f",
    "v",
    "s",
    "z",
    "ʃ",
    "r",
    "l",
    "m",
    "n",
    "ɲ",
    "j",
    # affricate
    "tʃ",
    # pauses
    "_",
    "__",
]


__all__ = ["PHONEME_INVENTORY"]
