from . import view_token
from . import view_dashboard
from fastapi import APIRouter

router = APIRouter(
    prefix='/users',
)

router.include_router(view_token.router)
router.include_router(view_dashboard.router)
