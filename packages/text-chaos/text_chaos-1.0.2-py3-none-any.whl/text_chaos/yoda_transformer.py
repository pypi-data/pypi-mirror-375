import random
import re
from typing import Dict, List, Tuple


class YodaTransformer:
    """
    Advanced Yoda speech transformer with linguistic analysis and multiple transformation strategies.
    """

    def __init__(self):
        # Yoda's characteristic sentence structures
        self.transformation_patterns = [
            # Subject-Verb-Object -> Object-Subject-Verb patterns
            (
                r"\b(I|You|We|They|He|She)\s+(am|are|is|was|were)\s+([^,.!?]+)",
                r"\3, \1 \2",
            ),
            # I/You + modal + verb -> verb, I/you + modal
            (
                r"\b(I|You)\s+(will|would|should|could|can|must)\s+([^,.!?]+)",
                r"\3, \1 \2",
            ),
            # I/You + verb + object -> object, I/you + verb
            (
                r"\b(I|You)\s+(love|like|hate|want|need|see|find|think|believe|know)\s+([^,.!?]+)",
                r"\3, \1 \2",
            ),
            # There is/are -> exists/exist, there
            (r"\bThere\s+(is|are)\s+([^,.!?]+)", r"\2, there \1"),
            # It is/was + adjective -> adjective, it is/was
            (r"\b(It)\s+(is|was)\s+(very\s+)?([^,.!?]+)", r"\3\4, \1 \2"),
            # We/They + verb -> verb, we/they + do
            (r"\b(We|They)\s+(go|come|fight|train|learn)\s*([^,.!?]*)", r"\2\3, \1 do"),
        ]

        # Yoda's speech quirks and additions
        self.yoda_quirks = {
            "confirmations": ["yes", "yeah", "ok", "okay", "right", "true"],
            "negations": ["no", "nope", "never"],
            "intensifiers": ["very", "really", "quite", "extremely"],
        }

        # Yoda's characteristic words and phrases
        self.yoda_vocabulary = {
            "young": "young one",
            "student": "young padawan",
            "person": "one",
            "people": "ones",
            "difficult": "difficult, this is",
            "easy": "easy, this is not",
            "impossible": "impossible, nothing is",
            "try": "do or do not, try there is no",
        }

        # Wisdom insertions
        self.wisdom_phrases = [
            "hmm",
            "mmm",
            "yes, yes",
            "strong with the Force",
            "much to learn",
            "patience, young one",
        ]

    def _add_yoda_quirks(self, text: str) -> str:
        """Add Yoda's characteristic speech patterns and quirks."""
        result = text

        # Add "mmm" to confirmations
        for word in self.yoda_quirks["confirmations"]:
            pattern = r"\b" + re.escape(word) + r"\b"
            result = re.sub(pattern, f"mmm, {word}", result, flags=re.IGNORECASE)

        # Add contemplative sounds to negations
        for word in self.yoda_quirks["negations"]:
            pattern = r"\b" + re.escape(word) + r"\b"
            result = re.sub(pattern, f"mmm, {word}", result, flags=re.IGNORECASE)

        # Replace vocabulary with Yoda alternatives
        for original, yoda_version in self.yoda_vocabulary.items():
            pattern = r"\b" + re.escape(original) + r"\b"
            result = re.sub(pattern, yoda_version, result, flags=re.IGNORECASE)

        return result

    def _apply_transformation_patterns(self, sentence: str) -> str:
        """Apply syntactic transformation patterns to create Yoda-like word order."""
        result = sentence.strip()

        for pattern, replacement in self.transformation_patterns:
            # Try to apply the pattern
            new_result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            if new_result != result:
                result = new_result
                break  # Apply only one transformation per sentence

        return result

    def _add_wisdom_insertion(self, text: str) -> str:
        """Randomly insert Yoda's wisdom phrases."""
        if random.random() < 0.3:  # 30% chance
            wisdom = random.choice(self.wisdom_phrases)
            # Insert at the beginning or end
            if random.random() < 0.5:
                return f"{wisdom}, {text}"
            else:
                return f"{text}, {wisdom}"
        return text

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences while preserving punctuation."""
        # Simple sentence splitting that preserves punctuation
        sentences = re.split(r"([.!?]+)", text)
        result = []

        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentence = sentences[i].strip()
                punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
                if sentence:
                    result.append(sentence + punctuation)

        # Handle case where text doesn't end with punctuation
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1].strip())

        return [s for s in result if s.strip()]

    def _fix_capitalization(self, text: str) -> str:
        """Fix capitalization after transformation."""
        # Capitalize first letter of sentences
        text = re.sub(
            r"([.!?]\s*)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text
        )

        # Capitalize first letter of the entire text
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        # Fix "i" to "I"
        text = re.sub(r"\bi\b", "I", text)

        return text

    def transform(self, text: str, add_wisdom: bool = True) -> str:
        """
        Transform text to Yoda-style speech patterns.

        Args:
            text: The input text to transform
            add_wisdom: Whether to randomly add Yoda's wisdom phrases

        Returns:
            The text transformed to Yoda's speech pattern

        Examples:
            >>> transformer = YodaTransformer()
            >>> transformer.transform("I love coding")
            'Coding, I love'
            >>> transformer.transform("You are very strong")
            'Very strong, you are'
            >>> transformer.transform("We should go now")
            'Go now, we should'
        """
        if not text or not text.strip():
            return text

        # Split into sentences for better processing
        sentences = self._split_into_sentences(text)
        transformed_sentences = []

        for sentence in sentences:
            # Remove punctuation for processing, but remember it
            punctuation = ""
            clean_sentence = sentence

            # Extract ending punctuation
            if sentence and sentence[-1] in ".!?":
                punctuation = sentence[-1]
                clean_sentence = sentence[:-1]

            # Apply transformations
            transformed = self._apply_transformation_patterns(clean_sentence)
            transformed = self._add_yoda_quirks(transformed)

            # Add wisdom phrases occasionally
            if add_wisdom:
                transformed = self._add_wisdom_insertion(transformed)

            # Restore punctuation
            transformed += punctuation

            transformed_sentences.append(transformed)

        # Join sentences and fix capitalization
        result = " ".join(transformed_sentences)
        result = self._fix_capitalization(result)

        return result
