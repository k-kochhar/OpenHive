import asyncio
import websockets


class RobotClient:
    """WebSocket client for communicating with robot"""
    
    def __init__(self, host="localhost", port=8765, device_id="ESP1"):
        self.host = host
        self.port = port
        self.device_id = device_id
        self.uri = f"ws://{host}:{port}"
        self.websocket = None
        self.connected = False
    
    async def connect(self):
        """Connect to WebSocket server and register device"""
        try:
            self.websocket = await asyncio.wait_for(
                websockets.connect(
                    self.uri, 
                    ping_interval=20, 
                    ping_timeout=20
                ),
                timeout=3.0
            )
            
            await self.websocket.send(f"ID:{self.device_id}")
            response = await asyncio.wait_for(self.websocket.recv(), timeout=2.0)
            
            if response == "REGISTERED":
                self.connected = True
                return True
            
            return False
            
        except:
            self.connected = False
            return False
    
    async def send_command(self, command):
        """Send movement command to robot"""
        if not self.connected or self.websocket is None:
            return False
        
        try:
            await self.websocket.send(command)
            return True
        except:
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
        self.connected = False
