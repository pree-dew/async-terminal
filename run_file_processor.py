from async_terminal import AsyncTerminal
import asyncio
import os

async def run_file_processor():
    async def process_file(filepath: str, _) -> dict:
        # Simulate file processing
        await asyncio.sleep(0.1)  # Simulate I/O
        
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            with open(filepath, 'r') as f:
                lines = len(f.readlines())
            return {"size": size, "lines": lines, "exists": True}
        else:
            return {"exists": False}
    
    # Custom formatter
    def format_file_result(filepath: str, result: dict) -> str:
        if result["exists"]:
            return f"📄 {filepath} | Size: {result['size']} bytes | Lines: {result['lines']}"
        else:
            return f"❌ File not found: {filepath}"
    
    # Create and run terminal
    terminal = AsyncTerminal(
        async_handler=process_file,
        format_output=format_file_result,
        startup_message="🎯 File Processor Ready! Type file paths to analyze..."
    )
    
    await terminal.run()

def main():
    asyncio.run(run_file_processor())

if __name__ == "__main__":
    main()

