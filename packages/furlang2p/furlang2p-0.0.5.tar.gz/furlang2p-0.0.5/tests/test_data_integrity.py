from __future__ import annotations

import csv
import json
from importlib import resources
from urllib.parse import urlparse


def test_seed_lexicon_tsv_is_well_formed() -> None:
    with (
        resources.files("furlan_g2p.data")
        .joinpath("seed_lexicon.tsv")
        .open("r", encoding="utf-8") as f
    ):
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)
    assert rows, "seed_lexicon.tsv is empty"
    required = {"word", "ipa", "variants_json", "source"}
    assert required.issubset(reader.fieldnames or set())
    # no duplicates by lowercase key
    keys = [r["word"].lower() for r in rows]
    assert len(keys) == len(set(keys)), "duplicate entries detected"
    for row in rows:
        word = row["word"]
        assert word == word.lower(), "word keys must be lowercase"
        # variants_json must be valid JSON list
        variants = json.loads(row["variants_json"] or "[]")
        assert isinstance(variants, list)
        # simple URL validation
        url = urlparse(row["source"])
        assert url.scheme and url.netloc, "invalid source URL"
