"""
Tests for the text-chaos library.

Each transformation mode is tested exactly once with a medium-length paragraph
to comprehensively validate functionality.
"""

import pytest

from text_chaos import batch_transform, get_modes, transform
from text_chaos.transformers import (
    drunk_transform,
    emoji_transform,
    leet_transform,
    mallock_transform,
    mock_transform,
    morse_transform,
    piglatin_transform,
    pirate_transform,
    roman_transform,
    shakespeare_transform,
    uwu_transform,
    yoda_transform,
    zalgo_transform,
)


class TestTransformations:
    """Test each transformation mode with comprehensive paragraph inputs."""

    def test_leet_transform(self):
        """Test leet speak transformation with a paragraph."""
        input_text = """Technology has evolved significantly over the past decade. 
        The internet connects billions of people worldwide, enabling instant communication. 
        Social media platforms have transformed how we share information and stay connected with friends."""

        result = leet_transform(input_text)

        # Verify leet substitutions occurred
        assert "3" in result  # 'e' -> '3'
        assert "1" in result  # 'i' or 'l' -> '1'
        assert "0" in result  # 'o' -> '0'
        assert "5" in result  # 's' -> '5'
        assert "7" in result  # 't' -> '7'
        assert result != input_text

    def test_uwu_transform(self):
        """Test uwu transformation with a paragraph."""
        input_text = """Learning new languages can be really rewarding and fun. 
        Reading books helps improve vocabulary and comprehension skills. 
        Regular practice leads to better fluency and natural conversation abilities."""

        result = uwu_transform(input_text)

        # Verify uwu characteristics
        assert result.count("w") > input_text.count("w")  # r/l -> w replacements
        assert "ny" in result  # n + vowel -> ny transformations
        assert any(expr in result for expr in [" uwu", " owo", " >w<", " ^w^"])
        assert result != input_text

    def test_mallock_transform(self):
        """Test mallock memory dump transformation with a paragraph."""
        input_text = """Debugging software requires patience and systematic thinking. 
        Memory leaks can cause applications to crash unexpectedly. 
        Understanding pointers helps developers write efficient code."""

        result = mallock_transform(input_text)

        # Verify memory dump format
        assert "0x1000:" in result  # Should start with base address
        assert result.endswith(" k")  # Should end with " k"
        assert "0x" in result  # Should contain hex addresses
        assert ":" in result  # Should have address:value format
        assert len(result) > len(input_text)  # Should be longer due to formatting

    def test_zalgo_transform(self):
        """Test zalgo transformation with a paragraph."""
        input_text = """The ancient ritual required careful preparation and focus. 
        Mysterious symbols adorned the stone walls of the temple. 
        Dark magic flowed through the ceremonial chamber like whispers."""

        result = zalgo_transform(input_text)

        # Verify zalgo characteristics
        assert len(result) > len(input_text)  # Should be longer due to combining chars
        # Original letters should still be present
        for char in "ancient ritual":
            if char.isalpha():
                assert char in result
        assert result != input_text

    def test_mock_transform(self):
        """Test mock transformation with conversational fillers."""
        input_text = """This assignment is really difficult to complete on time. 
        The professor expects high quality work from every student. 
        Nobody understands the complicated requirements clearly."""

        result = mock_transform(input_text)

        # Verify mock characteristics (filler words and pauses)
        mock_words = [
            "uhh",
            "like",
            "you know",
            "I mean",
            "whatever",
            "umm",
            "basically",
            "actually",
        ]
        assert any(word in result for word in mock_words)  # Should have filler words
        assert "..." in result or ", " in result  # Should have pauses or commas
        assert result != input_text

    def test_pirate_transform(self):
        """Test pirate transformation with a paragraph."""
        input_text = """Hello there, my good friend! How are you doing today? 
        I have some money saved up for our next adventure. 
        Yes, we should definitely go explore that mysterious island over there."""

        result = pirate_transform(input_text)

        # Verify pirate characteristics
        pirate_words = ["ahoy", "matey", "ye", "aye", "doubloons", "thither"]
        assert any(word in result.lower() for word in pirate_words)
        assert result != input_text

    def test_emoji_transform(self):
        """Test emoji transformation with a paragraph."""
        input_text = """I love eating pizza and drinking coffee in the morning. 
        My dog and cat are very happy when the sun shines bright. 
        We often travel by car to visit beautiful places and take photos."""

        result = emoji_transform(input_text)

        # Verify emoji substitutions
        expected_emojis = ["❤️", "🍕", "☕", "🐶", "🐱", "😊", "☀️", "🚗"]
        assert any(emoji in result for emoji in expected_emojis)
        assert result != input_text

    def test_yoda_transform(self):
        """Test Yoda transformation with a paragraph."""
        input_text = """I believe you will become a great teacher someday. 
        The young student must learn patience and wisdom. 
        Yes, there are many challenges ahead but we can overcome them."""

        result = yoda_transform(input_text)

        # Verify Yoda characteristics
        yoda_words = [
            "young one",
            "young padawan",
            "hmm",
            "mmm",
            "strong with the force",
        ]
        assert any(word in result.lower() for word in yoda_words)
        # Should have sentence reordering
        assert result != input_text

    def test_drunk_transform(self):
        """Test drunk typing transformation with a paragraph."""
        input_text = """The presentation went extremely well yesterday evening. 
        Everyone appreciated the detailed analysis and thorough research. 
        Professional communication skills are essential for career success."""

        result = drunk_transform(input_text)

        # Since drunk transform is random, test multiple times if first doesn't change
        attempts = 0
        while result == input_text and attempts < 5:
            result = drunk_transform(input_text)
            attempts += 1

        # Should eventually produce some changes (typos, missing letters, etc.)
        assert result != input_text or attempts < 5

    def test_shakespeare_transform(self):
        """Test Shakespeare transformation with a paragraph."""
        input_text = """Hello, you are a very great and beautiful person today. 
        Yes, maybe you should go there before the meeting starts. 
        I believe you have the wisdom to make good decisions quickly."""

        result = shakespeare_transform(input_text)

        # Verify Shakespearean characteristics
        shakespeare_words = [
            "thou",
            "thy",
            "art",
            "hail",
            "aye",
            "mayhap",
            "thither",
            "magnificent",
            "beauteous",
            "hast",
        ]
        assert any(word in result.lower() for word in shakespeare_words)
        assert result != input_text

    def test_piglatin_transform(self):
        """Test Pig Latin transformation with a paragraph."""
        input_text = """Education opens many opportunities for personal growth and development. 
        Students should always strive to learn something new every single day. 
        Understanding different perspectives helps create better solutions."""

        result = piglatin_transform(input_text)

        # Verify Pig Latin characteristics
        assert "ay" in result  # Consonant clusters + "ay"
        assert "way" in result  # Vowel-starting words + "way"
        # Should maintain word boundaries
        assert len(result.split()) == len(input_text.split())
        assert result != input_text

    def test_morse_transform(self):
        """Test Morse code transformation with a paragraph."""
        input_text = """SOS Emergency rescue needed immediately. 
        Radio communication systems are down. 
        Send help to our coordinates as soon as possible."""

        result = morse_transform(input_text)

        # Verify Morse code characteristics
        assert "." in result and "-" in result  # Should contain dots and dashes
        assert " " in result  # Spaces between letters
        assert "/" in result  # Word separators
        # Should be longer due to morse encoding
        assert len(result) > len(input_text)

    def test_roman_transform(self):
        """Test Roman numeral transformation with a paragraph."""
        input_text = """The year 2024 marked significant technological advancement. 
        Over 500 companies participated in the innovation summit. 
        By 2030, we expect 1000 new patents to be filed annually."""

        result = roman_transform(input_text)

        # Verify Roman numeral transformations
        roman_chars = ["M", "D", "C", "L", "X", "V", "I"]
        assert any(char in result for char in roman_chars)
        assert "2024" not in result  # Should be converted to roman
        assert "500" not in result  # Should be converted to roman
        assert result != input_text


class TestMainAPI:
    """Test the main API functions."""

    def test_transform_basic(self):
        """Test basic transform functionality."""
        result = transform("hello", "leet")
        assert result == "h3110"

        result = transform("hello", "mallock")
        assert "0x1000:" in result

    def test_transform_invalid_mode(self):
        """Test transform with invalid mode."""
        with pytest.raises(ValueError, match="Unknown transformation mode"):
            transform("hello", "invalid_mode")

    def test_get_modes(self):
        """Test getting available modes."""
        modes = get_modes()
        expected_modes = [
            "leet",
            "uwu",
            "mallock",
            "zalgo",
            "mock",
            "pirate",
            "emoji",
            "yoda",
            "drunk",
            "shakespeare",
            "piglatin",
            "morse",
            "roman",
        ]

        assert len(modes) == 13
        for mode in expected_modes:
            assert mode in modes

    def test_batch_transform(self):
        """Test batch transformation."""
        texts = ["hello world", "test message"]
        results = batch_transform(texts, "leet")

        assert len(results) == 2
        assert all("3" in result for result in results)  # Leet transformation applied


class TestIntegration:
    """Integration tests for the complete library."""

    def test_all_modes_work(self):
        """Test that all 13 registered modes work without errors."""
        test_text = "Hello World! This is a test message with numbers 123."

        modes = get_modes()
        assert len(modes) == 13

        for mode in modes:
            result = transform(test_text, mode)
            assert isinstance(result, str)
            assert len(result) > 0  # Should produce some output
