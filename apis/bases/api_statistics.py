from datetime import date, timedelta
from core.database import get_collection, doc_create
from fastapi import APIRouter, HTTPException, status
from .models import COL_OPERATE_PATH, COL_OPERATE_PATH_DAY, NoPaginate

router = APIRouter(prefix='/statistics', )


def summary_day_statistics(one_day):
    """ 汇总日统计数据 """
    new_path_day = {
        'date': one_day,
        'byte_m': 0.0,
        'total': 0,
        'c_200': 0,
        'paths': [],
    }
    for result in get_collection(COL_OPERATE_PATH).find({'date': one_day}):
        t_byte_m, t_spend_s = 0.0, 0.0
        t_total, t_c_200 = 0, 0
        for hour, data in result['hours'].items():
            t_byte_m += data['byte_m']
            t_spend_s += data['spend_s']
            t_total += data['total']
            t_c_200 += data.get('c_200', 0)
        new_path_day['paths'].append({
            'path':
            result['path'],
            'total':
            t_total,
            'c_200':
            t_c_200,
            'byte_m':
            t_byte_m,
            'avera_byte_m':
            t_byte_m / t_total if t_byte_m != 0.0 else t_byte_m,
            'avera_spend_s':
            t_spend_s / t_total if t_spend_s != 0.0 else t_spend_s,
        })
        new_path_day['byte_m'] += t_byte_m
        new_path_day['total'] += t_total
        new_path_day['c_200'] += t_c_200
    return new_path_day


def summary_hour_statistics(one_day):
    """ 汇总小时统计数据 """
    hour_dict = {}
    for i in range(24):
        hour_dict[str(i).zfill(2)] = {}
    for result in get_collection(COL_OPERATE_PATH).find({'date': one_day}):
        for _hour, value in result['hours'].items():
            hour_dict[str(_hour).zfill(2)][result['path']] = value
    hour_item = []
    for hour, value in hour_dict.items():
        new_path_hour = {
            'date': hour,
            'byte_m': 0.0,
            'total': 0,
            'c_200': 0,
            'paths': [],
        }
        for path, data in value.items():
            byte_m = data['byte_m']
            spend_s = data['spend_s']
            c_200 += data.get('c_200', 0)
            new_path_hour['paths'].append({
                'path':
                path,
                'total':
                data['total'],
                'c_200':
                c_200,
                'byte_m':
                byte_m,
                'avera_byte_m':
                byte_m / data['total'] if byte_m != 0.0 else byte_m,
                'avera_spend_s':
                spend_s / data['total'] if spend_s != 0.0 else spend_s,
            })
            new_path_hour['byte_m'] += byte_m
            new_path_hour['total'] += data['total']
            new_path_hour['c_200'] += c_200
        hour_item.append(new_path_hour)
    return hour_item


@router.get(
    '/',
    response_model=NoPaginate,
    summary='读取访问统计 (全量)',
)
async def read_statistics_all(start_date: date, end_date: date):
    if start_date > end_date or end_date > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='开始与结束日期不在合理范围内',
        )
    if start_date == end_date:
        all_item = summary_hour_statistics(str(start_date))
        return NoPaginate(all_item=all_item, total=len(all_item))
    date_list = []
    while start_date <= end_date:
        date_list.append(str(start_date))
        start_date += timedelta(days=1)
    path_day_col = get_collection(COL_OPERATE_PATH_DAY)
    all_item = []
    for one_day in date_list:
        if one_day == str(date.today()):
            # 当前天查询逻辑
            stored_path_day = summary_day_statistics(one_day)
        else:
            # 历史天查询逻辑
            stored_path_day = path_day_col.find_one({'date': one_day})
            if not stored_path_day:
                # 创建历史天数据
                stored_path_day = summary_day_statistics(one_day)
                doc_create(path_day_col, stored_path_day)
        if '_id' in stored_path_day:
            del stored_path_day['_id']
        if 'create_time' in stored_path_day:
            del stored_path_day['create_time']
            del stored_path_day['update_time']
        all_item.append(stored_path_day)
    return NoPaginate(all_item=all_item, total=len(all_item))
