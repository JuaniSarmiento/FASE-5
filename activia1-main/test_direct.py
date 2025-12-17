#!/usr/bin/env python3
"""Test directo del tutor para ver errores"""
import requests
import json

# Login
login_resp = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "estudiante@activia.com", "password": "estudiante123"}
)
print(f"Login: {login_resp.status_code}")
login_data = login_resp.json()
token = login_data["data"]["tokens"]["access_token"]
user_id = login_data["data"]["user"]["id"]

# Create session
session_resp = requests.post(
    "http://localhost:8000/api/v1/sessions",
    headers={"Authorization": f"Bearer {token}"},
    json={"student_id": user_id, "activity_id": "prog2_tp1", "mode": "TUTOR"}
)
print(f"Session: {session_resp.status_code}")
session_data = session_resp.json()
session_id = session_data["data"]["session_id"]
print(f"Session ID: {session_id}")

# Send interaction
interaction_resp = requests.post(
    "http://localhost:8000/api/v1/interactions",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "session_id": session_id,
        "prompt": "Explícame qué es una base de datos relacional y cómo funcionan las claves primarias."
    }
)
print(f"\nInteraction: {interaction_resp.status_code}")
print(f"Response: {json.dumps(interaction_resp.json(), indent=2)}")
