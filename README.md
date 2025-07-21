# AsyncTerminal

**Turn any async function into a responsive terminal app**

Stop waiting for long operations to finish. Build terminals that stay interactive while processing database queries, API calls, or file operations in the background.

```python
# Your async function
async def process(cmd: str, resources):
    return await your_async_operation(cmd)

# Instant terminal
terminal = AsyncTerminal(process)
await terminal.run()
```

## Install

```bash
pip install async-terminal
```

## Examples

**Database Terminal**
```python
import asyncpg
from async_terminal import AsyncTerminal

async def query(sql: str, pool):
    async with pool.acquire() as conn:
        return dict(await conn.fetchrow(sql))

async def setup():
    return await asyncpg.create_pool("postgresql://localhost/db")

terminal = AsyncTerminal(query, setup_resources=setup)
await terminal.run()
```

**API Testing Terminal**
```python
import aiohttp

async def fetch(url: str, session):
    async with session.get(url) as resp:
        return f"{resp.status} - {len(await resp.text())} bytes"

async def setup():
    return aiohttp.ClientSession()

terminal = AsyncTerminal(fetch, setup_resources=setup)
await terminal.run()
```

**File Processing Terminal**
```python
async def analyze(filepath: str, _):
    with open(filepath) as f:
        return f"Lines: {len(f.readlines())}"

terminal = AsyncTerminal(analyze)
await terminal.run()
```

## What You Get

- ✅ **Concurrent execution** - run multiple commands at once
- ✅ **Non-blocking UI** - terminal stays responsive during long operations  
- ✅ **Auto error handling** - exceptions displayed cleanly
- ✅ **Resource management** - automatic setup/cleanup
- ✅ **Live updates** - see results as they complete

## API

```python
AsyncTerminal(
    async_handler,           # (user_input, resources) -> result
    setup_resources=None,    # () -> resources
    cleanup_resources=None,  # (resources) -> None
    format_output=None,      # (input, result) -> display_string
    startup_message="Ready!"
)
```

## Perfect For

- Database query tools
- HTTP/API clients  
- File batch processors
- DevOps command runners
- Real-time monitoring dashboards

## Demo

```
🎯 Database Terminal Ready!
> SELECT * FROM users LIMIT 5;
✅ Query completed: {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}

> SELECT COUNT(*) FROM orders;
✅ Query completed: {'count': 15420}

> INVALID SQL QUERY;
❌ Error: syntax error at or near "INVALID"
```

Multiple queries run concurrently. No waiting, no blocking.

## Requirements

- Python 3.8+
- Zero dependencies
