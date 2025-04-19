from django.db.models import Q
from django.utils.translation import get_language

from warehouse.models import ItemType


def get_item_type_name():
    language = get_language()
    if language == 'zh-hant':
        item_type_column = "type_name"
    elif language == 'zh-hans':
        item_type_column = "type_name"
    elif language == 'vi':
        item_type_column = "type_vn_name"
    else:
        item_type_column = "type_code"
    return item_type_column


def get_type_code_by_desc(desc_value):
    try:
        obj = ItemType.objects.get(desc=desc_value)
    except ItemType.DoesNotExist:
        return None

    return obj.type_code


def get_item_type_object(type_name):
    item_type = ItemType.objects.get(
        Q(type_code=type_name) |
        Q(type_name=type_name) |
        Q(type_vn_name=type_name)
    )
    return item_type














