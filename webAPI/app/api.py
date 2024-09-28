import base64
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
import os
import asyncio
import re

import docker

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

STATIC_DIR = "/app/static"

app = FastAPI()

origins = [
    "*",  # Add the frontend origin
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define a custom logging filter
class UpdateImageEndpointFilter(logging.Filter):
    def filter(self, record):
        # Filter out POST requests to /update_image
        return "/update_image" not in record.getMessage()

class LogsEndpointFilter(logging.Filter):
    def filter(self, record):
        # Filter out POST requests to /update_image
        return "/micro_ros_agent_logs" not in record.getMessage()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.access")
logger.addFilter(UpdateImageEndpointFilter())
# logger.addFilter(LogsEndpointFilter())

class ImageData(BaseModel):
    data: str

class WebSocketConnection:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.is_running = False
        self.connection_type = None
    
    def is_text(self):
        return self.connection_type == "text"

    async def handle(self):
        try:
            await self.websocket.accept()
            self.is_running = True
            print(f"Websocket connection ACCEPTED: {self.websocket}")
            
            while self.is_running:
                try:
                    data = await asyncio.wait_for(self.websocket.receive_text(), timeout=1.0)
                    print(f"Received data: {data}")
                    if "READY" in data:
                        self.connection_type = "text"
                        await self.websocket.send_text('{"type": "PONG"}')
                    elif "IMAGE" in data:
                        self.connection_type = "image"
                except asyncio.TimeoutError:
                    # No data received, just continue the loop
                    continue

        except WebSocketDisconnect:
            print("[WEBSOCKET CONNECTION ERROR] : WebSocket disconnected")
        except Exception as e:
            print(f"[WEBSOCKET CONNECTION ERROR] : {e}")
        finally:
            self.is_running = False
            await self.close()

    async def close(self):
        if not self.websocket.client_state.DISCONNECTED:
            await self.websocket.close()
        active_connections.remove(self)

    async def send_text(self, text):
        if self.is_running:
            await self.websocket.send_text(text)

active_connections: list[WebSocketConnection] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(f"[INFO WEBSOCKET] Websocket connection request obtained: {websocket}")
    connection = WebSocketConnection(websocket)
    active_connections.append(connection)
    await connection.handle()

# Example API route
@app.get("/")
async def get_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.post("/start")
async def start_action():
    for conn in active_connections:
        if conn.is_text():
            await conn.send_text('{"type": "PONG"}')
    return {"status": "success", "message": "Started"}

@app.post("/restart")
async def restart_action():
    for conn in active_connections:
        if conn.is_text():
            await conn.send_text('{"type": "RESET"}')
        # await active_connections[-1].send_text('{"type": "RESET"}')  # Use valid JSON format
    return {"status": "success", "message": "Restarted"}

@app.post("/connections")
async def calculate_connections():
    print(f"Number of connections: {len(active_connections)}")
    return {"status": "success", "count": str(len(active_connections))}

async def broadcast_image(image_data: str):
    for conn in active_connections:
        if not conn.is_text():
            await conn.send_text(f'{{"type": "IMAGE", "data": "{image_data}"}}')
    # await image_active_socket[-1].send_text(f'{{"type": "IMAGE", "data": "{image_data}"}}')

@app.post("/update_image")
async def update_image(image_data: ImageData):
    try:
        # Assuming the image data is already base64 encoded
        await broadcast_image(image_data.data)
        return {"status": "success", "message": "Image broadcasted"}
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail="Error broadcasting image")


def clean_log(log):
    # Regex pattern to match the escape sequences for color codes
    escape_sequence = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return escape_sequence.sub('', log)

@app.get("/micro_ros_agent_logs")
async def get_microros_logs():
    client = docker.from_env()
    try:
        container = client.containers.get("rover_ros2-micro_ros_agent-1")
        logs = container.logs(tail=20).decode("utf-8")
        cleaned_logs = clean_log(logs)
        return {"logs": cleaned_logs}
    except docker.errors.NotFound:
        return {"error": "micro_ros_agent container not found"}
    except Exception as e:
        print(e)
        return {"error": str(e)}

@app.get("/rover_logs")
async def get_rover_logs():
    client = docker.from_env()
    try:
        container = client.containers.get("rover_humble")
        logs = container.logs(tail=50).decode("utf-8")
        cleaned_logs = clean_log(logs)
        return {"logs": cleaned_logs}
    except docker.errors.NotFound:
        return {"error": "micro_ros_agent container not found"}
    except Exception as e:
        print(e)
        return {"error": str(e)}