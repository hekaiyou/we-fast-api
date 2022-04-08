from . import view_token
from fastapi import APIRouter

router = APIRouter(
    prefix='/users',
)

router.include_router(view_token.router)
