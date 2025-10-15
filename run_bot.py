import subprocess
import sys
import time
import os

TUNNEL_TOKEN = "eyJhIjoiOGZiYzg1NDYzOGU2MjE4YWRjYWQwMWM5NDA3NDU3MjUiLCJ0IjoiYmM5YzZmNjgtNGViMy00YTA1LWE5YjMtMGE3YTg0MmE3MWUxIiwicyI6Ik9ETmhZMlV3TVRjdE16STFOUzAwTWpabUxXRXhOekV0TkdJd01UTm1aVGM1TnpoayJ9"

def main():
    print("Starting WhatsApp Number Checker with Telegram Bot...")
    print("=" * 60)
    
    whatsapp_process = None
    api_process = None
    bot_process = None
    tunnel_process = None
    
    try:
        print("\n[1/4] Starting WhatsApp Server...")
        whatsapp_process = subprocess.Popen(
            ["node", "whatsapp_server.js"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ WhatsApp Server started (PID: {})".format(whatsapp_process.pid))
        time.sleep(3)
        
        print("\n[2/4] Starting API Server...")
        api_process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ API Server started (PID: {})".format(api_process.pid))
        time.sleep(3)
        
        print("\n[3/4] Starting Cloudflare Tunnel...")
        try:
            tunnel_process = subprocess.Popen(
                ["cloudflared", "tunnel", "run", "--token", TUNNEL_TOKEN],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("✅ Tunnel started (PID: {})".format(tunnel_process.pid))
            print("🌐 Public URL: https://checkwa.elwe.qzz.io")
            time.sleep(2)
        except FileNotFoundError:
            print("⚠️  cloudflared not found, tunnel not started")
            print("   API available locally only at http://localhost:5000")
        
        print("\n[4/4] Starting Telegram Bot...")
        bot_process = subprocess.Popen(
            [sys.executable, "telegram_bot.py"]
        )
        print("✅ Telegram Bot started (PID: {})".format(bot_process.pid))
        time.sleep(2)
        
        print("\n" + "=" * 60)
        print("🚀 All services are running!")
        print("=" * 60)
        print("\nLocal API: http://localhost:5000")
        print("Public URL: https://checkwa.elwe.qzz.io")
        print("WhatsApp Server: http://localhost:3000")
        print("Telegram Bot: Running for admin 7011309417")
        print("\nPress Ctrl+C to stop all services...")
        print("=" * 60)
        
        while True:
            time.sleep(1)
            
            if whatsapp_process.poll() is not None:
                print("\n⚠️  WhatsApp Server stopped unexpectedly!")
                break
            
            if api_process.poll() is not None:
                print("\n⚠️  API Server stopped unexpectedly!")
                break
            
            if bot_process.poll() is not None:
                print("\n⚠️  Telegram Bot stopped unexpectedly!")
                break
            
            if tunnel_process and tunnel_process.poll() is not None:
                print("\n⚠️  Tunnel stopped unexpectedly!")
                
    except KeyboardInterrupt:
        print("\n\nStopping all services...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if tunnel_process:
            print("Stopping Tunnel...")
            tunnel_process.terminate()
            tunnel_process.wait()
        
        if bot_process:
            print("Stopping Telegram Bot...")
            bot_process.terminate()
            bot_process.wait()
        
        if api_process:
            print("Stopping API Server...")
            api_process.terminate()
            api_process.wait()
        
        if whatsapp_process:
            print("Stopping WhatsApp Server...")
            whatsapp_process.terminate()
            whatsapp_process.wait()
        
        print("\n✅ All services stopped")
        print("Goodbye!")

if __name__ == "__main__":
    main()
