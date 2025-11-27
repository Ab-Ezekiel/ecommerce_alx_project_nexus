# tests/test_auth.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_register_and_login():
    client = APIClient()
    reg_url = "/api/auth/register/"
    login_url = "/api/auth/login/"

    payload = {
        "username": "tester1",
        "email": "tester1@example.com",
        "password": "P@ssw0rd123",
        "password2": "P@ssw0rd123"
    }
    r = client.post(reg_url, payload, format="json")
    assert r.status_code == 201

    # login
    r = client.post(login_url, {"username": "tester1", "password": "P@ssw0rd123"}, format="json")
    assert r.status_code == 200
    assert "access" in r.data and "refresh" in r.data

@pytest.mark.django_db
def test_refresh_and_logout():
    client = APIClient()
    user = User.objects.create_user(username="u2", email="u2@example.com", password="P@ssw0rd123")
    login_resp = client.post("/api/auth/login/", {"username": "u2", "password": "P@ssw0rd123"}, format="json")
    refresh = login_resp.data["refresh"]
    access = login_resp.data["access"]

    # refresh
    r = client.post("/api/auth/refresh/", {"refresh": refresh}, format="json")
    assert r.status_code == 200
    assert "access" in r.data

    # logout (blacklist)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    r = client.post("/api/auth/logout/", {"refresh": refresh}, format="json")
    assert r.status_code == 200
