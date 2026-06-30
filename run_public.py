"""Run Streamlit app with public ngrok URL"""
import os
import sys
import threading
import time
import logging

logger = logging.getLogger(__name__)

# Disable pyngrok logs
logging.getLogger("pyngrok").setLevel(logging.WARNING)


def run_streamlit():
    """Start Streamlit app in a subprocess"""
    try:
        os.system("streamlit run app.py")
    except Exception as e:
        logger.error("Failed to start Streamlit: %s", e, exc_info=True)
        print(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)


def start_ngrok():
    """Start ngrok tunnel to expose Streamlit app publicly"""
    time.sleep(3)  # Wait for streamlit to start
    try:
        from pyngrok import ngrok
    except ImportError:
        print("❌ pyngrok not installed. Install with: pip install pyngrok")
        return
    except Exception as e:
        print(f"❌ Failed to load pyngrok: {e}")
        return

    try:
        # Kill any existing ngrok tunnels
        ngrok.kill()
        logger.info("Killed existing ngrok tunnels")
        
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
        logger.error("Failed to start ngrok: %s", e, exc_info=True)
        print(f"❌ Error starting ngrok: {e}")
        print("\n💡 Troubleshooting:")
        print("  1. Set your ngrok auth token:")
        print("     ngrok config add-authtoken YOUR_TOKEN")
        print("  2. Get your token at: https://dashboard.ngrok.com/signup")
        print("  3. Check internet connection")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Starting Streamlit app with public ngrok tunnel...")
    logger.info("Initializing Streamlit + ngrok")
    
    # Start streamlit in a thread
    st_thread = threading.Thread(target=run_streamlit, daemon=True)
    st_thread.start()
    
    # Start ngrok tunnel
    start_ngrok()
