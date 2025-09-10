AGENTS BRIEFING

This repository is scaffolded for future automated agents (e.g., codegen, test bots). The current state is a deliberate skeleton:

- All core algorithms raise NotImplementedError.
- Public interfaces are stable, so agents can implement internals without reshaping the API.
- Tests check importability, CLI help, and that unimplemented methods raise NotImplementedError.

Agent tasks (suggested):

- Implement text normalization rules and configuration loading.
- Implement tokenization with abbreviation handling and sentence/word splitting.
- Implement G2P: lexicon lookup, LTS rules engine, and phoneme inventory management.
- Implement phonology: syllabification and stress assignment.
- Wire services into CLI subcommands; add CSV batch processing.
- Add real tests, fixtures, and golden sets.

Reference checks:

- When changing business logic (rules, lexicon, phonology, etc.), consult the
  bibliography in `docs/references.md` to ensure modifications align with the
  cited sources.

Coding standards:

- Type hints everywhere.
- Docstrings with argument/return types and examples.
- Keep runtime deps minimal; add extras behind optional groups if needed.
- Follow ruff/black/mypy configs defined in pyproject.toml.
