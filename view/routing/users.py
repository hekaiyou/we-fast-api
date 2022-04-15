from typing import Optional
from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.responses import HTMLResponse
from core.dependencies import get_settings
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from core.dependencies import get_view_request

router = APIRouter(
    prefix='/users',
)
templates = Jinja2Templates(directory='view/templates')


@router.get('/token/', response_class=HTMLResponse, include_in_schema=False)
async def page_token(request: Request, token_s: Optional[str] = Cookie(None)):
    settings = get_settings()
    if token_s:
        return RedirectResponse('/view/users/dashboard/')
    return templates.TemplateResponse('users/token.html', {
        'request': request,
        'settings': settings,
    })


@router.get('/dashboard/', response_class=HTMLResponse, include_in_schema=False)
async def page_dashboard(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('users/dashboard.html', {**request})


@router.get('/dashboard/me/', response_class=HTMLResponse, include_in_schema=False)
async def page_dashboard_me(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('users/me.html', {'sub': True, **request})
