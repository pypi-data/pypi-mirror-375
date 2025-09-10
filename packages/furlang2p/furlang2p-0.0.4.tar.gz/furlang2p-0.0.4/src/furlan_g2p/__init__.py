"""FurlanG2P public API."""

from __future__ import annotations

from .__about__ import __version__
from .core.interfaces import (
    IG2PPhonemizer,
    INormalizer,
    IStressAssigner,
    ISyllabifier,
    ITokenizer,
)
from .g2p.phonemizer import G2PPhonemizer
from .normalization.normalizer import Normalizer
from .phonology.stress import StressAssigner
from .phonology.syllabifier import Syllabifier
from .tokenization.tokenizer import Tokenizer

version = __version__

__all__ = [
    "version",
    "INormalizer",
    "ITokenizer",
    "IG2PPhonemizer",
    "ISyllabifier",
    "IStressAssigner",
    "Normalizer",
    "Tokenizer",
    "G2PPhonemizer",
    "Syllabifier",
    "StressAssigner",
]
