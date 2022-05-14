from typing import Optional, List
from datetime import datetime
from core.validate import ObjId
from pydantic import BaseModel, EmailStr, Field

COL_USER = 'user'
COL_ROLE = 'role'


class Token(BaseModel):
    ''' 访问令牌的模型 '''
    access_token: str = Field(title='令牌',)
    token_type: str = Field(title='令牌类型',)
    username: str = Field(title='用户名',)
    role_title: str = Field(title='角色名称',)
    role_permissions: list = Field(title='权限列表',)
    expires_minutes: int = Field(title='令牌超时分钟数',)
    incomplete: Optional[bool] = Field(default=False, title='需要补全资料',)


class TokenData(BaseModel):
    ''' 访问令牌的数据解析模型 '''
    user_id: Optional[str] = Field(title='用户ID',)
    role_id: Optional[str] = Field(title='角色ID',)


class UserBase(BaseModel):
    ''' 用户的基础模型 '''
    username: Optional[str] = Field(title='用户名称',)
    full_name: Optional[str] = Field(title='用户完整姓名',)
    email: Optional[EmailStr] = Field(title='电子邮箱',)
    disabled: Optional[bool] = Field(default=False, title='是否禁用',)


class UserCreate(UserBase):
    ''' 用户的创建模型 '''
    username: str = Field(title='用户名称',)
    password: str = Field(title='认证密码',)
    role_id: Optional[str] = Field(default='', title='角色ID',)


class UserGlobal(UserCreate):
    ''' 用户的全局模型 '''
    id: ObjId = Field(alias='_id', title='用户ID',)


class UserUpdate(UserBase):
    ''' 用户的更新模型 '''
    role_id: Optional[str] = Field(title='角色ID',)


class UserRead(UserBase):
    ''' 用户的读取模型 '''
    id: ObjId = Field(alias='_id', title='用户ID',)
    role_id: Optional[str] = Field(title='角色ID',)
    source: str = Field(title='用户来源',)
    create_time: datetime
    update_time: datetime


class PermissionRead(BaseModel):
    ''' 权限的读取模型 '''
    name: str = Field(title='权限名称',)
    path: str = Field(title='接口路径',)
    tag: str = Field(title='接口标签',)
    summary: str = Field(title='接口描述',)


class RoleBase(BaseModel):
    ''' 角色数据的基础模型 '''
    title: str = Field(title='角色名称', regex='^\S{2,}$',)
    permissions: list = Field(title='权限列表',)


class RoleUpdate(RoleBase):
    ''' 角色的更新模型 '''
    title: Optional[str] = Field(title='角色名称', regex='^\S{2,}$',)
    permissions: Optional[list] = Field(title='权限列表',)


class RoleRead(RoleBase):
    ''' 角色的读取模型 '''
    id: ObjId = Field(alias='_id', title='角色ID',)
    create_time: Optional[datetime] = datetime.utcnow()
    update_time: Optional[datetime] = datetime.utcnow()


class SetupUpdate(BaseModel):
    ''' 设置的更新模型 '''
    synced_wids: List[str] = Field(title='已同步进程ID列表',)
    setups: dict = Field(title='设置内容',)


class SyncedWorkerRead(BaseModel):
    ''' 同步工作进程的读取模型 '''
    wid: str = Field(title='进程ID',)
