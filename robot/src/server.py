import asyncio
import websockets

HOST = "0.0.0.0"
PORT = 8765

devices = {}
controllers = {}


async def handler(ws):
    client_id = None
    is_robot = False
    
    try:
        async for msg in ws:
            msg = msg.strip()

            if msg.startswith("ID:"):
                client_id = msg[3:].strip()
                if not client_id:
                    await ws.send("ERR:EMPTY_ID")
                    continue

                # Determine if this is a robot (ESP) or controller
                if client_id.startswith("ESP"):
                    devices[client_id] = ws
                    is_robot = True
                    print(f"Robot registered: {client_id}")
                else:
                    controllers[client_id] = ws
                    print(f"Controller registered: {client_id}")

                await ws.send("REGISTERED")
                
                if is_robot:
                    await ws.send("S")

                continue

            # Handle targeted commands: TARGET:ESP1:F
            if not is_robot and msg.startswith("TARGET:"):
                parts = msg.split(":", 2)
                if len(parts) == 3:
                    _, target_device, command = parts
                    if target_device in devices:
                        try:
                            await devices[target_device].send(command)
                            print(f"Forwarded {command} -> {target_device}")
                        except:
                            devices.pop(target_device, None)
                continue
            
            # If message is a command (F, B, L, R, S), forward to all robots
            if not is_robot and msg in ["F", "B", "L", "R", "S"]:
                dead = []
                for device_id, device_ws in list(devices.items()):
                    try:
                        await device_ws.send(msg)
                        print(f"Forwarded {msg} -> {device_id}")
                    except:
                        dead.append(device_id)
                for device_id in dead:
                    devices.pop(device_id, None)
            else:
                # Log other messages
                if client_id:
                    print(f"From {client_id}: {msg}")

    except websockets.ConnectionClosed:
        pass
    finally:
        if client_id:
            if is_robot and devices.get(client_id) is ws:
                devices.pop(client_id, None)
                print(f"Robot disconnected: {client_id}")
            elif not is_robot and controllers.get(client_id) is ws:
                controllers.pop(client_id, None)
                print(f"Controller disconnected: {client_id}")


async def main():
    print(f"WebSocket server listening on ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT, ping_interval=20, ping_timeout=20):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
