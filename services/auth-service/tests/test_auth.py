import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_login(monkeypatch):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # register (use random email to avoid uniqueness)
        r = await ac.post("/auth/register", json={"email":"test+1@example.com","password":"secret"})
        assert r.status_code in (200,201)
        # login
        resp = await ac.post("/auth/token", data={"username":"test+1@example.com","password":"secret"})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body