# NARA Pension Grabber 📜

A specialized tool for researchers to batch-download Revolutionary War pension files from the National Archives (NARA) and combine them into high-quality, lossless PDFs for Zotero.

## Setup for Ubuntu

1. **Clone the repository:**

```bash
git clone [https://github.com/YOUR_USERNAME/nara-pension-grabber.git](https://github.com/YOUR_USERNAME/nara-pension-grabber.git)
cd nara-pension-grabber
```

2. **Install System Dependencies:**

```bash
sudo apt update && sudo apt install python3-tk img2pdf -y
```

3. **Initialize Environment:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

1. Activate the environment:

```bash
source venv/bin/activate
```

2. Run the tool:

```bash
python3 nara_grabber.py
```

3. Paste a NARA URL or NAID (e.g., 196632154) and hit **Generate PDF**.

## Browser Integration (Firefox Bookmarklet)

TO quickly grab IDs from NARA