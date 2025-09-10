"""Sentence and word tokenization utilities (skeleton)."""

from __future__ import annotations

import re

from ..config.schemas import TokenizerConfig
from ..core.interfaces import ITokenizer


class Tokenizer(ITokenizer):
    """Sentence and word tokenizer.

    The implementation is intentionally simple and aims only to provide the
    basic functionality required by the tests.  Sentences are split on ``.``,
    ``!`` and ``?`` followed by whitespace; words are extracted as contiguous
    alphabetic sequences (including accented letters and apostrophes).

    Examples
    --------
    >>> t = Tokenizer()
    >>> t.split_sentences("A. B!")
    ['A.', 'B!']
    >>> t.split_words("Bêle cjase!")
    ['bêle', 'cjase']
    """

    def __init__(self, config: TokenizerConfig | None = None) -> None:
        self.config = config or TokenizerConfig()

    def split_sentences(self, text: str) -> list[str]:
        """Split ``text`` into sentences.

        Parameters
        ----------
        text:
            Raw text string.

        Returns
        -------
        list[str]
            Sentence fragments including their terminal punctuation.
        """

        sentences = [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
        return sentences

    def split_words(self, sentence: str) -> list[str]:
        """Split a ``sentence`` into word tokens.

        Parameters
        ----------
        sentence:
            Sentence to tokenize.

        Returns
        -------
        list[str]
            Lowercase word tokens without punctuation.
        """

        return re.findall(r"[a-zâêîôûàèìòùç'’]+", sentence.lower())


__all__ = ["Tokenizer"]
