from async_terminal import AsyncTerminal
import asyncio

async def run_calculator():
    async def calculate(expression: str, _) -> float:
        return eval(expression)
    
    # Custom formatter
    def format_calc_result(expression: str, result: float) -> str:
        return f"🧮 {expression} = {result}"
    
    # Create and run terminal
    terminal = AsyncTerminal(
        async_handler=calculate,
        format_output=format_calc_result,
        startup_message="🎯 Async Calculator Ready! Type math expressions..."
    )
    
    await terminal.run()

def main():
    asyncio.run(run_calculator())

if __name__ == "__main__":
    main()

