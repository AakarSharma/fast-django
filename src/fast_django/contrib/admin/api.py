from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from fast_django.contrib.auth.models import Group, Permission, User
from fast_django.contrib.auth.sessions import get_request_user

router = APIRouter(prefix="/auth", tags=["admin-auth"])


async def _require_admin(request: Request) -> User:
    user = get_request_user(request)
    if not isinstance(user, User) or not user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if not user.is_staff and not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required")
    return user


@router.get("/users")
async def list_users(request: Request) -> list[dict[str, object]]:
    await _require_admin(request)
    users = await User.all().order_by("id")
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }
        for user in users
    ]


@router.get("/groups")
async def list_groups(request: Request) -> list[dict[str, object]]:
    await _require_admin(request)
    groups = await Group.all().order_by("id")
    return [{"id": group.id, "name": group.name} for group in groups]


@router.get("/permissions")
async def list_permissions(request: Request) -> list[dict[str, object]]:
    await _require_admin(request)
    permissions = await Permission.all().prefetch_related("content_type")
    return [
        {
            "id": permission.id,
            "name": permission.name,
            "codename": permission.codename,
            "content_type": (
                f"{permission.content_type.app_label}.{permission.content_type.model}"
                if permission.content_type is not None
                else None
            ),
        }
        for permission in permissions
    ]


@router.post("/users/{user_id:int}/groups/{group_id:int}")
async def assign_user_group(user_id: int, group_id: int, request: Request) -> dict[str, str]:
    await _require_admin(request)
    user = await User.get_or_none(id=user_id)
    group = await Group.get_or_none(id=group_id)
    if user is None or group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or group not found")
    await user.groups.add(group)
    return {"status": "ok"}


@router.post("/users/{user_id:int}/permissions/{permission_id:int}")
async def assign_user_permission(user_id: int, permission_id: int, request: Request) -> dict[str, str]:
    await _require_admin(request)
    user = await User.get_or_none(id=user_id)
    permission = await Permission.get_or_none(id=permission_id)
    if user is None or permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or permission not found")
    await user.user_permissions.add(permission)
    return {"status": "ok"}


@router.post("/groups/{group_id:int}/permissions/{permission_id:int}")
async def assign_group_permission(group_id: int, permission_id: int, request: Request) -> dict[str, str]:
    await _require_admin(request)
    group = await Group.get_or_none(id=group_id)
    permission = await Permission.get_or_none(id=permission_id)
    if group is None or permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group or permission not found")
    await group.permissions.add(permission)
    return {"status": "ok"}
