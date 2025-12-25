"""
Glyph definitions for Sovwren IDE.

Centralizes all icon/glyph usage with Nerd Font primary and ASCII fallbacks.
Toggle USE_NERD_FONTS to switch between them.
"""

# Set to False if Nerd Fonts aren't rendering in your terminal
USE_NERD_FONTS = True

# Nerd Font glyphs (Font Awesome subset)
_NERD = {
    # Gates & security
    "lock": "\uf023",
    "unlock": "\uf09c",
    "globe": "\uf0ac",
    "cloud": "\uf0c2",

    # Files & folders
    "file": "\uf15b",
    "folder": "\uf07b",
    "save": "\uf0c7",

    # Actions
    "search": "\uf002",
    "gear": "\uf013",
    "bookmark": "\uf02e",

    # Modes
    "wrench": "\uf0ad",      # Workshop
    "moon": "\uf186",        # Sanctuary (candle alternative)

    # Status
    "clock": "\uf017",
    "calendar": "\uf073",
    "comment": "\uf075",     # Chat/exchanges
    "chart": "\uf080",       # Monitor/stats

    # Lens (colored circles - using Unicode for color support)
    "blue": "●",
    "red": "●",
    "purple": "●",

    # Misc
    "expand": "\uf065",
    "warning": "\uf071",
    "thread": "\uf126",      # Sessions/history
    "handshake": "\uf2b5",   # Social carryover on
    "square": "○",           # Social carryover off (hollow circle)
    "bulb": "\uf0eb",        # Hints
    "chat": "\uf27a",        # Chat mode
    "robot": "\uf544",       # Models/AI
    "mirror": "\uf074",      # Profiles (random icon stand-in)
    "upload": "\uf093",      # Push
    "download": "\uf019",    # Pull
    "pencil": "\uf040",      # Edit/commit
    "memo": "\uf15c",        # Notes/commit message
    "thought": "\uf10d",     # Thought/reasoning (quote-left as stand-in)
}

# ASCII/Unicode fallbacks
_FALLBACK = {
    "lock": "[X]",
    "unlock": "[ ]",
    "globe": "(W)",
    "cloud": "(C)",
    "file": "[f]",
    "folder": "[D]",
    "save": "[S]",
    "search": "[?]",
    "gear": "[*]",
    "bookmark": "[B]",
    "wrench": "[W]",
    "moon": "[~]",
    "clock": "[@]",
    "calendar": "[#]",
    "comment": "[>]",
    "chart": "[|]",
    "blue": "o",
    "red": "o",
    "purple": "o",
    "expand": "[^]",
    "warning": "[!]",
    "thread": "[=]",
    "handshake": "[+]",
    "square": "[-]",
    "bulb": "[i]",
    "chat": "[>]",
    "robot": "[A]",
    "mirror": "[M]",
    "upload": "[U]",
    "download": "[D]",
    "pencil": "[E]",
    "memo": "[N]",
    "thought": "[?]",
}

def g(name: str) -> str:
    """Get a glyph by name. Returns fallback if Nerd Fonts disabled."""
    source = _NERD if USE_NERD_FONTS else _FALLBACK
    return source.get(name, "?")

# Direct exports for convenience
LOCK = g("lock")
UNLOCK = g("unlock")
GLOBE = g("globe")
CLOUD = g("cloud")
FILE = g("file")
FOLDER = g("folder")
SAVE = g("save")
SEARCH = g("search")
GEAR = g("gear")
BOOKMARK = g("bookmark")
WRENCH = g("wrench")
MOON = g("moon")
CLOCK = g("clock")
CALENDAR = g("calendar")
COMMENT = g("comment")
CHART = g("chart")
LENS_BLUE = g("blue")
LENS_RED = g("red")
LENS_PURPLE = g("purple")
EXPAND = g("expand")
WARNING = g("warning")
THREAD = g("thread")
HANDSHAKE = g("handshake")
SQUARE = g("square")
BULB = g("bulb")
CHAT = g("chat")
ROBOT = g("robot")
MIRROR = g("mirror")
UPLOAD = g("upload")
DOWNLOAD = g("download")
PENCIL = g("pencil")
MEMO = g("memo")
THOUGHT = g("thought")
