from __future__ import annotations

from click.testing import CliRunner

from furlan_g2p.cli.app import cli


def test_ipa_lexicon_and_rules() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["ipa", "ìsule", "glace"])
    assert result.exit_code == 0
    assert result.output.strip() == "ˈizule ˈglatʃe"


def test_ipa_with_slashes() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["ipa", "--with-slashes", "glaç"])
    assert result.exit_code == 0
    assert result.output.strip() == "/ˈglatʃ/"


def test_ipa_rules_only() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["ipa", "--rules-only", "glaç"])
    assert result.exit_code == 0
    assert result.output.strip() == "glatʃ"


def test_ipa_apostrophes() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["ipa", "l'cjase"])
    assert result.exit_code == 0
    assert result.output.strip() == "l'ˈcaze"


def test_ipa_pause_and_separator() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["ipa", "--sep", "|", "_", "ìsule", "__"])
    assert result.exit_code == 0
    assert result.output.strip() == "_|ˈizule|__"


def test_ipa_punctuation() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["ipa", "«perturbazion»,", "—", "…"])
    assert result.exit_code == 0
    assert result.output.strip() == "perturbazion _"


def test_ipa_missing_argument() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["ipa"])
    assert result.exit_code != 0
    assert "Usage" in result.output
