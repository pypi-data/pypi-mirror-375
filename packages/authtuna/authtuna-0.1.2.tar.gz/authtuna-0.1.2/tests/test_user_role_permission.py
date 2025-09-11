import pytest
from authtuna.core.database import db_manager, User, Role, Permission
from authtuna.manager.asynchronous import AuthTunaAsync
from authtuna.core.encryption import encryption_utils
from sqlalchemy import select

@pytest.mark.asyncio
async def test_user_crud_and_password(setup_db):
    service = AuthTunaAsync(db_manager)
    # Create user
    user = await service.users.create(email="u1@example.com", username="user1", password="Secret123", ip_address="1.2.3.4")
    assert user.id and user.username == "user1"
    # Set and check password
    await service.users.set_password(user.id, "NewPass123", "1.2.3.4")
    async with db_manager.get_db() as db:
        user_db = await db.get(User, user.id)
        assert await user_db.check_password("NewPass123", "1.2.3.4", db_manager, db)
    # Update user
    updated = await service.users.update(user.id, {"username": "user1x"}, ip_address="1.2.3.4")
    assert updated.username == "user1x"
    # Delete user
    await service.users.delete(user.id, ip_address="1.2.3.4")
    async with db_manager.get_db() as db:
        assert await db.get(User, user.id) is None

@pytest.mark.asyncio
async def test_role_permission_management(setup_db):
    service = AuthTunaAsync(db_manager)
    # Create role and permission
    role, created = await service.roles.get_or_create("editor", {"description": "Can edit"})
    perm, created = await service.permissions.get_or_create("edit_content", {"description": "Edit content"})
    # Assign permission to role
    await service.roles.add_permission_to_role("editor", "edit_content")
    # Create user and assign role
    user = await service.users.create(email="u2@example.com", username="user2", password="Secret123", ip_address="1.2.3.4")
    await service.roles.assign_to_user(user.id, "editor", assigner_id=user.id, scope="global")
    # Check permission
    has_perm = await service.roles.has_permission(user.id, "edit_content")
    assert has_perm
    # List user roles with scope
    roles = await service.roles.get_user_roles_with_scope(user.id)
    assert any(r["role_name"] == "editor" for r in roles)
    # Clean up
    await service.users.delete(user.id)


