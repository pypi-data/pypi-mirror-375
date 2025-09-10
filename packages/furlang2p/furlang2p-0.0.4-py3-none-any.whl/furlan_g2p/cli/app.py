"""Command-line interface for FurlanG2P (skeleton)."""

from __future__ import annotations

import sys

import click

from ..g2p.lexicon import Lexicon
from ..g2p.rule_engine import RuleEngine
from ..normalization.experimental_normalizer import ExperimentalNormalizer
from ..phonology import canonicalize_ipa
from ..services.pipeline import PipelineService

_NORMALIZER = ExperimentalNormalizer()
_LEXICON = Lexicon.load_seed()
_RULES = RuleEngine()


def _split_apostrophes(token: str) -> list[str]:
    """Split ``token`` on apostrophes while keeping them as separate elements."""

    parts: list[str] = []
    start = 0
    for idx, ch in enumerate(token):
        if ch == "'":
            if start < idx:
                parts.append(token[start:idx])
            parts.append("'")
            start = idx + 1
    if start < len(token):
        parts.append(token[start:])
    return parts


def _is_pause(token: str) -> bool:
    """Return ``True`` if ``token`` consists solely of underscores."""

    return bool(token) and set(token) <= {"_"}


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """FurlanG2P command-line interface (skeleton)."""
    # click requires a function body
    pass


@cli.command("normalize")
@click.argument("text", nargs=-1)
def cmd_normalize(text: tuple[str, ...]) -> None:
    """Normalize text and print it."""
    PipelineService()
    _ = " ".join(text)
    raise NotImplementedError("normalize command is not implemented yet.")


@cli.command("g2p")
@click.argument("text", nargs=-1)
def cmd_g2p(text: tuple[str, ...]) -> None:
    """Convert text to phonemes and print them."""
    PipelineService()
    _ = " ".join(text)
    raise NotImplementedError("g2p command is not implemented yet.")


@cli.command("phonemize-csv")
@click.option("--in", "inp", required=True, help="Input metadata CSV (LJSpeech-like).")
@click.option("--out", "out", required=True, help="Output CSV with phonemes added.")
@click.option("--delim", "delim", default="|", show_default=True, help="CSV delimiter.")
def cmd_phonemize_csv(inp: str, out: str, delim: str) -> None:
    """Batch phonemize an LJSpeech-like CSV file."""
    PipelineService()
    raise NotImplementedError("phonemize-csv command is not implemented yet.")


@cli.command(
    "ipa",
    help="[experimental] Convert text to IPA using the seed lexicon and rule-based fallback.",
)
@click.option(
    "--rules-only",
    is_flag=True,
    default=False,
    help="Skip lexicon lookup and always use the rule engine.",
)
@click.option(
    "--with-slashes/--no-slashes",
    default=False,
    help="Wrap each token's IPA in /slashes/.",
)
@click.option(
    "--sep",
    default=" ",
    show_default=True,
    help="Separator used to join output tokens.",
)
@click.argument("text", nargs=-1, required=True)
def cmd_ipa(
    text: tuple[str, ...],
    rules_only: bool,
    with_slashes: bool,
    sep: str,
) -> None:
    """Phonemize ``text`` using experimental components."""

    raw_sentence = " ".join(text)
    tokens: list[str] = []
    for raw in raw_sentence.split():
        if _is_pause(raw):
            tokens.append(raw)
            continue
        tokens.extend(_NORMALIZER.normalize(raw))
    out_tokens: list[str] = []
    for token in tokens:
        if _is_pause(token):
            out_tokens.append(token)
            continue
        parts = _split_apostrophes(token)
        ipa_parts: list[str] = []
        for part in parts:
            if part == "'":
                ipa_parts.append(part)
                continue
            raw_ipa = (
                _RULES.convert(part) if rules_only else (_LEXICON.get(part) or _RULES.convert(part))
            )
            ipa = canonicalize_ipa(raw_ipa)
            if with_slashes:
                ipa = f"/{ipa}/"
            ipa_parts.append(ipa)
        out_tokens.append("".join(ipa_parts))
    click.echo(sep.join(out_tokens))


def main() -> None:  # pragma: no cover - small wrapper
    try:
        cli(prog_name="furlang2p")
    except NotImplementedError as e:  # pragma: no cover - placeholder behaviour
        click.echo(f"[FurlanG2P skeleton] {e}", err=True)
        sys.exit(2)


__all__ = ["cli", "main"]
