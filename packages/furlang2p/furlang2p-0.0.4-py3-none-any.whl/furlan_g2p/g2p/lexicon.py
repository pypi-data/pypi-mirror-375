from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources

from ..phonology import canonicalize_ipa


@dataclass(frozen=True)
class LexiconEntry:
    word: str
    ipa: str
    variants: tuple[str, ...]
    source: str


class Lexicon:
    """
    Tiny read-only lexicon backed by a packaged TSV.

    TSV columns: word, ipa, variants_json, source
    - 'variants_json' is a JSON array of alternative IPA strings (may be []).
    """

    def __init__(self, entries: dict[str, LexiconEntry] | None = None):
        # keys stored in NFC lowercase
        self._entries = entries or {}

    @classmethod
    def load_seed(cls) -> Lexicon:
        """
        Load the packaged seed lexicon.
        """
        # data file is located in "furlan_g2p/data/seed_lexicon.tsv"
        with (
            resources.files("furlan_g2p.data")
            .joinpath("seed_lexicon.tsv")
            .open("r", encoding="utf-8") as f
        ):
            reader = csv.DictReader(f, delimiter="\t")
            entries: dict[str, LexiconEntry] = {}
            for row in reader:
                word = row["word"].strip()
                ipa = canonicalize_ipa(row["ipa"].strip())
                raw_variants = json.loads(row.get("variants_json", "[]") or "[]")
                variants = tuple(canonicalize_ipa(v) for v in raw_variants)
                source = row["source"].strip()
                key = word.lower()
                entries[key] = LexiconEntry(word=word, ipa=ipa, variants=variants, source=source)
        return cls(entries)

    @lru_cache(maxsize=2048)  # noqa: B019 - deliberate cache on bound method
    def _lookup(self, key: str) -> LexiconEntry | None:
        return self._entries.get(key)

    def get(self, word: str) -> str | None:
        """Return the primary IPA for ``word`` if present, else ``None``.

        LRU-cached to avoid repeated dictionary lookups for frequent queries.
        """
        if not word:
            return None
        entry = self._lookup(word.lower())
        return entry.ipa if entry else None

    def get_entry(self, word: str) -> LexiconEntry | None:
        if not word:
            return None
        return self._lookup(word.lower())

    def __contains__(self, word: str) -> bool:
        return word.lower() in self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def items(self) -> Iterable[tuple[str, LexiconEntry]]:
        return self._entries.items()


__all__ = ["Lexicon", "LexiconEntry"]
