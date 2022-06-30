from datetime import date
from fastapi import APIRouter

router = APIRouter(
    prefix='/statistics',
)


@router.get(
    '/',
    summary='读取访问统计 (分页)',
)
async def read_statistics_page(start_date: date, end_date: date):
    return {}
