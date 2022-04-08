from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/token',
)
templates = Jinja2Templates(directory='view/public/templates')


@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def read_token(request: Request):
    return templates.TemplateResponse('users/read_token.html', {'request': request})
