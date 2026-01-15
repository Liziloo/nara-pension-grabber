#!/bin/bash
# 1. System Tools
sudo apt update && sudo apt install aria2 img2pdf python3-venv -y

# 2. Python Venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 3. Permissions
chmod +x nara_bridge.py

# 4. Firefox Registration
mkdir -p ~/.mozilla/native-messaging-hosts
USER_PATH=$(pwd)
cat <<EOF > ~/.mozilla/native-messaging-hosts/com.nara.pension.grabber.json
{
  "name": "com.nara.pension.grabber",
  "description": "NARA Orchestrator",
  "path": "$USER_PATH/venv/bin/python",
  "args": ["$USER_PATH/nara_bridge.py"],
  "type": "stdio",
  "allowed_extensions": ["pension-grabber@familysearch.org"]
}
EOF

echo "Done. Now load the 'extension' folder into Firefox about:debugging."