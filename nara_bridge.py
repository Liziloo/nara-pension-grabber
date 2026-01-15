#!/usr/bin/env python3
import sys, json, struct, os, subprocess, requests
from pathlib import Path

# Change this path to your preferred permanent folder
SAVE_PATH = Path.home() / "Documents/Pensions"
SAVE_PATH.mkdir(parents=True, exist_ok=True)

def get_message():
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len: return None
    msg_len = struct.unpack('@I', raw_len)[0]
    return json.loads(sys.stdin.buffer.read(msg_len).decode('utf-8'))

def send_status(text):
    # Optional: Send messages back to browser console
    msg = json.dumps({"status": text}).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('@I', len(msg)))
    sys.stdout.buffer.write(msg)
    sys.stdout.buffer.flush()

def run():
    msg = get_message()
    if not msg or 'naid' not in msg: return
    
    naid = msg['naid']
    temp_dir = Path(f"/tmp/nara_{naid}")
    temp_dir.mkdir(exist_ok=True)

    try:
        # 1. Resolve URLs via NARA API
        resp = requests.get(f"https://catalog.archives.gov/api/v2/records/{naid}", timeout=20).json()
        objects = resp.get('record', {}).get('digitalObjects', [])
        urls = [obj['accessUrl'] for obj in objects if 'accessUrl' in obj]
        
        if not urls: return

        # 2. Download with aria2c
        url_file = temp_dir / "urls.txt"
        url_file.write_text("\n".join(urls))
        # -j16 = 16 concurrent downloads, -x16 = 16 connections per server
        subprocess.run(["aria2c", "-i", str(url_file), "-d", str(temp_dir), "-j", "16", "-x", "16", "--quiet=true"])

        # 3. Stitch with img2pdf
        pdf_file = SAVE_PATH / f"NARA_{naid}.pdf"
        imgs = sorted([str(p) for p in temp_dir.glob("*.jpg")])
        subprocess.run(["img2pdf"] + imgs + ["-o", str(pdf_file)])

        # 4. Clean up and Open Folder
        subprocess.run(["rm", "-rf", str(temp_dir)])
        subprocess.run(["xdg-open", str(SAVE_PATH)])
        
    except Exception as e:
        with open(str(SAVE_PATH / "error.log"), "a") as f:
            f.write(f"Failed {naid}: {str(e)}\n")

if __name__ == "__main__":
    run()