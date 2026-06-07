"""widpath - hierarchical file-path resolver for WID-based storage.

Quick start::

    from pathlib import Path
    from widpath import locate, WidPathResolver

    # Functional interface (canonical linear-scan algorithm)
    path = locate(Path("data/nodes"), "4a3f9c2b1e0d5678abcd1234567890ab")

    # OOP interface (binary-search variant)
    resolver = WidPathResolver()
    path = resolver.resolve("4a3f9c2b1e0d5678abcd1234567890ab", Path("data/nodes"))
"""



from .resolver import WidPathResolver, locate

__all__ = ["WidPathResolver", "locate"]
__version__ = "0.2.0"
