from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from core.dependencies import get_view_request
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/dashboard',
)
templates = Jinja2Templates(directory='view/public/templates')


@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def page_dashboard(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('users/dashboard.html', {**request})


@router.get('/me/', response_class=HTMLResponse, include_in_schema=False)
async def page_dashboard_me(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('users/me.html', {'sub': True, **request})
