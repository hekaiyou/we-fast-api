import os
import json
import uvicorn
import apis.apis_urls as apis_urls
import view.view_urls as view_urls
from time import time
from loguru import logger
from core.tasks import repeat_task
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, applications
from core.dependencies import get_base_settings, aiwrap
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from core.database import create_db_client, close_db_client, get_collection, doc_create
from core.dynamic import get_startup_task, get_apis_configs, set_request_record, get_request_record


def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args,
        **kwargs,
        swagger_js_url='/static/swagger-ui/4/swagger-ui-bundle.js',
        swagger_css_url='/static/swagger-ui/4/swagger-ui.css',
        swagger_favicon_url='/static/image/favicon.png',
    )


def redoc_monkey_patch(*args, **kwargs):
    return get_redoc_html(
        *args,
        **kwargs,
        redoc_js_url='/static/redoc/next/redoc.standalone.js',
        redoc_favicon_url='/static/image/favicon.png',
    )


applications.get_swagger_ui_html = swagger_monkey_patch
applications.get_redoc_html = redoc_monkey_patch
settings = get_apis_configs('bases')
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url='/docs' if settings.app_docs else None,
    redoc_url='/redoc' if settings.app_redoc else None,
)
app.include_router(apis_urls.router)
app.include_router(view_urls.router)
app.mount(
    '/static',
    StaticFiles(
        directory=f'{os.path.dirname(os.path.realpath(__file__))}/view/static'
    ),
    name='static')
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
    create_db_client(apis_urls)
    for task in get_startup_task():
        task()


@app.on_event('startup')
@repeat_task(seconds=60, wait_first=True)
def repeat_task_aggregate_request_records() -> None:
    operate_path_col = get_collection('operate_path')
    current_temp = []
    while True:
        record = get_request_record()
        if not record:
            break
        current_data = {'date': record['date'], 'path': record['path']}
        if f'{record["date"]}{record["path"]}' not in current_temp:
            if not operate_path_col.count_documents(current_data):
                doc_create(operate_path_col, {'hours': {}, **current_data})
            current_temp.append(f'{record["date"]}{record["path"]}')
        operate_path_col.update_one(
            current_data, {
                '$inc': {
                    f'hours.{record["hour"]}.total': 1,
                    f'hours.{record["hour"]}.spend_s': record['spend_sec'],
                    f'hours.{record["hour"]}.byte_m':
                    record['byte'] / 1024 / 1024,
                    f'hours.{record["hour"]}.c_{record["status"]}': 1,
                },
            })


@app.on_event('shutdown')
async def shutdown_event():
    close_db_client()


@app.middleware('http')
async def add_response_middleware(request: Request, call_next):
    start = time()  # 请求开始前获取开始时间
    response = await call_next(request)
    end = time()  # 请求完成后获取结束时间
    set_request_record(request, end - start, response)
    if response.status_code not in [200, 307, 304, 422, 405, 404, 403, 401]:
        # 提前解析响应
        resp_body = [
            section async for section in response.__dict__['body_iterator']
        ]
        # 修复 FastAPI 响应
        response.__setattr__('body_iterator', aiwrap(resp_body))
        # 格式化响应正文以进行日志记录
        try:
            resp_body = json.loads(resp_body[0].decode())
        except:
            resp_body = str(resp_body)
        log = f'{request["method"]} {request["path"]} 请求响应 {response.status_code} {resp_body}'
        if response.status_code >= 500:
            logger.error(log)
        else:
            logger.warning(log)
    return response


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
        workers=settings.uvicorn_workers,
        reload=settings.uvicorn_reload,
    )
