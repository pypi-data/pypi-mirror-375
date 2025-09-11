"""Mermaid diagram builder (stub).

Builds a simple Mermaid flowchart or graph source string. This is a
lightweight stub that emits mermaid source suitable for embedding in
Markdown or rendering with mermaid CLI/tools.
"""

from __future__ import annotations

import logging
import sys as _sys

_LOGGER = logging.getLogger("x_make")


def _info(*args: object) -> None:
    msg = " ".join(str(a) for a in args)
    try:
        _LOGGER.info("%s", msg)
    except Exception:
        pass
    try:
        print(msg)
    except Exception:
        try:
            _sys.stdout.write(msg + "\n")
        except Exception:
            pass


class x_cls_make_mermaid_x:
    """Simple Mermaid builder stub.

    Supports flowchart style building: nodes and edges. The internal
    representation is intentionally minimal so it can be extended later.
    """

    def __init__(
        self, direction: str = "LR", ctx: object | None = None
    ) -> None:
        # direction: LR (left-right), TB (top-bottom), etc.
        self.direction = direction
        self._ctx = ctx
        self._lines: list[str] = [f"flowchart {self.direction}"]

    def add_node(self, node_id: str, label: str | None = None) -> None:
        label_part = f"[{label}]" if label is not None else ""
        self._lines.append(f"{node_id}{label_part}")

    def add_edge(self, src: str, dst: str, label: str | None = None) -> None:
        if label:
            self._lines.append(f"{src} -->|{label}| {dst}")
        else:
            self._lines.append(f"{src} --> {dst}")

    def source(self) -> str:
        """Return the mermaid source string."""
        return "\n".join(self._lines) + "\n"

    def save(self, path: str = "diagram.mmd") -> str:
        """Save the mermaid source to a file and return the path."""
        src = self.source()
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        if getattr(self._ctx, "verbose", False):
            # inlined helper to avoid importing shared module
            import logging as _logging

            _LOGGER = _logging.getLogger("x_make")

            def _info(*args: object) -> None:
                msg = " ".join(str(a) for a in args)
                try:
                    _LOGGER.info("%s", msg)
                except Exception:
                    pass
                try:
                    print(msg)
                except Exception:
                    try:
                        import sys as _sys

                        _sys.stdout.write(msg + "\n")
                    except Exception:
                        pass

            _info(f"[mermaid] saved mermaid source to {path}")
        return path


def main() -> str:
    m = x_cls_make_mermaid_x()
    m.add_node("A", "Start")
    m.add_node("B", "End")
    m.add_edge("A", "B", "next")
    return m.source()


if __name__ == "__main__":
    _info(main())
