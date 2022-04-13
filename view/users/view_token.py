from typing import Optional
from fastapi import APIRouter, Request, Cookie
from fastapi.responses import HTMLResponse
from core.dependencies import get_settings
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix='/token',
)
templates = Jinja2Templates(directory='view/public/templates')


@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def page_token(request: Request, token_s: Optional[str] = Cookie(None)):
    settings = get_settings()
    if token_s:
        return RedirectResponse('/view/users/dashboard/')
    return templates.TemplateResponse('users/token.html', {
        'request': request,
        'settings': settings,
    })
