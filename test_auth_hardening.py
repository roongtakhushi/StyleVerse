import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.database import connect_to_mongo, db_instance

def run_tests():
    print("=" * 60)
    print("STYLEVERSE AUTH HARDENING TEST SUITE")
    print("=" * 60)

    # 1. Connect to Mongo
    asyncio.run(connect_to_mongo())
    assert db_instance.db is not None, "Database instance should not be None"
    print("✓ Database connected successfully. Storage mode:", "fallback" if db_instance.is_fallback else "atlas")

    with TestClient(app) as client:
        # TEST 1: Dual route verification (Both /api/auth/login and /auth/login must not 404)
        print("\n[TEST 1] Dual-Route Resolution (/api prefix and root alias)")
        r1 = client.post("/api/auth/login", json={"email": "nonexistent@test.com", "password": "123"})
        r2 = client.post("/auth/login", json={"email": "nonexistent@test.com", "password": "123"})
        print(f"POST /api/auth/login -> status: {r1.status_code}, detail: {r1.json().get('detail')}")
        print(f"POST /auth/login      -> status: {r2.status_code}, detail: {r2.json().get('detail')}")
        assert r1.status_code == 404 and r1.json().get("detail") == "No account found with this email. Please check your email or sign up."
        assert r2.status_code == 404 and r2.json().get("detail") == "No account found with this email. Please check your email or sign up."
        print("✓ Both /api/auth/login and /auth/login resolved to the same endpoint without 404 Route Not Found!")

        # TEST 2: Registration with brand new user
        test_email = f"verified_user_{int(datetime.utcnow().timestamp())}@styleverse.com"
        print(f"\n[TEST 2] User Registration with: {test_email}")
        reg_res = client.post("/api/auth/register", json={
            "name": "Audit Test User",
            "email": test_email,
            "password": "SecurePassword123!",
            "gender_preference": "unisex"
        })
        print(f"Registration status: {reg_res.status_code}")
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        reg_data = reg_res.json()
        assert "access_token" in reg_data
        assert reg_data["user"]["email"] == test_email
        print(f"✓ Registration SUCCESS! User ID: {reg_data['user']['id']}, Token generated.")

        # TEST 3: Duplicate Registration Guard
        print("\n[TEST 3] Duplicate Registration Guard")
        dup_res = client.post("/api/auth/register", json={
            "name": "Duplicate User",
            "email": test_email,
            "password": "SecurePassword123!"
        })
        print(f"Duplicate status: {dup_res.status_code}, detail: {dup_res.json().get('detail')}")
        assert dup_res.status_code == 400
        assert "already exists" in dup_res.json().get("detail", "")
        print("✓ Duplicate registration correctly rejected with 400 Bad Request!")

        # TEST 4: Login with correct credentials
        print("\n[TEST 4] Login with registered user")
        login_res = client.post("/api/auth/login", json={
            "email": test_email,
            "password": "SecurePassword123!"
        })
        print(f"Login status: {login_res.status_code}")
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data["access_token"]
        assert login_data["user"]["email"] == test_email
        print("✓ Login SUCCESS with valid JWT token.")

        # TEST 5: Login with WRONG password
        print("\n[TEST 5] Login with wrong password")
        wrong_pwd_res = client.post("/api/auth/login", json={
            "email": test_email,
            "password": "WrongPassword999!"
        })
        print(f"Wrong password status: {wrong_pwd_res.status_code}, detail: {wrong_pwd_res.json().get('detail')}")
        assert wrong_pwd_res.status_code == 401
        assert "Incorrect password" in wrong_pwd_res.json().get("detail", "")
        print("✓ Wrong password rejected with 401 Unauthorized and explicit guidance!")

        # TEST 6: Authenticated /users/me check
        print("\n[TEST 6] Authenticated session validation (/users/me)")
        me_res = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        print(f"/users/me status: {me_res.status_code}, User: {me_res.json().get('name')}")
        assert me_res.status_code == 200
        assert me_res.json().get("email") == test_email
        print("✓ Authenticated session valid! User persists properly.")

        # TEST 7: 503 DB Disconnect Guard
        print("\n[TEST 7] Database Disconnect Guard (503 Service Unavailable)")
        saved_db = db_instance.db
        try:
            db_instance.db = None
            r_down = client.post("/api/auth/login", json={"email": "any@test.com", "password": "123"})
            print(f"When DB is None -> status: {r_down.status_code}, detail: {r_down.json().get('detail')}")
            assert r_down.status_code == 503
            assert "initializing" in r_down.json().get("detail", "")
            print("✓ 503 Guard working! No phantom tokens generated when DB is unavailable.")
        finally:
            db_instance.db = saved_db

    print("\n" + "=" * 60)
    print("ALL 7 AUTH HARDENING TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
