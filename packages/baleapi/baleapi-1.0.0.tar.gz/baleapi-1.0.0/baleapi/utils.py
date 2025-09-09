import asyncio
from typing import Callable, Any

def run_async(func: Callable[..., Any], *args, **kwargs):
    
    return asyncio.run(func(*args, **kwargs))