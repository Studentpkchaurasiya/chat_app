import asyncio
import websockets
import sys
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

async def chat_client():
    uri = "ws://13.233.131.198:8001/ws/chat/"
    username = input("Enter your username: ")

    async with websockets.connect(uri) as websocket:
        # first message = username
        await websocket.send(username)

        recipient = input("Enter recipient username: ")
        print(f"Connected to chat with {recipient}. Type 'quit' to exit.\n")

        session = PromptSession()

        async def send_msg():
            while True:
                with patch_stdout():
                    msg = await session.prompt_async("You: ")
                if msg.lower() == "quit":
                    await websocket.close()
                    break
                data = {"to": recipient, "message": msg}
                await websocket.send(json.dumps(data))

        async def receive_messages():
            try:
                async for raw in websocket:
                    try:
                        data = json.loads(raw)
                        sender = data.get("from", "server")
                        msg = data.get("message", raw)
                        sys.stdout.write(f"\r{sender}: {msg}\n")
                        sys.stdout.flush()
                    except:
                        print(raw)
            except websockets.exceptions.ConnectionClosed:
                print("Disconnected from server")

        await asyncio.gather(send_msg(), receive_messages())

asyncio.run(chat_client())
