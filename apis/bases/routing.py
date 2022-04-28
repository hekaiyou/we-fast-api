from . import api_user
from . import api_permission
from . import api_role
from . import api_setup
from fastapi import APIRouter

router = APIRouter(
    prefix='/bases',
    tags=['bases'],
)

router.include_router(api_user.router)
router.include_router(api_permission.router)
router.include_router(api_role.router)
router.include_router(api_setup.router)
