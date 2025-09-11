# FurlanG2P

Utilities for converting Friulian (Furlan) text to phonemes. The package
includes a tiny gold lexicon and a rule-based engine that together provide an
experimental `furlang2p` command-line tool.

## Installation

```bash
pip install furlang2p
```

## CLI usage

Phonemise short phrases using the experimental `ipa` subcommand:

```bash
furlang2p ipa "ìsule glace"
# -> ˈizule ˈglatʃe
```

Wrap tokens in slashes or force rule-only conversion:

```bash
furlang2p ipa --with-slashes "glaç"
# -> /ˈglatʃ/

furlang2p ipa --rules-only "glaç"
# -> glatʃ
```

Use underscores as pause markers and customise the token separator:

```bash
furlang2p ipa --sep '|' _ "ìsule" __
# -> _|ˈizule|__
```

Other subcommands (`normalize`, `g2p`, `phonemize-csv`) are stubs and currently
raise `NotImplementedError`.

## Python usage

The same components can be invoked programmatically:

```python
from furlan_g2p.g2p.lexicon import Lexicon
from furlan_g2p.g2p.rule_engine import RuleEngine
from furlan_g2p.phonology import canonicalize_ipa

lex = Lexicon.load_seed()
rules = RuleEngine()
word = "glaç"
ipa = lex.get(word) or canonicalize_ipa(rules.convert(word))
print(ipa)
# -> ˈglatʃ
```

## Project links

- Source code and issue tracker: https://github.com/daurmax/FurlanG2P
- Bibliography and references: https://github.com/daurmax/FurlanG2P/blob/main/docs/references.md

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://github.com/daurmax/FurlanG2P/blob/main/LICENSE).
