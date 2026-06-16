import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Login
resp = client.post("/api/v1/auth/login", json={
    "email": "nguyenquoctien0000@gmail.com",
    "password": "user123"
})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("=== ACCOUNT APIs ===\n")

# 1. GET /users/me (Account Summary)
resp = client.get("/api/v1/users/me", headers=headers)
print("1. GET /users/me -", resp.status_code)
for k, v in resp.json().items():
    print(f"   {k}: {v}")

# 2. PUT /users/me (Update Profile)
resp = client.put("/api/v1/users/me", headers=headers, json={
    "full_name": "Nguyen Quoc Tien Updated"
})
print("\n2. PUT /users/me -", resp.status_code)
print(f"   full_name: {resp.json()['full_name']}")

# 3. POST /users/me/change-password
resp = client.post("/api/v1/users/me/change-password", headers=headers, json={
    "current_password": "user123",
    "new_password": "newpass123"
})
print("\n3. POST /users/me/change-password -", resp.status_code)
print(f"   {resp.json()}")

# 4. Login with new password
resp = client.post("/api/v1/auth/login", json={
    "email": "nguyenquoctien0000@gmail.com",
    "password": "newpass123"
})
print("\n4. Login with new password -", resp.status_code, "(expected 200)")

# 5. Login with old password (should fail)
resp = client.post("/api/v1/auth/login", json={
    "email": "nguyenquoctien0000@gmail.com",
    "password": "user123"
})
print("5. Login with old password -", resp.status_code, "(expected 401)")

# 6. GET /users/ (list all users)
resp = client.get("/api/v1/users/", headers=headers)
print("\n6. GET /users/ -", resp.status_code)
data = resp.json()
print(f"   total: {data['total']} users")
for u in data["items"]:
    print(f"   [{u['id']}] {u['email']} - {u['full_name']}")

# 7. Change password back
token2 = client.post("/api/v1/auth/login", json={
    "email": "nguyenquoctien0000@gmail.com",
    "password": "newpass123"
}).json()["access_token"]
headers2 = {"Authorization": f"Bearer {token2}"}
resp = client.post("/api/v1/users/me/change-password", headers=headers2, json={
    "current_password": "newpass123",
    "new_password": "user123"
})
print("\n7. Reset password -", resp.status_code)
