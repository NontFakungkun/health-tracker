"""
Run this once to add your Google service account credentials to secrets.toml.
Usage: python setup_gsheets.py path/to/your-key-file.json
"""
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python setup_gsheets.py path/to/your-key-file.json")
    sys.exit(1)

key_path = Path(sys.argv[1])
if not key_path.exists():
    print(f"File not found: {key_path}")
    sys.exit(1)

with open(key_path) as f:
    creds = json.load(f)

secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"

# Read existing secrets
existing = secrets_path.read_text(encoding="utf-8") if secrets_path.exists() else ""

# Remove any existing gcp block
lines = existing.splitlines()
filtered = []
skip = False
for line in lines:
    if line.strip() == "[gcp_service_account]":
        skip = True
    elif line.startswith("[") and skip:
        skip = False
    if not skip:
        filtered.append(line)

existing_clean = "\n".join(filtered).strip()

# Build the new gcp block
private_key = creds["private_key"].replace("\n", "\\n")
gcp_block = f"""
[gcp_service_account]
type = "{creds['type']}"
project_id = "{creds['project_id']}"
private_key_id = "{creds['private_key_id']}"
private_key = "{private_key}"
client_email = "{creds['client_email']}"
client_id = "{creds['client_id']}"
auth_uri = "{creds['auth_uri']}"
token_uri = "{creds['token_uri']}"
auth_provider_x509_cert_url = "{creds['auth_provider_x509_cert_url']}"
client_x509_cert_url = "{creds['client_x509_cert_url']}"
"""

secrets_path.write_text(existing_clean + "\n" + gcp_block, encoding="utf-8")
print(f"Done. Credentials written to {secrets_path}")
print(f"Service account: {creds['client_email']}")
