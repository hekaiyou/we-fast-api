from typing import Optional
from datetime import datetime
from core.validate import ObjId
from pydantic import BaseModel, EmailStr, Field

COL_USER = 'user'
COL_ROLE = 'role'


class Token(BaseModel):
    ''' 访问令牌的模型 '''
    access_token: str
    token_type: str
    role_title: str
    role_permissions: list
    incomplete: Optional[bool] = False


class UserBase(BaseModel):
    ''' 用户数据的基础模型 '''
    full_name: Optional[str] = None
    disabled: Optional[bool] = False


class UserGlobal(UserBase):
    ''' 用户数据的全局模型 '''
    id: ObjId = Field(..., alias='_id')
    username: str
    email: Optional[EmailStr] = None
    password: str
    role_id: str


class UserCreate(UserBase):
    ''' 用户数据的创建模型 '''
    username: str
    email: Optional[EmailStr] = None
    password: str
    role_id: Optional[str] = ''


class UserUpdate(UserBase):
    ''' 用户数据的更新模型 '''
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[str] = None


class UserUpdateMe(UserBase):
    ''' 用户数据的更新模型 (我的) '''
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserRead(UserBase):
    ''' 用户数据的读取模型 '''
    id: ObjId = Field(..., alias='_id')
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[str] = None
    source: Optional[str] = None
    create_time: datetime
    update_time: datetime


class PermissionRead(BaseModel):
    ''' 权限数据的读取模型 '''
    name: str
    path: str
    tag: str
    summary: str


class RoleBase(BaseModel):
    ''' 角色数据的基础模型 '''
    title: str


class RoleCreate(RoleBase):
    ''' 角色数据的创建模型 '''
    permissions: list


class RoleUpdate(RoleBase):
    ''' 角色数据的更新模型 '''
    title: Optional[str] = None
    permissions: Optional[list] = None


class RoleRead(RoleBase):
    ''' 角色数据的读取模型 '''
    id: ObjId = Field(..., alias='_id')
    permissions: list
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
