import pytest
import time
from fastapi.testclient import TestClient
from fastapi import Request

from authtuna.core.database import db_manager, Session as DBSession, User, AuditEvent
from authtuna.core.encryption import encryption_utils
from authtuna.helpers import create_session_and_set_cookie
from sqlalchemy import select


@pytest.mark.asyncio
async def test_database_manager_initialize_and_audit(setup_db):
    # Ensure referenced user exists for audit event
    async with db_manager.get_db() as db:
        user = User(id="u1", username="testuser1", email="test1@example.com")
        db.add(user)
        await db.commit()
    # log an event without external session (auto commit)
    ev = await db_manager.log_audit_event("u1", "TEST_EVENT", "127.0.0.1", {"k": 1})
    assert ev.id is None or isinstance(ev.id, int)  # id will be assigned after commit.
    async with db_manager.get_db() as db:
        stmt = select(AuditEvent).where(AuditEvent.event_type == "TEST_EVENT")
        res = await db.execute(stmt)
        row = res.scalar_one_or_none()
        assert row is not None
        # test with provided session (no commit inside function)
        user2 = User(id="u2", username="testuser2", email="test2@example.com")
        db.add(user2)
        await db.commit()
        ev2 = await db_manager.log_audit_event("u2", "TEST_EVENT2", db=db)
        await db.commit()
        assert ev2.event_type == "TEST_EVENT2"


@pytest.mark.asyncio
async def test_session_cookie_roundtrip_and_rotation(setup_db):
    # create a session row and test cookie encode/decode and rotation
    async with db_manager.get_db() as db:
        user = User(id="user1", username="testuser", email="test@example.com")
        db.add(user)
        await db.commit()

    async with db_manager.get_db() as db:
        s = DBSession(
            session_id=encryption_utils.gen_random_string(32),
            user_id="user1",
            region="City, Country",
            device="Chrome on Windows",
            create_ip="127.0.0.1",
            last_ip="127.0.0.1",
        )
        db.add(s)
        await db.commit()
        cookie = s.get_cookie_string()
        data = encryption_utils.decode_jwt_token(cookie)
        assert data["session"] == s.session_id
        assert data["user_id"] == s.user_id
        assert "random_string" in data
        assert data["e_abs_time"] >= time.time()

        old_rs = s.random_string
        await s.update_random_string()
        assert s.random_string != old_rs


def test_middleware_public_and_protected_routes(app):
    client = TestClient(app)

    # Public route should be accessible without cookie
    r = client.get("/public")
    assert r.status_code == 200 and r.json()["ok"] is True

    # Protected route without session: user_id should be None
    r2 = client.get("/protected")
    assert r2.status_code == 200 and r2.json()["user_id"] is None


@pytest.mark.asyncio
async def test_middleware_sets_cookie_on_login_flow(app):
    client = TestClient(app)

    # Manually create user and session using helper and verify cookie is set
    async with db_manager.get_db() as db:
        user = User(id="u-login", username="LoginUser", email="login@example.com")
        db.add(user)
        await db.commit()

    # simulate an endpoint that logs in and sets cookie
    @app.get("/do-login")
    async def do_login(request: Request):
        from fastapi import Response
        async with db_manager.get_db() as db:
            response = Response()
            await create_session_and_set_cookie(user, request, response, db)
            return response

    # Perform login to receive cookie
    resp = client.get("/do-login", headers={"CF-Connecting-IP": "127.0.0.1", "user-agent": "TestAgent"})
    assert resp.status_code == 200
    assert "set-cookie" in resp.headers or resp.cookies

    # Now call protected with cookie carried by client
    r2 = client.get("/protected")
    assert r2.status_code == 200
    assert r2.json()["user_id"] == "u-login"
