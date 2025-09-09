"""Caching example demonstrating ContextCache usage."""

import asyncio
import random

from enrichmcp import EnrichMCP

app = EnrichMCP("Caching API", instructions="Demo of request caching")


@app.retrieve
async def slow_square(n: int) -> int:
    """Return n squared using request-scoped caching."""
    ctx = app.get_context()

    async def compute() -> int:
        await asyncio.sleep(0.1)
        return n * n

    return await ctx.cache.get_or_set(f"square:{n}", compute)


@app.retrieve
async def fibonacci(n: int) -> int:
    """Compute the n-th Fibonacci number with global caching."""
    ctx = app.get_context()

    async def compute() -> int:
        await asyncio.sleep(0.1)
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    return await ctx.cache.get_or_set(f"fib:{n}", compute, scope="global")


@app.retrieve
async def user_analytics() -> dict:
    """Return fake analytics for the user with user-scoped caching."""
    ctx = app.get_context()

    async def compute() -> dict:
        await asyncio.sleep(0.1)
        return {"clicks": random.randint(50, 150)}

    return await ctx.cache.get_or_set("analytics", compute, scope="user", ttl=300)


if __name__ == "__main__":
    app.run()
