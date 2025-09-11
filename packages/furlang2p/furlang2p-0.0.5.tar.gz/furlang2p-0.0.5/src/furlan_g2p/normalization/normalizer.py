"""Text normalization utilities (skeleton)."""

from __future__ import annotations

import re

from ..config.schemas import NormalizerConfig
from ..core.exceptions import NormalizationError  # noqa: F401
from ..core.interfaces import INormalizer


class Normalizer(INormalizer):
    """Simple text normalizer.

    The current implementation performs very lightweight normalization by
    lowercasing the input and collapsing consecutive whitespace characters.

    Examples
    --------
    >>> Normalizer().normalize("  Bêle  CJASE  ")
    'bêle cjase'
    """

    def __init__(self, config: NormalizerConfig | None = None) -> None:
        self.config = config or NormalizerConfig()

    def normalize(self, text: str) -> str:
        """Normalize raw input text into a canonical, speakable form.

        Parameters
        ----------
        text:
            Raw input text.

        Returns
        -------
        str
            Normalized text.

        Raises
        ------
        NormalizationError
            If the text cannot be normalized.
        """

        if not isinstance(text, str):  # pragma: no cover - defensive programming
            raise NormalizationError("Input must be a string")

        # Collapse whitespace and lowercase.
        normalized = re.sub(r"\s+", " ", text.strip()).lower()
        return normalized


__all__ = ["Normalizer"]
