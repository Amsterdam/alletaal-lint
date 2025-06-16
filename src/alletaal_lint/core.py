"""
Core LiNT scoring functionality for Dutch text readability assessment.

This module implements the core components of the LiNT (Leesbaarheids­instrument
voor Nederlandse Teksten) readability assessment tool, based on the research from
Gebruiker Centraal and the T-Scan project.

Note: This implementation uses modern NLP tools (spaCy, wordfreq) and may produce
scores that differ from the original T-Scan implementation due to different
parsing approaches and feature extraction methods. The core LiNT formula
remains unchanged, ensuring scientific validity while benefiting from
contemporary NLP advances.

See METHODOLOGY.md for detailed information about implementation differences.
"""

import math
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import spacy
from wordfreq import zipf_frequency


class WordStats:
    """Statistics and linguistic features for individual words."""

    def __init__(self, token: spacy.tokens.Token) -> None:
        self.token = token
        self.text = token.text
        self.lemma = token.lemma_
        self.dep_length = self._get_dependency_distance(token)
        self.tag = token.tag_.split("|")[0] if token.tag_ else ""
        self.sub_tags = token.tag_.split("|")[1:] if token.tag_ else []
        self.pos = token.pos_
        self.gender: Optional[str] = None
        self.number: Optional[str] = None
        self._parse_morphology(token.morph)

    def _get_dependency_distance(self, token: spacy.tokens.Token) -> int:
        """Calculate dependency distance between token and its head."""
        if token.dep_ in ["punct"]:
            return 0
        return int(abs(token.head.i - token.i))

    def _parse_morphology(self, morph: spacy.tokens.MorphAnalysis) -> None:
        """Parse morphological features from spaCy token."""
        if hasattr(morph, "get"):
            gender_list = morph.get("Gender", [])
            number_list = morph.get("Number", [])
            self.gender = gender_list[0] if gender_list else None
            self.number = number_list[0] if number_list else None

    def get_word_frequency(self) -> Optional[float]:
        """Get word frequency using zipf scale."""
        if self.tag not in ["N", "ADJ", "WW", "BW"]:
            return None

        if self.sub_tags and self.sub_tags[0] == "eigen":
            return None

        freq = zipf_frequency(self.text, "nl")
        return freq if freq > 0 else 1.3555  # Default frequency for unknown words

    def is_content_word_excluding_adverbs(self) -> bool:
        """Check if word is a content word (excluding adverbs)."""
        return (
            self.pos in ["NOUN", "PROPN", "VERB", "ADJ", "NUM", "SYM"]
            and self.pos != "ADV"
        )

    def is_noun_or_spec(self) -> bool:
        """Check if word is a noun or special token."""
        return self.tag in ["N", "SPEC"]

    def is_non_noun_content(self) -> bool:
        """Check if word is non-noun content (for concrete noun calculation)."""
        return self.pos not in ["NOUN"]


class LintScorer:
    """Core LiNT scoring functionality."""

    @staticmethod
    def calculate_lint_score(
        freq_log: float, al_max: int, content_words: float, concrete: float
    ) -> float:
        """
        Calculate LiNT readability score using the core formula.

        Args:
            freq_log: Average log word frequency
            al_max: Maximum dependency length
            content_words: Proportion of content words (excluding adverbs)
            concrete: Proportion of broadly concrete nouns

        Returns:
            LiNT score (0-100, higher = more readable)
        """
        score = (
            3.204
            + (15.845 * freq_log)
            - (1.331 * al_max)
            - (3.829 * content_words)
            + (13.096 * concrete)
        )
        return round(min(100.0, max(0.0, 100 - score)), 2)

    @staticmethod
    def get_difficulty_level(score: float) -> int:
        """
        Convert LiNT score to difficulty level.

        Args:
            score: LiNT score (0-100)

        Returns:
            Difficulty level (1-4, where 1 is most difficult)
        """
        if score <= 36:
            return 1
        elif score <= 51:
            return 2
        elif score <= 61.5:
            return 3
        else:
            return 4


class Sentence:
    """Sentence-level readability analysis."""

    def __init__(self, text: str, nlp_model: Optional[Any] = None) -> None:
        self.text = text
        self.nlp = nlp_model or self._load_nlp_model()
        self.doc = self.nlp(text)
        self.tokens = list(self.doc)
        self.words = [WordStats(token) for token in self.tokens]

    @staticmethod
    def _load_nlp_model() -> Any:
        """Load Dutch spaCy model."""
        try:
            return spacy.load("nl_core_news_sm")
        except OSError:
            raise RuntimeError(
                "Dutch spaCy model 'nl_core_news_sm' not found. "
                "Install it with: python -m spacy download nl_core_news_sm"
            )

    def get_word_frequency_log(self) -> float:
        """Calculate average log word frequency for the sentence."""
        frequencies = []
        for word in self.words:
            freq = word.get_word_frequency()
            if freq is not None and freq > 0:
                frequencies.append(freq)

        return sum(frequencies) / len(frequencies) if frequencies else 0

    def get_max_dependency_length(self) -> int:
        """Get maximum dependency length in the sentence."""
        max_dep_length = max((word.dep_length for word in self.words), default=0)

        # Apply T-Scan adjustment for very long dependencies
        if max_dep_length > 3:
            max_dep_length -= 2

        return max_dep_length

    def count_content_words_excluding_adverbs(self) -> int:
        """Count content words excluding adverbs."""
        return sum(1 for word in self.words if word.is_content_word_excluding_adverbs())

    def get_proportion_of_content_words_excluding_adverbs(self) -> float:
        """Get proportion of content words excluding adverbs per clause."""
        content_count = self.count_content_words_excluding_adverbs()
        clause_count = self._get_clause_count()

        return content_count / clause_count if clause_count > 0 else 0

    def get_proportion_of_broadly_concrete_nouns(self) -> float:
        """Calculate proportion of broadly concrete nouns."""
        total_nouns = 0
        non_noun_content = 0

        for word in self.words:
            if word.is_noun_or_spec():
                total_nouns += 1
                if word.is_non_noun_content():
                    non_noun_content += 1

        return non_noun_content / total_nouns if total_nouns > 0 else 0

    def _get_clause_count(self) -> int:
        """Estimate clause count (simplified implementation)."""
        # Simplified clause counting - in practice, this would require more sophisticated parsing
        # For now, assume 1 clause per sentence as a baseline
        return 1

    def calculate_lint_score(self) -> float:
        """Calculate LiNT readability score for the sentence."""
        freq_log = self.get_word_frequency_log()
        al_max = self.get_max_dependency_length()
        content_words = self.get_proportion_of_content_words_excluding_adverbs()
        concrete = self.get_proportion_of_broadly_concrete_nouns()

        return LintScorer.calculate_lint_score(
            freq_log, al_max, content_words, concrete
        )

    def get_difficulty_level(self) -> int:
        """Get difficulty level for the sentence."""
        return LintScorer.get_difficulty_level(self.calculate_lint_score())


class Document:
    """Document-level readability analysis."""

    def __init__(self, text: str):
        self.text = text
        self.nlp = Sentence._load_nlp_model()
        self.doc = self.nlp(text)
        self.sentences = self._tokenize_sentences()

    def _tokenize_sentences(self) -> List[Sentence]:
        """Split document into sentences."""
        return [Sentence(sent.text, self.nlp) for sent in self.doc.sents]

    def calculate_lint_score(self) -> float:
        """Calculate average LiNT score for the document."""
        if not self.sentences:
            return 0.0

        scores = [sentence.calculate_lint_score() for sentence in self.sentences]
        return round(sum(scores) / len(scores), 2)

    def get_difficulty_level(self) -> int:
        """Get difficulty level for the document."""
        return LintScorer.get_difficulty_level(self.calculate_lint_score())

    def get_sentence_scores(self) -> List[Tuple[str, float, int]]:
        """Get scores for individual sentences."""
        results = []
        for sentence in self.sentences:
            score = sentence.calculate_lint_score()
            level = sentence.get_difficulty_level()
            results.append((sentence.text, score, level))
        return results

    def get_detailed_analysis(self) -> Dict[str, Any]:
        """Get detailed readability analysis."""
        doc_score = self.calculate_lint_score()
        doc_level = self.get_difficulty_level()
        sentence_scores = self.get_sentence_scores()

        return {
            "document_score": doc_score,
            "document_level": doc_level,
            "sentence_count": len(self.sentences),
            "sentence_scores": sentence_scores,
            "average_sentence_length": (
                sum(len(s.text.split()) for s in self.sentences) / len(self.sentences)
                if self.sentences
                else 0
            ),
        }
