import subprocess
import sys
import time
import os

def main():
    print("Starting WhatsApp Number Checker System...")
    print("=" * 50)
    
    whatsapp_process = None
    api_process = None
    
    try:
        print("\n[1/2] Starting WhatsApp Server...")
        whatsapp_process = subprocess.Popen(
            ["node", "whatsapp_server.js"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ WhatsApp Server started (PID: {})".format(whatsapp_process.pid))
        time.sleep(3)
        
        print("\n[2/2] Starting API Server...")
        api_process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ API Server started (PID: {})".format(api_process.pid))
        time.sleep(3)
        
        print("\n" + "=" * 50)
        print("🚀 All servers are running!")
        print("=" * 50)
        print("\nAPI Server: http://localhost:5000")
        print("WhatsApp Server: http://localhost:3000")
        print("\nPress Ctrl+C to stop all servers...")
        print("=" * 50)
        
        while True:
            time.sleep(1)
            
            if whatsapp_process.poll() is not None:
                print("\n⚠️  WhatsApp Server stopped unexpectedly!")
                break
            
            if api_process.poll() is not None:
                print("\n⚠️  API Server stopped unexpectedly!")
                break
                
    except KeyboardInterrupt:
        print("\n\nStopping servers...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if api_process:
            print("Stopping API Server...")
            api_process.terminate()
            api_process.wait()
        
        if whatsapp_process:
            print("Stopping WhatsApp Server...")
            whatsapp_process.terminate()
            whatsapp_process.wait()
        
        print("\n✅ All servers stopped")
        print("Goodbye!")

if __name__ == "__main__":
    main()
