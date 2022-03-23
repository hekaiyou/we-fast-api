from pydantic import BaseModel
from typing import Optional, List, Dict


class Token(BaseModel):
    ''' 访问令牌的模型 '''
    access_token: str
    token_type: str


class TokenData(BaseModel):
    ''' 访问令牌的数据解析模型 '''
    user_id: Optional[str] = None
    role_id: Optional[str] = None


class Paginate(BaseModel):
    ''' 分页数据响应的模型 '''
    items: List[Dict]
    total: int


class NoPaginate(BaseModel):
    ''' 不分页数据响应的模型 '''
    all_item: List[Dict]
    total: int
