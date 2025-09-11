import pytest
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient

from authtuna.core.database import db_manager, User, Role
from authtuna.integrations.fastapi_integration import get_current_user, RoleChecker


@pytest.mark.asyncio
async def test_get_current_user_dependency_requires_user(setup_db):
    app = FastAPI()

    @app.get("/me")
    async def me(user = Depends(get_current_user)):
        return {"id": user.id}

    client = TestClient(app)
    # Without middleware setting user_id or cookie, should return 401
    r = client.get("/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_role_checker_uses_user_roles(setup_db):
    # create a user and role, and assign role using the manager (to set given_by_id)
    async with db_manager.get_db() as db:
        u = User(id="r1", username="RoleUser", email="role@example.com")
        db.add(u)
        await db.commit()
        r_admin = Role(name="admin")
        db.add(r_admin)
        await db.commit()
    # Assign role using the manager to set given_by_id
    from authtuna.manager.asynchronous import AuthTunaAsync
    service = AuthTunaAsync(db_manager)
    await service.roles.assign_to_user("r1", "admin", assigner_id="r1", scope="global")

    app = FastAPI()

    # Simulate middleware by injecting user object into request.state via dependency override
    async def fake_get_current_user(request: Request):
        from authtuna.integrations.fastapi_integration import auth_service
        user = await auth_service.users.get_by_id("r1", with_relations=True)
        request.state.user_object = user
        return user

    @app.get("/admin")
    async def admin(user = Depends(fake_get_current_user), _ = Depends(RoleChecker("admin"))):
        return {"ok": True}

    client = TestClient(app)
    r = client.get("/admin")
    assert r.status_code == 200
