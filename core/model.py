from pydantic import BaseModel
from typing import List, Dict


class Paginate(BaseModel):
    ''' 分页数据响应的模型 '''
    items: List[Dict]
    total: int


class NoPaginate(BaseModel):
    ''' 不分页数据响应的模型 '''
    all_item: List[Dict]
    total: int
