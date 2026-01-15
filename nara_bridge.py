#!/usr/bin/env python3
import sys, json, struct, os, subprocess, requests
from pathlib import Path

# --- DEBUG LOGGING ---
# Using absolute path for reliability on Linux
DEBUG_LOG = Path("/home/liz/GitHub/nara-pension-grabber/bridge_debug.log")

def log(text):
    with open(DEBUG_LOG, "a") as f:
        f.write(f"{text}\n")

SAVE_PATH = Path.home() / "Documents/Pensions"
SAVE_PATH.mkdir(parents=True, exist_ok=True)

def get_message():
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len: 
        return None
    msg_len = struct.unpack('@I', raw_len)[0]
    msg_bytes = sys.stdin.buffer.read(msg_len).decode('utf-8')
    return json.loads(msg_bytes)

def run():
    log("Bridge triggered by Firefox")
    try:
        msg = get_message()
        if not msg or 'naid' not in msg:
            log("No valid message or NAID received")
            return
        
        naid = msg['naid']
        log(f"Processing NAID: {naid}")
        
        temp_dir = Path(f"/tmp/nara_{naid}")
        temp_dir.mkdir(exist_ok=True)

        # 1. Resolve URLs via NARA API V1
        headers = {'User-Agent': 'Mozilla/5.0 (NARA Pension Grabber)'}
        api_url = f"https://catalog.archives.gov/api/v1?naIds={naid}"
        
        response = requests.get(api_url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            log(f"API Error {response.status_code}")
            return

        resp_data = response.json()
        
        # --- FIXED V1 PARSING LOGIC ---
        # V1 path: opaResponse -> results -> result -> [list] -> objects -> object -> [list] -> file -> @url
        try:
            results = resp_data.get('opaResponse', {}).get('results', {}).get('result', [])
            if not results:
                log(f"No results found in V1 for {naid}")
                return
            
            # Extract objects from the first result found
            res_objects = results[0].get('objects', {}).get('object', [])
            
            # Handle cases where there is only 1 image (V1 turns it into a dict instead of a list)
            if isinstance(res_objects, dict):
                res_objects = [res_objects]
                
            urls = [obj.get('file', {}).get('@url') for obj in res_objects if obj.get('file')]
            urls = [u for u in urls if u] # Remove empty entries
        except Exception as parse_err:
            log(f"JSON Parsing Error: {str(parse_err)}")
            return
        # ------------------------------

        if not urls:
            log(f"No image URLs extracted for {naid}")
            return

        log(f"Found {len(urls)} images. Downloading with aria2c...")

        # 2. Download with aria2c
        url_file = temp_dir / "urls.txt"
        url_file.write_text("\n".join(urls))
        
        subprocess.run(
            ["aria2c", "-i", str(url_file), "-d", str(temp_dir), "-j", "16", "-x", "16", "--quiet=true"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        # 3. Stitch with img2pdf
        log("Stitching PDF...")
        pdf_file = SAVE_PATH / f"NARA_{naid}.pdf"
        imgs = sorted([str(p) for p in temp_dir.glob("*") if p.suffix.lower() in ['.jpg', '.jpeg']])
        
        if imgs:
            subprocess.run(
                ["img2pdf"] + imgs + ["-o", str(pdf_file)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            log(f"Success! PDF saved to {pdf_file}")
        else:
            log("No images found in temp folder to stitch.")

        # 4. Clean up and Open Folder
        subprocess.run(["rm", "-rf", str(temp_dir)], stdout=subprocess.DEVNULL)
        subprocess.run(["xdg-open", str(SAVE_PATH)], stdout=subprocess.DEVNULL)
        
    except Exception as e:
        log(f"CRASH: {str(e)}")

if __name__ == "__main__":
    run()
    sys.exit(0)