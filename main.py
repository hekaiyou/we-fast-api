import apis.apis_urls as apis_urls
import view.view_urls as view_urls
import core.api_token as token_urls
from fastapi import FastAPI
from core.dependencies import get_settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from core.database import create_db_client, close_db_client

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)
app.include_router(token_urls.router)
app.include_router(apis_urls.router)
app.include_router(view_urls.router)
app.mount('/static', StaticFiles(directory='view/static'), name='static')
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/', include_in_schema=False)
async def redirect_view():
    return RedirectResponse('/view/users/token/')


@app.on_event('startup')
async def startup_event():
    create_db_client(apis_urls)


@app.on_event('shutdown')
async def shutdown_event():
    close_db_client()
