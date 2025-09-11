"""High-level pipeline service (skeleton)."""

from __future__ import annotations

import csv

from ..g2p.phonemizer import G2PPhonemizer
from ..normalization.normalizer import Normalizer
from ..phonology.stress import StressAssigner
from ..phonology.syllabifier import Syllabifier
from ..tokenization.tokenizer import Tokenizer


class PipelineService:
    """Orchestrates normalization -> tokenization -> G2P -> phonology."""

    def __init__(self) -> None:
        self.normalizer = Normalizer()
        self.tokenizer = Tokenizer()
        self.phonemizer = G2PPhonemizer()
        self.syllabifier = Syllabifier()
        self.stress = StressAssigner()

    def process_text(self, text: str) -> tuple[str, list[str]]:
        """Return ``(normalized_text, phoneme_sequence_as_list)``.

        Examples
        --------
        >>> PipelineService().process_text("Cjase")
        ('cjase', ['ˈc', 'a', 'z', 'e'])
        """

        norm = self.normalizer.normalize(text)
        sentences = self.tokenizer.split_sentences(norm)
        tokens: list[str] = []
        for sent in sentences:
            tokens.extend(self.tokenizer.split_words(sent))
        phons = self.phonemizer.to_phonemes(tokens)
        syllables = self.syllabifier.syllabify(phons)
        stressed = self.stress.assign_stress(syllables)
        flat = [p for syl in stressed for p in syl]
        return norm, flat

    def process_csv(self, input_csv_path: str, output_csv_path: str, delimiter: str = "|") -> None:
        """Phonemize an LJSpeech-like metadata CSV file.

        The input is expected to contain at least two columns: an identifier
        and the text to phonemize.  The output file will contain the same
        columns with an additional field containing the space-separated
        phoneme sequence.
        """

        with (
            open(input_csv_path, encoding="utf-8") as src,
            open(output_csv_path, "w", encoding="utf-8", newline="") as dst,
        ):
            reader = csv.reader(src, delimiter=delimiter)
            writer = csv.writer(dst, delimiter=delimiter)
            for row in reader:
                if len(row) < 2:
                    continue
                norm, phons = self.process_text(row[1])
                writer.writerow([row[0], norm, " ".join(phons)])


__all__ = ["PipelineService"]
