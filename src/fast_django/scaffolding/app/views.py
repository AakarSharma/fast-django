from __future__ import annotations

from fast_django.routers import APIRouter

router = APIRouter()


@router.get("/")
def index() -> dict[str, str]:
    return {"hello": "app"}


