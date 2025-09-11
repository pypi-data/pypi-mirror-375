"""Abstract base interfaces for FurlanG2P components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable


class INormalizer(ABC):
    """Interface for text normalization."""

    @abstractmethod
    def normalize(self, text: str) -> str:
        """Return a normalized text string."""
        raise NotImplementedError


class ITokenizer(ABC):
    """Interface for sentence/word tokenization."""

    @abstractmethod
    def split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        raise NotImplementedError

    @abstractmethod
    def split_words(self, sentence: str) -> list[str]:
        """Split a sentence into tokens/words (keeping pause markers if any)."""
        raise NotImplementedError


class IG2PPhonemizer(ABC):
    """Interface for grapheme-to-phoneme conversion."""

    @abstractmethod
    def to_phonemes(self, tokens: Iterable[str]) -> list[str]:
        """Map tokens to a flat sequence of phoneme symbols."""
        raise NotImplementedError


class ISyllabifier(ABC):
    """Interface for syllabification."""

    @abstractmethod
    def syllabify(self, phonemes: Iterable[str]) -> list[list[str]]:
        """Return a list of syllables, each as a list of phoneme strings."""
        raise NotImplementedError


class IStressAssigner(ABC):
    """Interface for lexical or post-lexical stress assignment."""

    @abstractmethod
    def assign_stress(self, syllables: list[list[str]]) -> list[list[str]]:
        """Return syllables with stress markers applied."""
        raise NotImplementedError


__all__ = [
    "INormalizer",
    "ITokenizer",
    "IG2PPhonemizer",
    "ISyllabifier",
    "IStressAssigner",
]
