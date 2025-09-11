"""File I/O helpers."""

from __future__ import annotations


class IOService:
    """Simple file I/O service.

    Examples
    --------
    >>> io = IOService()
    >>> io.write_text('example.txt', 'hello')
    >>> io.read_text('example.txt')
    'hello'
    """

    def read_text(self, path: str) -> str:
        """Read text from ``path`` using UTF-8 encoding."""

        with open(path, encoding="utf-8") as f:
            return f.read()

    def write_text(self, path: str, data: str) -> None:
        """Write ``data`` to ``path`` using UTF-8 encoding."""

        with open(path, "w", encoding="utf-8") as f:
            f.write(data)


__all__ = ["IOService"]
