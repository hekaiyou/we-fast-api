import os
from datetime import date
from typing import Optional
from core.dynamic import get_apis_configs
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from core.dependencies import get_view_request
from fastapi import APIRouter, Cookie, Depends
from apis.templating import templates
from apis.bases.validate import UserObjIdParams, RoleObjIdParams

router = APIRouter(prefix='/bases', )


@router.get('/token/', response_class=HTMLResponse, include_in_schema=False)
async def page_token(mode: str = '',
                     request: dict = Depends(get_view_request),
                     token_s: Optional[str] = Cookie(None)):
    configs = get_apis_configs('bases')
    if token_s:
        return RedirectResponse(configs.app_home_path)
    if mode:
        return templates.TemplateResponse(f'bases/{mode}.html', {**request})
    if configs.enable_ldap_ad:
        return templates.TemplateResponse('bases/token-ldap.html', {**request})
    else:
        return templates.TemplateResponse('bases/token.html', {**request})


@router.get('/token/forget/',
            response_class=HTMLResponse,
            include_in_schema=False)
async def page_token_forget(request: dict = Depends(get_view_request),
                            token_s: Optional[str] = Cookie(None)):
    if token_s:
        configs = get_apis_configs('bases')
        return RedirectResponse(configs.app_home_path)
    return templates.TemplateResponse('bases/password-forget.html',
                                      {**request})


@router.get('/token/register/',
            response_class=HTMLResponse,
            include_in_schema=False)
async def page_token_register(request: dict = Depends(get_view_request),
                              token_s: Optional[str] = Cookie(None)):
    if token_s:
        configs = get_apis_configs('bases')
        return RedirectResponse(configs.app_home_path)
    return templates.TemplateResponse('bases/user-register.html', {**request})


@router.get('/home/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_home(request: dict = Depends(get_view_request),
                          token_s: Optional[str] = Cookie(None)):
    configs = get_apis_configs('bases')
    if token_s:
        _app_home = configs.app_home_path
    else:
        _app_home = configs.app_home_path_anon
    if _app_home != '/view/bases/home/':
        return RedirectResponse(_app_home)
    else:
        return templates.TemplateResponse('bases/home.html', {**request})


@router.get('/statistics/',
            response_class=HTMLResponse,
            include_in_schema=False)
async def page_bases_statistics(start_date: date = None,
                                end_date: date = None,
                                request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/statistics.html', {
        'start_date': str(start_date),
        'end_date': str(end_date),
        **request
    })


@router.get('/statistics/path/',
            response_class=HTMLResponse,
            include_in_schema=False)
async def page_bases_statistics_path(
        pk: str,
        start_date: date,
        end_date: date,
        request: dict = Depends(get_view_request),
):
    return templates.TemplateResponse(
        'bases/statistics_path.html', {
            'pk': pk,
            'start_date': str(start_date),
            'end_date': str(end_date),
            **request
        })


@router.get('/me/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_me(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/me.html', {**request})


@router.get('/role/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_role(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/role.html', {**request})


@router.get('/role/create/',
            response_class=HTMLResponse,
            include_in_schema=False)
async def page_bases_role_create(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/role-edit.html', {**request})


@router.get('/role/update/{role_id}/',
            response_class=HTMLResponse,
            include_in_schema=False)
async def page_bases_role_update(role_id: RoleObjIdParams,
                                 request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/role-edit.html', {
        'role_id': str(role_id),
        **request
    })


@router.get('/setup/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_setup(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/setup.html', {**request})


@router.get('/setup/update/{module_name}/',
            response_class=HTMLResponse,
            include_in_schema=False)
async def page_bases_setup_update(module_name: str,
                                  request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/setup-edit.html', {
        'module_name': module_name[9:],
        **request
    })


@router.get('/logs/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_logs(request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/logs.html', {
        **request,
        'ppid': os.getppid(),
    })


@router.get('/password/update/',
            response_class=HTMLResponse,
            include_in_schema=False)
async def page_bases_password_update(
        request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/password-update.html',
                                      {**request})


@router.get('/user/', response_class=HTMLResponse, include_in_schema=False)
async def page_bases_user(username: str = '',
                          full_name: str = '',
                          source: str = '',
                          request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/user.html', {
        'username': username,
        'full_name': full_name,
        'source': source,
        **request
    })


@router.get('/user/create/',
            response_class=HTMLResponse,
            include_in_schema=False)
async def page_bases_user_create(username: str = '',
                                 full_name: str = '',
                                 source: str = '',
                                 request: dict = Depends(get_view_request)):
    return templates.TemplateResponse('bases/user-edit.html', {
        'username': username,
        'full_name': full_name,
        'source': source,
        **request
    })


@router.get('/user/update/{user_id}/',
            response_class=HTMLResponse,
            include_in_schema=False)
async def page_bases_user_update(user_id: UserObjIdParams,
                                 username: str = '',
                                 full_name: str = '',
                                 source: str = '',
                                 request: dict = Depends(get_view_request)):
    return templates.TemplateResponse(
        'bases/user-edit.html', {
            'user_id': str(user_id),
            'username': username,
            'full_name': full_name,
            'source': source,
            **request
        })
