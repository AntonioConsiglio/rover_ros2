from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.responses import FileResponse
import os

STATIC_DIR = "app/static"

app = FastAPI()
active_connections: list[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket.send_text("{'type': 'PONG'}")
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle received data if needed
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# Example API route
@app.get("/")
async def get_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html")) 

@app.post("/start")
async def start_action():
    # Implement the logic to handle START action
    active_connections[0].send_text("{'type': 'PONG'}")
    # For example, trigger some background process or service
    return {"status": "success", "message": "Started"}

@app.post("/restart")
async def restart_action():
    # Implement the logic to handle RESTART action
    active_connections[0].send_text("{'type': 'RESET'}")
    # For example, restart some service or process
    return {"status": "success", "message": "Restarted"}

# if __name__ == "__main__":
#     uvicorn.run("app:app", host="0.0.0.0", port=8000, log_level="info")