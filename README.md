# NARA Pension Archive Bridge 📜

A high-performance Linux orchestrator that bridges **FamilySearch** and the **National Archives (NARA)**. 

This tool allows you to find a Revolutionary War pension file on FamilySearch and, with one click, trigger a multi-threaded download of the original NARA master images, which are then stitched into a lossless PDF for your Zotero library.

## 🛠️ Architecture
- **Browser:** Firefox Extension (scrapes NAID and page counts).
- **Glue:** Python 3 + `requests` (runs in a local `venv`).
- **Engines:** `aria2c` (Multi-threaded downloads) and `img2pdf` (Lossless PDF conversion).
- **Communication:** Mozilla Native Messaging API.

## 🚀 Installation (Pop!_OS / Ubuntu)

1. **Clone the Repo:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/nara-pension-grabber.git](https://github.com/YOUR_USERNAME/nara-pension-grabber.git)
   cd nara-pension-grabber
   ```

2. **Run the Setup Script:**
   This installs system tools, creates the `venv`, and registers the bridge with Firefox.
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Install the Extension:**
   - Open Firefox and go to `about:debugging#/runtime/this-firefox`.
   - Click **Load Temporary Add-on**.
   - Select the `manifest.json` inside the `extension/` folder.

## 📂 Project Structure
- `nara_bridge.py`: The primary orchestrator (Native Host).
- `setup.sh`: Automated installer and Firefox registration.
- `extension/`: Firefox background scripts and manifest.
- `requirements.txt`: Python dependencies (`requests`).

## 📖 Usage
1. Open any Revolutionary War Pension file on **FamilySearch**.
2. Click the **NARA Archive Bridge** icon in your Firefox toolbar.
3. The script will:
   - Resolve the NARA S3 URLs via API.
   - Download images in parallel via `aria2c`.
   - Generate a PDF in `~/Documents/Pensions`.
   - Open the folder automatically via `xdg-open`.

## 🧪 Troubleshooting
If the bridge fails to trigger, check the Firefox **Browser Console** (`Ctrl+Shift+J`). Look for "Native Messaging" errors. Ensure the path in `~/.mozilla/native-messaging-hosts/com.nara.pension.grabber.json` correctly points to your `venv` Python and the `nara_bridge.py` script.