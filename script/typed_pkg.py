"""List typed packages."""
from __future__ import annotations

from importlib.metadata import files, packages_distributions


def main() -> None:
    """List typed packages."""

    pkgs = {p for items in packages_distributions().values() for p in items}

    typed: set[str] = set()
    for pkg in pkgs:
        if any(path for path in files(pkg) or () if "py.typed" in str(path)):
            typed.add(pkg)

    print("\n".join(sorted(typed)))
    print(f"------\nFound: {len(typed)} strictly typed packages")


if __name__ == "__main__":
    main()
