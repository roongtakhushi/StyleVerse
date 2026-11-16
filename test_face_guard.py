import urllib.request
import json

# Login to get token
login_req = urllib.request.Request(
    'http://127.0.0.1:8000/api/auth/login',
    data=json.dumps({'email': 'khushi@styleverse.com', 'password': 'Password123!'}).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(login_req) as resp:
    token = json.loads(resp.read().decode())['access_token']

# Attempt to upload face portrait to /wardrobe/upload
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
with open(r'Project\test_samples\boy_selfie_1.jpg', 'rb') as f:
    img_data = f.read()

part1 = f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="boy_selfie_1.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode()
part2 = f'\r\n--{boundary}--\r\n'.encode()
body = part1 + img_data + part2

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/wardrobe/upload',
    data=body,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Authorization': f'Bearer {token}'
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        print('Upload allowed (Unexpected!):', resp.status)
except urllib.error.HTTPError as e:
    print('✓ Face Portrait Guard successfully blocked face upload!')
    print('  Status:', e.code)
    print('  Detail:', e.read().decode())
