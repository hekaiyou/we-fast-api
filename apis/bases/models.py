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
    expires_minutes: int
    incomplete: Optional[bool] = False


class TokenData(BaseModel):
    ''' 访问令牌的数据解析模型 '''
    user_id: Optional[str] = None
    role_id: Optional[str] = None


class UserBase(BaseModel):
    ''' 用户数据的基础模型 '''
    full_name: Optional[str] = Field(title='完整姓名',)
    disabled: Optional[bool] = Field(title='是否禁用',)


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
    name: str = Field(title='权限名称',)
    path: str = Field(title='接口路径',)
    tag: str = Field(title='接口标签',)
    summary: str = Field(title='接口描述',)


class RoleBase(BaseModel):
    ''' 角色数据的基础模型 '''
    title: str = Field(title='角色名称', regex='^\S{2,}$',)
    permissions: list = Field(title='权限列表',)


class RoleUpdate(RoleBase):
    ''' 角色数据的更新模型 '''
    title: Optional[str] = Field(title='角色名称', regex='^\S{2,}$',)
    permissions: Optional[list] = Field(title='权限列表',)


class RoleRead(RoleBase):
    ''' 角色的读取模型 '''
    id: ObjId = Field(alias='_id', title='角色ID',)
    create_time: Optional[datetime] = datetime.utcnow()
    update_time: Optional[datetime] = datetime.utcnow()
