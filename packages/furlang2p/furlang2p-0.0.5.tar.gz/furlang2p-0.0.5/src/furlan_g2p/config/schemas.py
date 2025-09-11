"""Dataclasses for configuration (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class NormalizerConfig:
    """Configuration for normalization rules."""

    units_map: dict[str, str] = field(default_factory=dict)
    acronyms_map: dict[str, str] = field(default_factory=dict)
    ordinal_map: dict[str, str] = field(default_factory=dict)
    pause_short: str = "_"
    pause_long: str = "__"


@dataclass(slots=True)
class TokenizerConfig:
    """Configuration for tokenization behavior."""

    abbrev_no_split: set[str] = field(default_factory=set)


@dataclass(slots=True)
class G2PConfig:
    """Configuration for G2P conversion."""

    phoneme_inventory: list[str] = field(default_factory=list)
    lexicon: dict[str, str] = field(default_factory=dict)


__all__ = ["NormalizerConfig", "TokenizerConfig", "G2PConfig"]
