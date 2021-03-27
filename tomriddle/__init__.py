"""Top-level package for Tom Riddle."""

__author__ = """Matt Rixman"""
__email__ = "MatrixManAtYrService@users.noreply.github.com"
__version__ = "0.1.0"

from .tomriddle import main, riddler
from .fragments import (
    gen_default_fragments,
    get_default_fragments,
    get_fragments_from,
    Fragments,
)
