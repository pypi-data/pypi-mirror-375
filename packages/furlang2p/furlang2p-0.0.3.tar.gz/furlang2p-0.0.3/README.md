# FurlanG2P

Tools and library code for converting Friulian (Furlan) text to phonemes. The
project ships a small gold lexicon and a rule-based engine that together provide
an experimental ``ipa`` command-line tool. Other pieces of the pipeline – text
normalisation, tokenisation, full G2P and phonology – are present as skeletons
and currently raise ``NotImplementedError``.

## Quick local run (how to launch the CLI and test phrases)

1. Create and activate a virtual environment:

   - macOS / Linux:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - Windows (cmd.exe):
     ```
     python -m venv .venv
     .\.venv\Scripts\activate
     ```

2. Install the package in editable mode so the `furlang2p` console script becomes available:

   ```bash
   pip install -e .
   ```

3. Run the CLI and test short phrases (examples):

   - Basic phonemize using the seed lexicon with rule fallback:
     ```bash
     furlang2p ipa "ìsule glace"
     # Example output:
     # -> ˈizule ˈglatʃe
     ```

   - Wrap each token in slashes:
     ```bash
     furlang2p ipa --with-slashes "glaç"
     # -> /ˈglatʃ/
     ```

   - Force rule-based conversion (skip lexicon lookup):
     ```bash
     furlang2p ipa --rules-only "glaç"
     # -> glatʃ
     ```

   - Use underscores as pause markers and change token separator:
     ```bash
     furlang2p ipa --sep '|' _ "ìsule" __
     # -> _|ˈizule|__
     ```

   Notes:
   - Quotes around the phrase are recommended to preserve spacing and punctuation.
   - The CLI is experimental; some commands (normalize, g2p, phonemize-csv) are stubs that raise NotImplementedError.

## Installation

### From PyPI

```bash
pip install furlang2p
```

### From source

1. Create and activate a virtual environment (see Quick local run above).

2. Install the project in editable mode:

   ```bash
   pip install -e .
   ```

3. (Optional) Add development tools for linting, typing and tests:

   ```bash
   pip install -e .[dev]
   ```

## Usage

The package exposes a ``furlang2p`` CLI. At present only the experimental
``ipa`` subcommand does real work; the ``normalize``, ``g2p`` and
``phonemize-csv`` commands are stubs that abort with ``NotImplementedError``.

Run `furlang2p --help` or `furlang2p ipa --help` for full details about options.

## Development

Run the following checks before committing code:

```bash
isort .
black .
ruff check .
mypy src
pytest -q
```

## VS Code integration

A ``.vscode/tasks.json`` file provides shortcuts for common actions:

- **Install dependencies** – ``pip install -e .[dev]``
- **Format** – run ``isort`` and ``black``
- **Lint** – run ``ruff``
- **Type check** – run ``mypy`` on ``src``
- **Test** – execute ``pytest -q``

From VS Code press ``Ctrl+Shift+B`` or run *Tasks: Run Task* from the Command
Palette and choose the desired action.

## References

This project draws on published descriptions of Friulian orthography and
phonology as well as lemma-level IPA transcriptions. A curated bibliography with
live and archived links is maintained in
[docs/references.md](docs/references.md).

## Contributing

Pull requests that flesh out the skeleton or expand test coverage are welcome.
Please open an issue to discuss major changes.
