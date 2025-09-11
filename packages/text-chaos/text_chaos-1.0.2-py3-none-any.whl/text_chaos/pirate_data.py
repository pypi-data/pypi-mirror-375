"""
Pirate transformation data.

This module contains the dictionaries and lists used for pirate speak transformations.
You can modify these dictionaries to customize the pirate transformation behavior.
"""

from typing import Dict, List

# Pirate word replacements - regex patterns mapped to pirate equivalents
PIRATE_REPLACEMENTS: Dict[str, str] = {
    # Greetings
    r"\bhello\b": "ahoy",
    r"\bhi\b": "ahoy",
    r"\bhey\b": "ahoy",
    # People
    r"\bfriend\b": "matey",
    r"\bfriends\b": "mateys",
    r"\bman\b": "lad",
    r"\bwoman\b": "lass",
    r"\bpeople\b": "crew",
    r"\bguys\b": "mateys",
    # Pronouns and verbs
    r"\byou\b": "ye",
    r"\byour\b": "yer",
    r"\byou\'re\b": "ye be",
    r"\bare\b": "be",
    r"\bmy\b": "me",
    r"\bover\b": "o'er",
    r"\bfor\b": "fer",
    r"\bto\b": "ter",
    # Common words
    r"\bmoney\b": "doubloons",
    r"\bgold\b": "treasure",
    r"\bstop\b": "avast",
    r"\byes\b": "aye",
    r"\byeah\b": "aye",
    r"\bno\b": "nay",
    r"\bokay\b": "aye aye",
    r"\bok\b": "aye",
    r"\bdrink\b": "grog",
    r"\bfight\b": "battle",
    # Places
    r"\bhouse\b": "cabin",
    r"\bhome\b": "ship",
    r"\bbathroom\b": "head",
    r"\bkitchen\b": "galley",
    r"\bfloor\b": "deck",
    # Fun additions
    r"\bawesome\b": "shipshape",
    r"\bgreat\b": "grand",
    r"\bgood\b": "fine",
    r"\bbad\b": "cursed",
    r"\bterrible\b": "scurvy",
    r"\bgoodbye\b": "farewell",
    r"\bbye\b": "fare ye well",
    r"\bgood morning\b": "top o' the mornin'",
    r"\bgood night\b": "fair winds",
    r"\bcheers\b": "yo ho ho",
    r"\bchild\b": "young buccaneer",
    r"\bkid\b": "wee lad",
    r"\bboy\b": "cabin boy",
    r"\bgirl\b": "lassie",
    r"\bcaptain\b": "cap’n",
    r"\bboss\b": "cap’n",
    r"\bthief\b": "scallywag",
    r"\bcoward\b": "lily-livered dog",
    r"\bvillain\b": "blackheart",
    r"\bdo not\b": "don’t ye",
    r"\bdon\'t\b": "don’t ye",
    r"\bgoing\b": "goin’",
    r"\bing\b": "in’",
    r"\bwith\b": "wit’",
    r"\bthem\b": "’em",
    r"\bfood\b": "grub",
    r"\bdrink\b": "rum",
    r"\bbeer\b": "ale",
    r"\bflag\b": "jolly roger",
    r"\btreasure\b": "booty",
    r"\bsword\b": "cutlass",
    r"\bgun\b": "blunderbuss",
    r"\bfear\b": "dread",
    r"\bhurry\b": "scurry",
    r"\bcrazy\b": "mad as a hatter",
    r"\bstupid\b": "addled",
    r"\bdrunk\b": "three sheets to the wind",
    r"\bcowardly\b": "yellow-bellied",
    r"\blucky\b": "blessed by the sea",
    r"\bunlucky\b": "cursed by Davy Jones",
}

# Pirate exclamations that can be added to the end of sentences
PIRATE_EXCLAMATIONS: List[str] = [
    "Arr!",
    "Avast!",
    "Shiver me timbers!",
    "Batten down the hatches!",
    "Yo ho ho!",
    "Yo ho ho and a bottle o’ rum!",
    "Dead men tell no tales!",
    "Blimey!",
    "By Blackbeard’s ghost!",
    "Scurvy dogs!",
    "Sink me!",
    "Walk the plank!",
    "Hoist the colors!",
    "Raise the Jolly Roger!",
]
