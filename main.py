import json
import uvicorn
import apis.apis_urls as apis_urls
import view.view_urls as view_urls
from loguru import logger
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from core.dependencies import get_base_settings, aiwrap
from core.database import create_db_client, close_db_client
from core.dynamic import get_startup_task, get_apis_configs

settings = get_apis_configs('bases')
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url='/docs' if settings.app_docs else None,
    redoc_url='/redoc' if settings.app_redoc else None,
)
app.include_router(apis_urls.router)
app.include_router(view_urls.router)
app.mount('/static', StaticFiles(directory='view/static'), name='static')
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_base_settings().allow_origins,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/', include_in_schema=False)
async def redirect_view():
    return RedirectResponse('/view/bases/token/')


@app.on_event('startup')
async def startup_event():
    logger.info('服务进程启动')
    create_db_client(apis_urls)
    for task in get_startup_task():
        task()


@app.on_event('shutdown')
async def shutdown_event():
    logger.info('服务进程结束')
    close_db_client()


@app.middleware('http')
async def add_response_middleware(request: Request, call_next):
    # 请求开始前的处理
    response = await call_next(request)
    # 请求完成后的处理
    if response.status_code not in [200, 404, 403, 401]:
        # 提前解析响应
        resp_body = [section async for section in response.__dict__['body_iterator']]
        # 修复 FastAPI 响应
        response.__setattr__('body_iterator', aiwrap(resp_body))
        # 格式化响应正文以进行日志记录
        try:
            resp_body = json.loads(resp_body[0].decode())
        except:
            resp_body = str(resp_body)
        logger.error(
            f'{request["method"]} {request["path"]} 请求响应 {response.status_code} {resp_body}')
    return response

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.uvicorn_host, port=settings.uvicorn_port,
        workers=settings.uvicorn_workers, reload=settings.uvicorn_reload,
    )
