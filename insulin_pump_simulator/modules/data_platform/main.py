from fastapi import FastAPI
import requests

app = FastAPI()

CLOUD_URL = "http://localhost:8001/cloud_data"

@app.post("/send_to_cloud")
async def send_to_cloud(data: dict):
    try:
        response = requests.post(CLOUD_URL, json=data)
        response.raise_for_status()
        return {"status": "success", "message": "Data sent to cloud"}
    except Exception as e:
        return {"status": "error", "message": str(e)}