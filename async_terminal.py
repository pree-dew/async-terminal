import asyncio
import os
import sys
import tty
import shutil
from asyncio import StreamReader
from collections import deque
from typing import Callable, Any, Optional

class MessageStore:
        def __init__(self, rows, callback):
            self._deque = deque(maxlen=rows)
            self._callback = callback

        async def append(self, msg):
            self._deque.append(msg)
            await self._callback(self._deque)

class AsyncTerminal:
    """
    A pluggable async terminal framework where you can provide your own
    async functions to be executed with user input.
    """
    
    def __init__(self, 
                 async_handler: Callable[[str, Any], Any],
                 setup_resources: Optional[Callable[[], Any]] = None,
                 cleanup_resources: Optional[Callable[[Any], None]] = None,
                 format_output: Optional[Callable[[str, Any], str]] = None,
                 startup_message: str = "🎯 Async Terminal Ready! Type your commands..."):
        """
        Initialize the async terminal.
        
        Args:
            async_handler: Async function that takes (user_input, resources) and processes it
            setup_resources: Optional function to setup resources (DB pools, API clients, etc.)
            cleanup_resources: Optional function to cleanup resources
            format_output: Optional function to format output messages
            startup_message: Message to show when terminal starts
        """
        self.async_handler = async_handler
        self.setup_resources = setup_resources
        self.cleanup_resources = cleanup_resources
        self.format_output = format_output or self._default_format
        self.startup_message = startup_message
        self.resources = None
        self.msg_store = None
        
    def _save_cursor_position(self):
        sys.stdout.write('\0337')

    def _restore_cursor_position(self):
        sys.stdout.write('\0338')

    def _move_to_top_of_screen(self):
        sys.stdout.write('\033[H')

    def _clear_line(self):
        sys.stdout.write('\033[2K\033[0G')

    def _move_back_one_char(self):
        sys.stdout.write('\033[1D')

    def _move_to_bottom_of_screen(self):
        _, total_rows = shutil.get_terminal_size()
        input_row = total_rows - 1
        sys.stdout.write(f'\033[{input_row}E')
        return total_rows

    async def _create_stdin_reader(self):
        stream_reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(stream_reader)
        loop = asyncio.get_running_loop()
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        return stream_reader

    def _default_format(self, user_input: str, result: Any) -> str:
        """Default output formatter"""
        return f"✅ Result for '{user_input}': {result}"

    async def _execute_user_function(self, user_input: str):
        """Execute the user-provided async function"""
        try:
            result = await self.async_handler(user_input, self.resources)
            formatted_msg = self.format_output(user_input, result)
            await self.msg_store.append(formatted_msg)
        except Exception as e:
            error_msg = f"❌ Error processing '{user_input}': {e}"
            await self.msg_store.append(error_msg)

    async def _read_line(self, stdin_reader: StreamReader) -> str:
        """Read user input with backspace support"""
        def erase_last_char():
            self._move_back_one_char()
            sys.stdout.write(' ')
            self._move_back_one_char()

        delete_char = b'\x7f'
        input_buffer = deque()
        
        while (char := await stdin_reader.read(1)) != b'\n':
            if char == delete_char:
                if len(input_buffer) > 0:
                    input_buffer.pop()
                    erase_last_char()
                    sys.stdout.flush()
            else:
                input_buffer.append(char)
                sys.stdout.write(char.decode())
                sys.stdout.flush()
        
        self._clear_line()
        return b''.join(input_buffer).decode()

    async def _redraw_screen(self, items: deque):
        """Refresh screen with latest messages"""
        self._save_cursor_position()
        self._move_to_top_of_screen()
        
        for item in items:
            sys.stdout.write('\033[2K')
            print(item)
        
        self._restore_cursor_position()
        sys.stdout.flush()

    async def run(self):
        """Main terminal loop"""

        try:
            # Setup user resources if provided
            if self.setup_resources:
                self.resources = await self.setup_resources()

            # Setup terminal
            tty.setcbreak(sys.stdin)
            os.system('clear')
            rows = self._move_to_bottom_of_screen()
            
            self.msg_store = MessageStore(rows - 1, self._redraw_screen)

            # Show startup message
            await self.msg_store.append(self.startup_message)

            stdin_reader = await self._create_stdin_reader()

            # Main input loop
            while True:
                user_input = await self._read_line(stdin_reader)
                if user_input.strip():
                    # Execute user function in background
                    asyncio.create_task(self._execute_user_function(user_input))

        finally:
            # Cleanup resources if provided
            if self.cleanup_resources and self.resources:
                await self.cleanup_resources(self.resources)

