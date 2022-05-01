from core.database import get_collection
from core.dynamic import get_username_binding


def update_bind_username(stored_name, update_name):
    ''' 同步更新全部绑定用户名的集合及其字段内容 '''
    for binding_k, binding_v in get_username_binding().items():
        for field in binding_v:
            if ':array' in field:
                field = field.split(':')[0]
                change_item = get_collection(binding_k).find({
                    field: {'$elemMatch': {
                        '$in': [stored_name]
                    }}
                }, {field: 1, '_id': 1})
                for change in change_item:
                    revise = change[field]
                    for i, v in enumerate(revise):
                        if v == stored_name:
                            revise[i] = update_name
                            break
                    doc_update(
                        collection=get_collection(binding_k),
                        filter={'_id': change['_id']},
                        update={field: revise},
                    )
            else:
                doc_update(
                    collection=get_collection(binding_k),
                    filter={field: stored_name},
                    update={field: update_name},
                    many=True
                )
