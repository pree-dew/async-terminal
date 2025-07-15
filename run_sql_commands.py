from async_terminal import AsyncTerminal
import asyncpg
import asyncio

async def run_sql_commands():
    async def run_query(query: str, pool) -> dict:
        async with pool.acquire() as connection:
            result = await connection.fetchrow(query)
            return dict(result) if result else {}
    
    # Resource setup
    async def setup_db_pool():
        return await asyncpg.create_pool(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            database='postgres',
            min_size=6,
            max_size=6
        )
    
    # Resource cleanup
    async def cleanup_db_pool(pool):
        await pool.close()
    
    # Custom output formatter
    def format_db_result(query: str, result: dict) -> str:
        if result:
            return f"🗃️  Query: {query} | Columns: {len(result)} | Data: {result}"
        else:
            return f"📭 Query: {query} | No results found"
    
    # Create and run terminal
    terminal = AsyncTerminal(
        async_handler=run_query,
        setup_resources=setup_db_pool,
        cleanup_resources=cleanup_db_pool,
        format_output=format_db_result,
        startup_message="🎯 Database Query Terminal Ready! Type your SQL queries..."
    )
    
    await terminal.run()


def main():
    asyncio.run(run_sql_commands())

if __name__ == "__main__":
    main()

