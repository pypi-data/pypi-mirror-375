import pytest
import time
from authtuna.core.database import db_manager, User
from authtuna.manager.asynchronous import AuthTunaAsync
from sqlalchemy import select

@pytest.mark.asyncio
async def test_session_manager_create_and_terminate(setup_db):
    service = AuthTunaAsync(db_manager)
    user = await service.users.create(email="s1@example.com", username="sessuser", password="Secret123", ip_address="1.2.3.4")
    session = await service.sessions.create(user.id, ip_address="1.2.3.4", region="TestRegion", device="TestDevice")
    assert session.session_id and session.active
    # Terminate session
    result = await service.sessions.terminate(session.session_id, ip_address="1.2.3.4")
    assert result is True
    # Terminate non-existent session
    result2 = await service.sessions.terminate("notfound", ip_address="1.2.3.4")
    assert result2 is False

@pytest.mark.asyncio
async def test_token_manager_create_and_validate(setup_db):
    service = AuthTunaAsync(db_manager)
    user = await service.users.create(email="t1@example.com", username="tokenuser", password="Secret123", ip_address="1.2.3.4")
    token = await service.tokens.create(user.id, "test_purpose", expiry_seconds=60)
    assert token.id and token.purpose == "test_purpose"
    # Validate token
    async with db_manager.get_db() as db:
        validated_user = await service.tokens.validate(db, token.id, "test_purpose", ip_address="1.2.3.4")
        assert validated_user.id == user.id
    # Expired token
    token.etime = time.time() - 1
    async with db_manager.get_db() as db:
        try:
            await service.tokens.validate(db, token.id, "test_purpose", ip_address="1.2.3.4")
        except Exception as e:
            assert "expired" in str(e).lower()

