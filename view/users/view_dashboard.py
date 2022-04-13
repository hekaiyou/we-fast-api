from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from core.dependencies import get_settings
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix='/dashboard',
)
templates = Jinja2Templates(directory='view/public/templates')


@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def read_token(request: Request):
    settings = get_settings()
    return templates.TemplateResponse('users/dashboard.html', {
        'request': request,
        'settings': settings,
    })
