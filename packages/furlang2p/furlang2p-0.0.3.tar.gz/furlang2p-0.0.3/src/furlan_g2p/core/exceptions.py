"""Custom exception hierarchy for FurlanG2P."""

from __future__ import annotations


class FurlanG2PError(Exception):
    """Base exception for FurlanG2P."""


class NormalizationError(FurlanG2PError):
    """Raised when normalization fails."""


class TokenizationError(FurlanG2PError):
    """Raised when tokenization fails."""


class G2PError(FurlanG2PError):
    """Raised when G2P conversion fails."""


class PhonologyError(FurlanG2PError):
    """Raised for syllabification/stress assignment errors."""


__all__ = [
    "FurlanG2PError",
    "NormalizationError",
    "TokenizationError",
    "G2PError",
    "PhonologyError",
]
