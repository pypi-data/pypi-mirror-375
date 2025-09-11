"""
Text transformation functions for the text-chaos library.

This module contains all the individual transformation functions
that can be applied to text strings.
"""

import random
import re
from typing import Callable, Dict, List

from .emoji_data import EMOJI_MAP
from .pirate_data import PIRATE_EXCLAMATIONS, PIRATE_REPLACEMENTS
from .shakespeare_data import SHAKESPEARE_REPLACEMENTS
from .yoda_transformer import YodaTransformer


def leet_transform(text: str) -> str:
    """
    Transform text to leet speak (1337 speak).

    Args:
        text: The input text to transform

    Returns:
        The text converted to leet speak

    Example:
        >>> leet_transform("Hello World")
        "H3110 W0r1d"
    """
    leet_map: Dict[str, str] = {
        "a": "4",
        "A": "4",
        "e": "3",
        "E": "3",
        "i": "1",
        "I": "1",
        "o": "0",
        "O": "0",
        "s": "5",
        "S": "5",
        "t": "7",
        "T": "7",
        "l": "1",
        "L": "1",
        "g": "9",
        "G": "9",
    }

    result = ""
    for char in text:
        result += leet_map.get(char, char)

    return result


def uwu_transform(text: str) -> str:
    """
    Transform text to uwu speak.

    Args:
        text: The input text to transform

    Returns:
        The text converted to uwu speak

    Example:
        >>> uwu_transform("Hello World")
        "Hewwo Wowwd uwu"
    """
    # Replace r and l with w
    text = re.sub(r"[rl]", "w", text)
    text = re.sub(r"[RL]", "W", text)

    # Replace some consonants
    text = re.sub(r"n([aeiou])", r"ny\1", text)
    text = re.sub(r"N([aeiou])", r"Ny\1", text)

    # Add uwu expressions
    uwu_expressions = [" uwu", " owo", " >w<", " ^w^"]
    if text and not any(expr in text for expr in uwu_expressions):
        text += random.choice(uwu_expressions)

    return text


def mallock_transform(text: str) -> str:
    """
    Transform text into a memory dump style format with hexadecimal addresses.

    Args:
        text: The input text to transform

    Returns:
        The text formatted as a memory dump with hex addresses

    Example:
        >>> mallock_transform("Hello")
        "0x1000:H0x1001:e0x1002:l0x1003:l0x1004:ok"
    """
    if not text:
        return text

    result = []
    base_address = 0x1000
    max_gap = 1
    addr = base_address

    for i, char in enumerate(text):
        gap = random.randint(0, max_gap)
        for _ in range(gap):
            result.append(f"0x{addr:X}:_")
            addr += 1
        result.append(f"0x{addr:X}:{char}")
        addr += 1

    # Append 'k' only to the final pointer
    if result:
        result[-1] = result[-1] + " k"

    return "".join(result)


def zalgo_transform(text: str) -> str:
    """
    Add zalgo-style diacritical marks to text.

    Args:
        text: The input text to transform

    Returns:
        The text with zalgo effects

    Example:
        >>> zalgo_transform("Hello")
        "Ḧ̴̰e̵͎̾l̶̤̿l̴̰̈o̵͎̾"
    """
    # Zalgo combining characters (subset for safety)
    zalgo_chars = [
        "\u0300",
        "\u0301",
        "\u0302",
        "\u0303",
        "\u0304",
        "\u0305",
        "\u0307",
        "\u0308",
        "\u0309",
        "\u030a",
        "\u030b",
        "\u030c",
        "\u0316",
        "\u0317",
        "\u0318",
        "\u0319",
        "\u031a",
        "\u031b",
        "\u031c",
        "\u031d",
        "\u031e",
        "\u031f",
        "\u0320",
        "\u0321",
    ]

    result = ""
    for char in text:
        result += char
        if char.isalpha():  # Only add zalgo to letters
            # Add 1-3 random zalgo characters
            num_marks = random.randint(1, 3)
            for _ in range(num_marks):
                result += random.choice(zalgo_chars)

    return result


def mock_transform(text: str) -> str:
    """
    Transform text by randomly inserting pauses, filler words, and "uhh".

    Args:
        text: The input text to transform

    Returns:
        The text with conversational fillers and pauses

    Example:
        >>> mock_transform("This is fine")
        "This... uhh is, like, fine... whatever..."
    """
    if not text.strip():
        return text

    # Filler words and expressions
    fillers = [
        "uhh",
        "like",
        "you know",
        "I mean",
        "whatever",
        "umm",
        "sort of",
        "kind of",
        "basically",
        "actually",
        "honestly",
    ]

    # Pauses and hesitations
    pauses = ["...", "... ", " ...", " ... "]

    # Split text into words while preserving punctuation
    words = re.findall(r"\w+|[^\w\s]", text)
    if not words:
        return text

    result = []

    for i, word in enumerate(words):
        # Add the current word/punctuation
        if word.isalpha():
            # 25% chance to add a filler before the word
            if random.random() < 0.25:
                filler = random.choice(fillers)
                if i > 0:  # Not the first word
                    result.append(", " + filler)
                else:
                    result.append(filler)

            result.append(word)

            # 20% chance to add a pause after the word
            if random.random() < 0.20:
                result.append(random.choice(pauses))

            # 15% chance to add a filler after the word
            if random.random() < 0.15 and i < len(words) - 1:  # Not the last word
                result.append(", " + random.choice(fillers))
        else:
            # Handle punctuation
            result.append(word)

    # Join and clean up spacing
    final_text = "".join(result)

    # Clean up multiple spaces and awkward punctuation
    final_text = re.sub(r"\s+", " ", final_text)  # Multiple spaces to single
    final_text = re.sub(r"\s*,\s*,", ",", final_text)  # Double commas
    final_text = re.sub(r"\s*\.\s*\.", ".", final_text)  # Double periods (not ellipsis)
    final_text = final_text.strip()

    # 30% chance to add a trailing filler at the end
    if random.random() < 0.30:
        trailing_fillers = ["whatever...", "you know?", "I guess...", "or something..."]
        final_text += ", " + random.choice(trailing_fillers) + ""

    return final_text


def pirate_transform(text: str) -> str:
    """
    Transform text to pirate speak.

    Args:
        text: The input text to transform

    Returns:
        The text converted to pirate speak

    Example:
        >>> pirate_transform("Hello friend, how are you?")
        "Ahoy matey, how be ye? Arr!"
    """
    # Convert to lowercase for pattern matching, but preserve original case
    result = text

    # Apply pirate replacements
    for pattern, replacement in PIRATE_REPLACEMENTS.items():
        # Use case-insensitive matching
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Add an exclamation at the end if the text doesn't already end with punctuation
    if result and result[-1] not in ".!?":
        result += ", " + random.choice(PIRATE_EXCLAMATIONS)
    elif (
        result and random.random() < 0.3
    ):  # 30% chance to add exclamation even with punctuation
        result += " " + random.choice(PIRATE_EXCLAMATIONS)

    return result


def emoji_transform(text: str) -> str:
    """
    Replace words with corresponding emojis.

    Args:
        text: The input text to transform

    Returns:
        The text with words replaced by emojis

    Example:
        >>> emoji_transform("I love pizza")
        "I ❤️ 🍕"
    """
    result = text
    for pattern, emoji in EMOJI_MAP.items():
        result = re.sub(pattern, emoji, result, flags=re.IGNORECASE)

    return result


# Create a global Yoda transformer instance for efficiency
_yoda_transformer = None


def yoda_transform(text: str) -> str:
    """
    Transform text to Yoda-style speech patterns using advanced linguistic analysis.

    Args:
        text: The input text to transform

    Returns:
        The text rearranged in Yoda's speech pattern with advanced transformations

    Example:
        >>> yoda_transform("I love coding")
        "Coding, I love"
        >>> yoda_transform("You are very strong")
        "Very strong, you are, mmm"
    """
    global _yoda_transformer
    if _yoda_transformer is None:
        _yoda_transformer = YodaTransformer()

    return _yoda_transformer.transform(text, add_wisdom=True)


def drunk_transform(text: str) -> str:
    """
    Add typos and missing letters to simulate drunk typing.

    Args:
        text: The input text to transform

    Returns:
        The text with drunk-style typos

    Example:
        >>> drunk_transform("hello there")
        "helo tehre"
    """
    result = ""
    i = 0

    while i < len(text):
        char = text[i]

        if char.isalpha():
            # 20% chance to introduce a typo
            if random.random() < 0.2:
                typo_type = random.choice(["skip", "swap", "double", "wrong"])

                if typo_type == "skip":
                    # Skip this character (missing letter)
                    pass
                elif typo_type == "swap" and i < len(text) - 1:
                    # Swap with next character
                    if text[i + 1].isalpha():
                        result += text[i + 1] + char
                        i += 1  # Skip next char since we used it
                    else:
                        result += char
                elif typo_type == "double":
                    # Double the character
                    result += char + char
                elif typo_type == "wrong":
                    # Replace with nearby keyboard key
                    keyboard_neighbors = {
                        "a": "s",
                        "b": "v",
                        "c": "x",
                        "d": "s",
                        "e": "r",
                        "f": "d",
                        "g": "f",
                        "h": "g",
                        "i": "u",
                        "j": "h",
                        "k": "j",
                        "l": "k",
                        "m": "n",
                        "n": "b",
                        "o": "i",
                        "p": "o",
                        "q": "w",
                        "r": "e",
                        "s": "a",
                        "t": "r",
                        "u": "y",
                        "v": "c",
                        "w": "q",
                        "x": "z",
                        "y": "t",
                        "z": "x",
                    }
                    wrong_char = keyboard_neighbors.get(char.lower(), char)
                    if char.isupper():
                        wrong_char = wrong_char.upper()
                    result += wrong_char
                else:
                    result += char
            else:
                result += char
        else:
            result += char

        i += 1

    return result


def shakespeare_transform(text: str) -> str:
    """
    Transform text to Shakespearean English.

    Args:
        text: The input text to transform

    Returns:
        The text in Shakespearean style

    Example:
        >>> shakespeare_transform("you are great")
        "thou art magnificent"
    """
    result = text
    for pattern, replacement in SHAKESPEARE_REPLACEMENTS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def piglatin_transform(text: str) -> str:
    """
    Transform text to Pig Latin.

    Args:
        text: The input text to transform

    Returns:
        The text converted to Pig Latin

    Example:
        >>> piglatin_transform("hello world")
        "ello-hay orld-way"
    """

    def pig_latin_word(word: str) -> str:
        if not word.isalpha():
            return word

        vowels = "aeiouAEIOU"

        # If word starts with vowel, add "way"
        if word[0] in vowels:
            return word + "way"

        # Find first vowel
        first_vowel = -1
        for i, char in enumerate(word):
            if char in vowels:
                first_vowel = i
                break

        if first_vowel == -1:  # No vowels found
            return word + "ay"

        # Move consonants to end and add "ay"
        consonants = word[:first_vowel]
        rest = word[first_vowel:]

        return rest + consonants + "ay"

    words = re.findall(r"\b\w+\b|\W+", text)
    result = ""

    for word_match in words:
        if re.match(r"\w+", word_match):
            # Preserve case
            if word_match.isupper():
                pig_word = pig_latin_word(word_match.lower()).upper()
            elif word_match[0].isupper():
                pig_word = pig_latin_word(word_match.lower())
                pig_word = pig_word[0].upper() + pig_word[1:]
            else:
                pig_word = pig_latin_word(word_match)
            result += pig_word
        else:
            result += word_match

    return result


def morse_transform(text: str) -> str:
    """
    Transform text to Morse code.

    Args:
        text: The input text to transform

    Returns:
        The text converted to Morse code

    Example:
        >>> morse_transform("hello")
        ".... . .-.. .-.. ---"
    """
    morse_code = {
        "A": ".-",
        "B": "-...",
        "C": "-.-.",
        "D": "-..",
        "E": ".",
        "F": "..-.",
        "G": "--.",
        "H": "....",
        "I": "..",
        "J": ".---",
        "K": "-.-",
        "L": ".-..",
        "M": "--",
        "N": "-.",
        "O": "---",
        "P": ".--.",
        "Q": "--.-",
        "R": ".-.",
        "S": "...",
        "T": "-",
        "U": "..-",
        "V": "...-",
        "W": ".--",
        "X": "-..-",
        "Y": "-.--",
        "Z": "--..",
        "0": "-----",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        " ": "/",
    }

    result = []
    for char in text.upper():
        if char in morse_code:
            result.append(morse_code[char])
        elif char == " ":
            result.append("/")

    return " ".join(result)


def roman_transform(text: str) -> str:
    """
    Transform numbers to Roman numerals.

    Args:
        text: The input text to transform

    Returns:
        The text with numbers converted to Roman numerals

    Example:
        >>> roman_transform("the year 2025")
        "the year MMXXV"
    """

    def to_roman(num: int) -> str:
        if num <= 0 or num > 3999:
            return str(num)  # Return original if out of range

        values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        numerals = [
            "M",
            "CM",
            "D",
            "CD",
            "C",
            "XC",
            "L",
            "XL",
            "X",
            "IX",
            "V",
            "IV",
            "I",
        ]

        result = ""
        for i, value in enumerate(values):
            count = num // value
            if count:
                result += numerals[i] * count
                num -= value * count
        return result

    # Find all numbers in the text
    def replace_number(match) -> str:
        num = int(match.group())
        return to_roman(num)

    return re.sub(r"\b\d+\b", replace_number, text)


# Registry of all available transformers
TRANSFORMERS: Dict[str, Callable[[str], str]] = {
    "leet": leet_transform,
    "uwu": uwu_transform,
    "drunk": drunk_transform,
    "mock": mock_transform,
    "pirate": pirate_transform,
    "emoji": emoji_transform,
    "yoda": yoda_transform,
    "mallock": mallock_transform,
    "zalgo": zalgo_transform,
    "shakespeare": shakespeare_transform,
    "piglatin": piglatin_transform,
    "morse": morse_transform,
    "roman": roman_transform,
}


def get_available_modes() -> List[str]:
    """
    Get a list of all available transformation modes.

    Returns:
        List of available transformation mode names
    """
    return list(TRANSFORMERS.keys())


def apply_transform(text: str, mode: str) -> str:
    """
    Apply a specific transformation to the given text.

    Args:
        text: The input text to transform
        mode: The transformation mode to apply

    Returns:
        The transformed text

    Raises:
        ValueError: If the specified mode is not available
    """
    if mode not in TRANSFORMERS:
        available_modes = ", ".join(get_available_modes())
        raise ValueError(
            f"Unknown transformation mode '{mode}'. Available modes: {available_modes}"
        )

    return TRANSFORMERS[mode](text)
