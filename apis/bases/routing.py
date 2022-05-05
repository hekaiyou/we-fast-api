from fastapi import APIRouter
from . import api_token, api_me, api_wechat, api_user, api_permission, api_role, api_setup

router = APIRouter(
    prefix='/bases',
    tags=['bases'],
)

router.include_router(api_token.router)
router.include_router(api_me.router)
router.include_router(api_wechat.router)
router.include_router(api_user.router)
router.include_router(api_permission.router)
router.include_router(api_role.router)
router.include_router(api_setup.router)
