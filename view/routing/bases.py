from typing import Optional
from core.validate import ObjIdParams
from fastapi.responses import HTMLResponse
from core.dependencies import get_base_settings
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from core.dependencies import get_view_request
from fastapi import APIRouter, Request, Cookie, Depends

router = APIRouter(
    prefix='/bases',
)
templates = Jinja2Templates(directory='view/templates')


@router.get('/token/', response_class=HTMLResponse, include_in_schema=False)
async def page_token(request: Request, token_s: Optional[str] = Cookie(None)):
    settings = get_base_settings()
    if token_s:
        return RedirectResponse('/view/bases/dashboard/')
    return templates.TemplateResponse('bases/token.html', {
        'request': request,
        'settings': settings,
    })


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
