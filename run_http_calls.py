from async_terminal import AsyncTerminal
import aiohttp
import asyncio

async def run_api():
    async def fetch_url(url: str, session) -> dict:
        async with session.get(url) as response:
            if response.content_type == 'application/json':
                return await response.json()
            else:
                resp_text = await response.text()
                return {"status": response.status, "text": resp_text[:100]}
    
    # Resource setup
    async def setup_http_session():
        return aiohttp.ClientSession()
    
    # Resource cleanup
    async def cleanup_http_session(session):
        await session.close()
    
    # Custom formatter
    def format_api_result(url: str, result: dict) -> str:
        status = result.get('status', 'success')
        return f"🌐 URL: {url} | Status: {status} | Keys: {list(result.keys())[:5]}"
    
    # Create and run terminal
    terminal = AsyncTerminal(
        async_handler=fetch_url,
        setup_resources=setup_http_session,
        cleanup_resources=cleanup_http_session,
        format_output=format_api_result,
        startup_message="🎯 HTTP API Terminal Ready! Type URLs to fetch..."
    )
    
    await terminal.run()

def main():
    asyncio.run(run_api())

if __name__ == "__main__":
    main()

