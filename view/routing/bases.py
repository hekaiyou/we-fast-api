import os
from typing import Optional
from core.validate import ObjIdParams
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from core.dependencies import get_view_request
from fastapi import APIRouter, Cookie, Depends

router = APIRouter(
    prefix='/bases',
)
templates = Jinja2Templates(
    directory=f'{os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))}/view/templates')


@router.get('/token/', response_class=HTMLResponse, include_in_schema=False)
async def page_token(request: dict = Depends(get_view_request), token_s: Optional[str] = Cookie(None)):
    if token_s:
        return RedirectResponse('/view/bases/dashboard/')
    return templates.TemplateResponse('bases/token.html', {**request})


@router.get('/dashboard/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_dashboard(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/dashboard.html', {**request})


@router.get('/me/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_me(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/me.html', {**request})


@router.get('/role/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_role(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/role.html', {**request})


@router.get('/role/create/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_role_create(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/role-edit.html', {**request})


@router.get('/role/update/{role_id}/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_role_update(role_id: ObjIdParams, request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/role-edit.html', {'role_id': str(role_id), **request})


@router.get('/setup/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_setup(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/setup.html', {**request})


@router.get('/setup/update/{module_name}/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_setup_update(module_name: str, request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/setup-edit.html', {'module_name': module_name[9:], **request})


@router.get('/logs/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_logs(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/logs.html', {**request})


@router.get('/password/update/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_password_update(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/password-update.html', {**request})
