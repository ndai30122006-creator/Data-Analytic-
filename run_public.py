"""Run Streamlit app with public ngrok URL"""
import os
import sys
import threading
import time

# Disable pyngrok logs
import logging
logging.getLogger("pyngrok").setLevel(logging.WARNING)

from pyngrok import ngrok

def run_streamlit():
    os.system("streamlit run app.py")

def start_ngrok():
    time.sleep(3)  # Wait for streamlit to start
    try:
        # Kill any existing ngrok tunnels
        ngrok.kill()
        
        # Create public URL tunnel to port 8501
        public_url = ngrok.connect(8501, "http")
        print(f"\n{'='*60}")
        print(f"🚀 PUBLIC URL: {public_url}")
        print(f"📱 Share this link with anyone to access the app!")
        print(f"{'='*60}\n")
        
        # Keep the script running
        while True:
            time.sleep(10)
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        print("Please set your ngrok auth token first:")
        print("  ngrok config add-authtoken YOUR_TOKEN")
        print("Get your token at: https://dashboard.ngrok.com/signup")

if __name__ == "__main__":
    print("Starting Streamlit app with public ngrok tunnel...")
    
    # Start streamlit in a thread
    st_thread = threading.Thread(target=run_streamlit, daemon=True)
    st_thread.start()
    
    # Start ngrok tunnel
    start_ngrok()