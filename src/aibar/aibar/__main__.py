"""
@file
@brief Module execution entry point for aibar.
@details Delegates to aibar.cli:main to enable `python -m aibar` invocation.
@satisfies REQ-024
"""

from aibar.cli import main

if __name__ == "__main__":
    main()  # pyright: ignore[reportCallIssue]
