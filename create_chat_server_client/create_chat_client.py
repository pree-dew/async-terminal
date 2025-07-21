import sys
import asyncio
from asyncio import StreamReader, StreamWriter
from typing import Callable, Any, Optional

from async_terminal import AsyncTerminal

class ChatConnection:
    def __init__(self, reader: StreamReader, writer: StreamWriter, username: str, listener_task):
        self.reader = reader
        self.writer = writer
        self.username = username
        self.listener_task = listener_task

class ChatClient:
    def __init__(self):
        self.terminal = None
    
    async def send_message(self, user_input: str, resources: ChatConnection):
        """Send message to chat server"""
        try:
            resources.writer.write((user_input + '\n').encode())
            await resources.writer.drain()
            # Show the sent message
            await self.terminal.msg_store.append(f"📤 {resources.username}: {user_input}")
        except Exception as e:
            raise e  # Let AsyncTerminal handle the error display
    
    async def setup_chat(self):
        """Setup chat connection and start listening for messages"""
        sys.stdout.write("enter username:")
        sys.stdout.flush()

        # Simple username input
        username = input().strip()
        print(f"Connecting as {username}...")
        
        # Connect to server
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', 8000)
            writer.write(f'CONNECT {username}\n'.encode())
            await writer.drain()
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            sys.exit(1)
        
        # Start background task to listen for server messages
        async def listen_for_messages():
            while True:
                try:
                    message = await reader.readline()
                    if not message:
                        await self.terminal.msg_store.append("🔌 Server disconnected")
                        break
                    await self.terminal.msg_store.append(f"📨 {message.decode().strip()}")
                except Exception as e:
                    await self.terminal.msg_store.append(f"❌ Connection error: {e}")
                    break
        
        listener_task = asyncio.create_task(listen_for_messages())
        return ChatConnection(reader, writer, username, listener_task)
    
    async def cleanup_chat(self, resources: ChatConnection):
        """Cleanup chat connection"""
        resources.listener_task.cancel()
        try:
            await resources.listener_task
        except asyncio.CancelledError:
            pass
        
        resources.writer.close()
        await resources.writer.wait_closed()
    
    def format_chat_message(self, user_input: str, result: Any) -> str:
        """Don't show result messages for chat"""
        return ""
    
    async def run(self):
        """Run the chat client"""
        # Create the terminal
        self.terminal = AsyncTerminal(
            async_handler=self.send_message,
            setup_resources=self.setup_chat,
            cleanup_resources=self.cleanup_chat,
            format_output=self.format_chat_message,
            startup_message="💬 Chat connected! Type messages to send..."
        )
        
        # Run the terminal
        await self.terminal.run()

async def main():
    chat_client = ChatClient()
    await chat_client.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Chat client stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")

