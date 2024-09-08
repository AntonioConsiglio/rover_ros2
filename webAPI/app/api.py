from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import os

from fastapi.middleware.cors import CORSMiddleware

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

active_connections: list[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"Connection added: {websocket}")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data: {data}")
            if "READY" in data:
                await websocket.send_text('{"type": "PONG"}')
            # Handle received data if needed
    except WebSocketDisconnect:
        pass
        # active_connections.remove(websocket)  # Remove disconnected socket

# Example API route
@app.get("/")
async def get_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.post("/start")
async def start_action():
    if active_connections:
        await active_connections[-1].send_text('{"type": "PONG"}')
    return {"status": "success", "message": "Started"}

@app.post("/restart")
async def restart_action():
    if active_connections:
        await active_connections[-1].send_text('{"type": "RESET"}')  # Use valid JSON format
    return {"status": "success", "message": "Restarted"}

@app.post("/connections")
async def calculate_connections():
    print(f"Number of connections: {len(active_connections)}")
    return {"status": "success", "count": str(len(active_connections))}