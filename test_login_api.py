import urllib.request
import json

url = "http://127.0.0.1:8000/api/auth/login"

for email in ["khushi.test1@styleverse.com", "khushi@styleverse.com", "Khushi@styleverse.com ", "KHUSHI.TEST1@STYLEVERSE.COM"]:
    data = json.dumps({"email": email, "password": "Password123!"}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode())
            name = body["user"]["name"]
            tok_len = len(body["access_token"])
            print(f"✓ Login SUCCESS for {email!r}: User = {name}, Token = {tok_len} chars")
    except urllib.error.HTTPError as e:
        print(f"✗ Login FAILED for {email!r}: {e.code} - {e.read().decode()}")
    except Exception as e:
        print(f"✗ Connection error for {email!r}: {e}")
