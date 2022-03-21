from . import api_user
from . import api_permission
from . import api_role
from fastapi import APIRouter

router = APIRouter(
    prefix='/users',
    tags=['users'],
)

router.include_router(api_user.router)
router.include_router(api_permission.router)
router.include_router(api_role.router)
