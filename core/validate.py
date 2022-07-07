from bson.objectid import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status


class ObjId(ObjectId):
    ''' 验证 ObjectId 并转 str (常用于models) '''

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        from bson.errors import InvalidId
        try:
            ObjectId.is_valid(v)
        except InvalidId as e:
            raise ValueError('无效的对象 ID')
        return str(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


class ObjIdParams(ObjectId):
    ''' 验证 str 并转 ObjectId (常用于api_x) '''

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('无效的字符串 ID')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


def str_to_oid(str_id):
    ''' str 转 ObjectId '''
    try:
        return ObjectId(str_id)
    except InvalidId as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='无效的字符串 ID',
        )
