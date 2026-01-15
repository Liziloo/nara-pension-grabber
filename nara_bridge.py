#!/usr/bin/env python3
import sys, json, struct, os, subprocess, requests
from pathlib import Path

# --- DEBUG LOGGING ---
DEBUG_LOG = Path("/home/liz/GitHub/nara-pension-grabber/bridge_debug.log")
with open(DEBUG_LOG, "a") as f:
    f.write("Bridge triggered by Firefox\n")

SAVE_PATH = Path.home() / "Documents/Pensions"
SAVE_PATH.mkdir(parents=True, exist_ok=True)

def get_message():
    # Use .buffer to read raw bytes from the stream
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len: 
        return None
    msg_len = struct.unpack('@I', raw_len)[0]
    msg_bytes = sys.stdin.buffer.read(msg_len).decode('utf-8')
    return json.loads(msg_bytes)

def run():
    try:
        msg = get_message()
        if not msg or 'naid' not in msg:
            with open(DEBUG_LOG, "a") as f: f.write("No NAID in message\n")
            return
        
        naid = msg['naid']
        with open(DEBUG_LOG, "a") as f: f.write(f"Processing NAID: {naid}\n")
        
        temp_dir = Path(f"/tmp/nara_{naid}")
        temp_dir.mkdir(exist_ok=True)

        # 1. Resolve URLs via NARA API
        resp = requests.get(f"https://catalog.archives.gov/api/v2/records/{naid}", timeout=20).json()
        
        # Note: NARA API V2 structure can be deep; ensuring we grab the list
        objects = resp.get('record', {}).get('digitalObjects', [])
        urls = [obj['accessUrl'] for obj in objects if 'accessUrl' in obj]
        
        if not urls:
            with open(DEBUG_LOG, "a") as f: f.write("No URLs found for this NAID\n")
            return

        # 2. Download with aria2c
        url_file = temp_dir / "urls.txt"
        url_file.write_text("\n".join(urls))
        
        # CRITICAL: Added stdout/stderr=DEVNULL so aria2c doesn't talk to Firefox
        subprocess.run(
            ["aria2c", "-i", str(url_file), "-d", str(temp_dir), "-j", "16", "-x", "16", "--quiet=true"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        # 3. Stitch with img2pdf
        pdf_file = SAVE_PATH / f"NARA_{naid}.pdf"
        imgs = sorted([str(p) for p in temp_dir.glob("*.jpg")])
        
        if imgs:
            subprocess.run(
                ["img2pdf"] + imgs + ["-o", str(pdf_file)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        # 4. Clean up and Open Folder
        subprocess.run(["rm", "-rf", str(temp_dir)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # This opens the folder so you know it's done
        subprocess.run(["xdg-open", str(SAVE_PATH)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    except Exception as e:
        with open(DEBUG_LOG, "a") as f:
            f.write(f"CRASH: {str(e)}\n")

if __name__ == "__main__":
    run()
    sys.exit(0) # Ensure clean exit