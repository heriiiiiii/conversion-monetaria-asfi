from __future__ import annotations

import asyncio
from typing import Awaitable, Iterable


async def run_parallel(tasks: Iterable[Awaitable]):
    return await asyncio.gather(*tasks)
