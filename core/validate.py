from typing import List, Any, Callable, Annotated
from pydantic_core import core_schema
from datetime import date, timedelta
from bson.objectid import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status, UploadFile
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue


class _ObjectIdPydanticAnnotation:

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:

        def validate_from_str(id_: str) -> ObjectId:
            return ObjectId(id_)

        from_str_schema = core_schema.chain_schema([
            core_schema.str_schema(),
            core_schema.no_info_plain_validator_function(validate_from_str),
        ])
        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema([
                # 执行下一步之前, 先检查是否实例
                core_schema.is_instance_schema(ObjectId),
                from_str_schema,
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, _core_schema: core_schema.CoreSchema,
            handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        # 使用与 `str` 相同的架构
        return handler(core_schema.str_schema())


ObjId = Annotated[ObjectId, _ObjectIdPydanticAnnotation]


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
    month_list = []
    while start_date <= end_date:
        if start_date.strftime('%Y-%m') not in month_list:
            month_list.append(start_date.strftime('%Y-%m'))
        start_date += timedelta(days=1)
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


def check_upload_files_type(files: List[UploadFile], type_check: list = None):
    """ 验证上传文件列表中每个文件的类型 """
    if type_check is None:
        type_check = []
    for file in files:
        if file.content_type.split('/')[0] not in type_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=
                f'文件 {file.filename}[{file.content_type.split("/")[0]}] 不是 {"|".join(type_check)} 类型',
            )
