from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os

from agent_loop import run_debate

app = FastAPI()

# Frontend dosyalarını sunmak için
# statik klasörünü oluşturacağız.
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.websocket("/ws/debate")
async def websocket_debate(websocket: WebSocket):
    await websocket.accept()
    try:
        # Client'tan başlangıç config'ini alıyoruz
        data_str = await websocket.receive_text()
        data = json.loads(data_str)
        
        user_idea = data.get("idea", "")
        model_name = data.get("model", "gemini-2.5-pro")
        max_loops = int(data.get("loops", 5))
        
        if not user_idea:
            await websocket.send_json({"agent": "System_Error", "message": "Fikir boş olamaz!"})
            await websocket.close()
            return

        # Tartışma döngüsünü başlat ve mesajları anlık gönder
        async for message_info in run_debate(user_idea, model_name, max_loops):
            await websocket.send_json(message_info)
            
    except WebSocketDisconnect:
        print("İstemci bağlantıyı kesti")
    except Exception as e:
        await websocket.send_json({"agent": "System_Error", "message": str(e)})
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
