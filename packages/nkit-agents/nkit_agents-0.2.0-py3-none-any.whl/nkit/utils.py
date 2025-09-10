import asyncio
import inspect
import json
import logging
from typing import Any, Callable


def setup_logger(name: str = "nbagents", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def is_async_function(func: Callable) -> bool:
    return asyncio.iscoroutinefunction(func)


async def run_sync_or_async(func: Callable, *args, **kwargs) -> Any:
    if is_async_function(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)


def parse_schema(func: Callable):
    return [{'name': n, 'type': p.annotation.__name__ if p.annotation != inspect.Parameter.empty else 'str'}
            for n, p in inspect.signature(func).parameters.items() if n != 'self']
