AGENTS BRIEFING

This repository is scaffolded for future automated agents (e.g., codegen, test bots).
The codebase includes minimal implementations for text normalization, a seed lexicon,
a rule-based orthography-to-IPA converter and basic phonology helpers, but many
public interfaces remain stubs that raise NotImplementedError.

- Public interfaces are stable, so agents can implement internals without reshaping the API.
- Tests check importability, CLI help, and that unimplemented methods raise NotImplementedError.

Agent tasks (suggested):

- Expand text normalization rules and configuration loading.
- Implement tokenization with abbreviation handling and sentence/word splitting.
- Expand G2P: grow the lexicon, refine the rule engine and manage phoneme inventory.
- Refine phonology: syllabification and stress assignment.
- Wire services into CLI subcommands; add CSV batch processing.
- Add real tests, fixtures, and golden sets.

Reference checks:

- When changing business logic (rules, lexicon, phonology, etc.), consult the
  bibliography in `docs/references.md` to ensure modifications align with the
  cited sources.

Documentation:

- `README.md` targets GitHub contributors. It should describe the repository
  layout, how to build distributions, how to run the test suite, and which
  sources form the project's basis of truth.
- `README-pypi.md` targets end users on PyPI. It should focus on installation
  and usage examples.
- When a change affects user-facing behaviour or packaging, update the
  appropriate README(s) to keep them in sync.

Coding standards:

- Type hints everywhere.
- Docstrings with argument/return types and examples.
- Keep runtime deps minimal; add extras behind optional groups if needed.
- Follow ruff/black/mypy configs defined in pyproject.toml.
