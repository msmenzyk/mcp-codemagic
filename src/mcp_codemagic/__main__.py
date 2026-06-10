"""Entry point: ``python -m mcp_codemagic`` or the ``mcp-codemagic`` console script."""

from .server import mcp


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
