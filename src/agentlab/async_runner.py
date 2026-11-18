"""Run a coroutine from synchronous code (CLI commands, Alembic)."""

import asyncio
import sys
from collections.abc import Coroutine
from typing import Any


def run_async[T](coroutine: Coroutine[Any, Any, T]) -> T:
    """Run `coroutine` to completion on a fresh event loop.

    psycopg's async mode cannot use Windows' default Proactor loop, so on Windows
    the selector loop is used instead.
    """
    if sys.platform == "win32":
        return asyncio.run(coroutine, loop_factory=asyncio.SelectorEventLoop)
    return asyncio.run(coroutine)
