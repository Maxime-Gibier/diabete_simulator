from fastapi import FastAPI

app = FastAPI()

@app.post("/cloud_data")
async def receive_data(data: dict):
    print(f"[CLOUD] Données reçues : {data}")
    return {"status": "success", "message": "Data received"}
