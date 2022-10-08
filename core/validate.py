from typing import List
from datetime import date, timedelta
from bson.objectid import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status, UploadFile


class ObjId(ObjectId):
    """ 验证 ObjectId 并转 str (常用于models) """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        from bson.errors import InvalidId
        try:
            ObjectId.is_valid(v)
        except InvalidId as e:
            raise ValueError('无效的对象ID')
        return str(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


class ObjIdParams(ObjectId):
    """ 验证 str 并转 ObjectId (常用于api_x) """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('无效的字符串ID')
        oid = ObjectId(v)
        if not cls.validate_doc(oid):
            raise ValueError('找不到匹配文档')
        return oid

    @classmethod
    def validate_doc(cls, oid) -> bool:
        return True

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


def get_date_list(start_date: date, end_date: date):
    """ 验证开始与结束日期并返回日期区间字符串列表 """
    if start_date > end_date or end_date > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='开始与结束日期不在合理范围内',
        )
    date_list = []
    while start_date <= end_date:
        date_list.append(str(start_date))
        start_date += timedelta(days=1)
    return date_list


def get_month_list(start_date: date, end_date: date):
    """ 验证开始与结束日期并返回月份区间字符串列表 """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='开始与结束日期不在合理范围内',
        )
    month_set = set()
    while start_date <= end_date:
        month_set.add(start_date.strftime('%Y-%m'))
        start_date += timedelta(days=1)
    month_list = list(month_set)
    month_list.sort()
    return month_list


def str_to_oid(str_id):
    """ str 转 ObjectId """
    try:
        return ObjectId(str_id)
    except InvalidId as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='无效的字符串ID',
        )


def check_upload_files_type(files: List[UploadFile], type_check: list = []):
    """ 验证上传文件列表中每个文件的类型 """
    for file in files:
        if file.content_type.split('/')[0] not in type_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=
                f'文件 {file.filename}[{file.content_type.split("/")[0]}] 不是 {"|".join(type_check)} 类型',
            )
