import asyncio
import logging
from asyncio import StreamReader, StreamWriter

class ChatServer:
    def __init__(self):
        self._username_to_writer = {} 

    async def start_chat_server(self, host: str, port: int):
        server = await asyncio.start_server(self.client_connected, host, port)
        async with server:
            await server.serve_forever()

    async def client_connected(self, reader: StreamReader, writer: StreamWriter):
        command = await reader.readline()
        print(f'CONNECTED {reader} {writer}')
        command, args = command.split(b' ')
        if command == b'CONNECT':
            username = args.replace(b'\n', b'').decode()
            self._add_user(username, reader, writer)
            await self._on_connect(username, writer)
        else:
            logging.error('Got invalid command from client, disconencting')
            writer.close()
            await writer.wait_closed()

    def _add_user(self, username, reader: StreamReader, writer: StreamWriter):
        self._username_to_writer[username] = writer
        asyncio.create_task(self._listen_for_messages(username, reader))

    async def _on_connect(self, username: str, writer: StreamWriter):
        writer.write(f'Welcome {username}! {len(self._username_to_writer)} are online \n'.encode())
        await writer.drain()
        await self._notify_all('New user connected!\n')

    async def _notify_all(self, message):
        inactive_users = []
        for username, writer in self._username_to_writer.items():
            try:
                writer.write(message.encode())
                await writer.drain()
            except ConnectionError as e:
                logging.exception('Error while notifiying client', exc_info=e)
                inactive_users.append(username)
        [await self._remove_user(username) for username in inactive_users]

    async def _remove_user(self, username: str):
        writer = self._username_to_writer[username]
        del self._username_to_writer[username]
        try:
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logging.exception('Error removing writer.', exc_info=e)

    async def _listen_for_messages(self, username: str, reader: StreamReader):
        try:
            while (data := await asyncio.wait_for(reader.readline(), 60)) != b'':
                   await self._notify_all(f'{username}: {data.decode()}')
            await self._notify_all(f'{username} has left the chat!\n')
        except Exception as e:
                   logging.exception('Error reading from client.', exc_info=e)
                   await self._remove_user(username)

async def main():
    chat_server = ChatServer()
    await chat_server.start_chat_server('127.0.0.1', 8000)

asyncio.run(main())
