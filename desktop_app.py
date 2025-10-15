import flet as ft
import asyncio
import aiohttp
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
import setup_dependencies

TUNNEL_TOKEN = "eyJhIjoiOGZiYzg1NDYzOGU2MjE4YWRjYWQwMWM5NDA3NDU3MjUiLCJ0IjoiYmM5YzZmNjgtNGViMy00YTA1LWE5YjMtMGE3YTg0MmE3MWUxIiwicyI6Ik9ETmhZMlV3TVRjdE16STFOUzAwTWpabUxXRXhOekV0TkdJd01UTm1aVGM1TnpoayJ9"

class WhatsAppCheckerApp:
    def __init__(self):
        self.api_process = None
        self.whatsapp_process = None
        self.tunnel_process = None
        self.is_running = False
        self.deps = None
        self.stats = {
            "total_checks": 0,
            "registered": 0,
            "not_registered": 0,
            "uptime": "00:00:00"
        }
        
    def setup_dependencies(self, log_area):
        self.log_message(log_area, "🔧 Setting up dependencies...")
        self.deps = setup_dependencies.setup_all()
        return self.deps
        
    async def start_servers(self, page, log_area, status_text):
        try:
            # Setup dependencies first
            if not self.deps:
                self.setup_dependencies(log_area)
            
            # Determine node command
            node_cmd = "node"
            if self.deps and self.deps.get("nodejs_path"):
                system = setup_dependencies.get_platform()
                if system == "windows":
                    node_cmd = str(Path(self.deps["nodejs_path"]) / "node.exe")
                else:
                    node_cmd = str(Path(self.deps["nodejs_path"]) / "bin" / "node")
            
            self.log_message(log_area, "🚀 Starting WhatsApp server...")
            
            self.whatsapp_process = subprocess.Popen(
                [node_cmd, "whatsapp_server.js"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            await asyncio.sleep(3)
            self.log_message(log_area, "✅ WhatsApp server started")
            
            self.log_message(log_area, "🚀 Starting API server...")
            
            self.api_process = subprocess.Popen(
                [sys.executable, "api_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            await asyncio.sleep(3)
            self.log_message(log_area, "✅ API server started")
            
            self.log_message(log_area, "🚀 Starting Cloudflare Tunnel...")
            
            # Determine cloudflared command
            cloudflared_cmd = "cloudflared"
            if self.deps and self.deps.get("cloudflared_path"):
                cloudflared_cmd = self.deps["cloudflared_path"]
            
            try:
                self.tunnel_process = subprocess.Popen(
                    [cloudflared_cmd, "tunnel", "run", "--token", TUNNEL_TOKEN],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                await asyncio.sleep(2)
                self.log_message(log_area, "✅ Tunnel started - https://checkwa.elwe.qzz.io")
            except FileNotFoundError:
                self.log_message(log_area, "⚠️ cloudflared not found, tunnel not started")
            
            self.is_running = True
            status_text.value = "🟢 Running"
            status_text.color = ft.colors.GREEN
            page.update()
            
            asyncio.create_task(self.monitor_stats(page, log_area))
            
        except Exception as e:
            self.log_message(log_area, f"❌ Error starting servers: {str(e)}")
            status_text.value = "🔴 Error"
            status_text.color = ft.colors.RED
            page.update()
    
    def stop_servers(self, log_area, status_text, page):
        try:
            self.log_message(log_area, "⏹️ Stopping servers...")
            
            if self.tunnel_process:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=5)
                self.log_message(log_area, "✅ Tunnel stopped")
            
            if self.api_process:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                self.log_message(log_area, "✅ API server stopped")
            
            if self.whatsapp_process:
                self.whatsapp_process.terminate()
                self.whatsapp_process.wait(timeout=5)
                self.log_message(log_area, "✅ WhatsApp server stopped")
            
            self.is_running = False
            status_text.value = "🔴 Stopped"
            status_text.color = ft.colors.RED
            page.update()
            
        except Exception as e:
            self.log_message(log_area, f"❌ Error stopping servers: {str(e)}")
    
    def log_message(self, log_area, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_area.value += f"[{timestamp}] {message}\n"
        log_area.update()
    
    async def monitor_stats(self, page, log_area):
        while self.is_running:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:5000/stats") as response:
                        if response.status == 200:
                            self.stats = await response.json()
                            self.log_message(
                                log_area,
                                f"📊 Stats - Total: {self.stats['total_checks']}, "
                                f"Registered: {self.stats['registered']}, "
                                f"Not Registered: {self.stats['not_registered']}"
                            )
            except:
                pass
            
            await asyncio.sleep(30)
    
    async def upload_session(self, page, log_area, file_picker):
        if file_picker.result and file_picker.result.files:
            file_path = file_picker.result.files[0].path
            self.log_message(log_area, f"📤 Uploading session file: {file_path}")
            
            try:
                async with aiohttp.ClientSession() as session:
                    with open(file_path, 'rb') as f:
                        data = aiohttp.FormData()
                        data.add_field('session_file', f, filename=os.path.basename(file_path))
                        
                        async with session.post(
                            "http://localhost:5000/upload-session",
                            data=data
                        ) as response:
                            if response.status == 200:
                                self.log_message(log_area, "✅ Session uploaded successfully!")
                            else:
                                error = await response.text()
                                self.log_message(log_area, f"❌ Upload failed: {error}")
            except Exception as e:
                self.log_message(log_area, f"❌ Error uploading: {str(e)}")

def main(page: ft.Page):
    page.title = "WhatsApp Number Checker"
    page.window_width = 900
    page.window_height = 700
    page.window_resizable = False
    
    app = WhatsAppCheckerApp()
    
    status_text = ft.Text("🔴 Stopped", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.RED)
    
    log_area = ft.TextField(
        value="",
        multiline=True,
        read_only=True,
        min_lines=20,
        max_lines=20,
        bgcolor=ft.colors.BLACK,
        color=ft.colors.GREEN,
        border_color=ft.colors.GREEN,
    )
    
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    async def start_clicked(e):
        start_btn.disabled = True
        stop_btn.disabled = False
        page.update()
        await app.start_servers(page, log_area, status_text)
    
    def stop_clicked(e):
        start_btn.disabled = False
        stop_btn.disabled = True
        app.stop_servers(log_area, status_text, page)
    
    async def upload_clicked(e):
        file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["json"]
        )
    
    async def create_session_clicked(e):
        phone_number = phone_input.value
        if not phone_number:
            app.log_message(log_area, "❌ Please enter a phone number")
            return
        
        app.log_message(log_area, f"🔐 Creating session for: {phone_number}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:5000/create-session",
                    json={"phoneNumber": phone_number}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        code = result.get('pairingCode', 'N/A')
                        app.log_message(log_area, f"✅ Pairing Code: {code}")
                        pairing_code_text.value = f"Pairing Code: {code}"
                        page.update()
                    else:
                        error = await response.text()
                        app.log_message(log_area, f"❌ Failed: {error}")
        except Exception as e:
            app.log_message(log_area, f"❌ Error: {str(e)}")
    
    start_btn = ft.ElevatedButton(
        "▶️ Start",
        on_click=start_clicked,
        bgcolor=ft.colors.GREEN,
        color=ft.colors.WHITE,
        width=150,
        height=50
    )
    
    stop_btn = ft.ElevatedButton(
        "⏹️ Stop",
        on_click=stop_clicked,
        bgcolor=ft.colors.RED,
        color=ft.colors.WHITE,
        width=150,
        height=50,
        disabled=True
    )
    
    upload_btn = ft.ElevatedButton(
        "📤 Upload Session",
        on_click=upload_clicked,
        bgcolor=ft.colors.BLUE,
        color=ft.colors.WHITE,
        width=200,
        height=50
    )
    
    phone_input = ft.TextField(
        label="Phone Number (with country code)",
        width=300,
        hint_text="+1234567890"
    )
    
    create_session_btn = ft.ElevatedButton(
        "🔐 Create Session",
        on_click=create_session_clicked,
        bgcolor=ft.colors.ORANGE,
        color=ft.colors.WHITE,
        width=200,
        height=50
    )
    
    pairing_code_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
    
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(
                        "WhatsApp Number Checker",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    padding=20
                ),
                ft.Row(
                    [ft.Text("Status:", size=20), status_text],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    [start_btn, stop_btn],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                ft.Divider(),
                ft.Row(
                    [upload_btn],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    [phone_input, create_session_btn],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                ft.Row(
                    [pairing_code_text],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Divider(),
                ft.Text("Console Output:", size=16, weight=ft.FontWeight.BOLD),
                log_area
            ]),
            padding=20
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
