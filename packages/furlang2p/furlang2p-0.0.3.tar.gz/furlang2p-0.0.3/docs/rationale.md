# Rule rationale

This repository treats the packaged lexicon as the authoritative source for
"gold" items.  Pronunciations in the lexicon must match their cited sources
exactly.  Phrase-level tests only check composition of these entries and are not
considered gold.

## Rule order

The experimental rule engine applies rules from longest to shortest context:

1. `cj` → `c` and `gj` → `ɟ` (palatal stops). [ARLeF – GRAFIE]
2. `ch`/`gh` harden `c`/`g` before front vowels. [ARLeF – GRAFIE]
3. `c` before `e i ê î` → `tʃ`; `ç` always → `tʃ`. [ARLeF – GRAFIE]
4. Intervocalic `s` → `z`; `ss` remains voiceless. [ìsule on Wiktionary]
5. Circumflex vowels map to long monophthongs. [ARLeF – Lezione 7; Wikipedia – Friulian language]

These rules intentionally avoid sandhi and stress except for length marks from
the lexicon.

## Sources

- ARLeF – *GRAFIE* <https://arlef.it/wp-content/uploads/2017/03/RegoleDellaGrafia.pdf>
- ARLeF – *Dut par furlan*, Lezione 7 <https://arlef.it/wp-content/uploads/2020/07/DPF-Ud-07.pdf>
- Wikipedia – *Friulian language* <https://en.wikipedia.org/wiki/Friulian_language>
- Wiktionary lemma pages cited in tests.
