from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Customer(_message.Message):
    __slots__ = ("id", "shop_id", "member_id", "platform_id", "name", "cellphone", "email", "birthday", "created_date", "last_login_date", "last_order_date", "is_empty_basket", "sms", "news_mail", "gender", "updated_at", "is_non_member", "is_deleted", "customer_group_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    SHOP_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CELLPHONE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    CREATED_DATE_FIELD_NUMBER: _ClassVar[int]
    LAST_LOGIN_DATE_FIELD_NUMBER: _ClassVar[int]
    LAST_ORDER_DATE_FIELD_NUMBER: _ClassVar[int]
    IS_EMPTY_BASKET_FIELD_NUMBER: _ClassVar[int]
    SMS_FIELD_NUMBER: _ClassVar[int]
    NEWS_MAIL_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_NON_MEMBER_FIELD_NUMBER: _ClassVar[int]
    IS_DELETED_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    shop_id: str
    member_id: str
    platform_id: str
    name: str
    cellphone: str
    email: str
    birthday: str
    created_date: str
    last_login_date: str
    last_order_date: str
    is_empty_basket: str
    sms: str
    news_mail: str
    gender: str
    updated_at: str
    is_non_member: str
    is_deleted: str
    customer_group_id: str
    def __init__(self, id: _Optional[str] = ..., shop_id: _Optional[str] = ..., member_id: _Optional[str] = ..., platform_id: _Optional[str] = ..., name: _Optional[str] = ..., cellphone: _Optional[str] = ..., email: _Optional[str] = ..., birthday: _Optional[str] = ..., created_date: _Optional[str] = ..., last_login_date: _Optional[str] = ..., last_order_date: _Optional[str] = ..., is_empty_basket: _Optional[str] = ..., sms: _Optional[str] = ..., news_mail: _Optional[str] = ..., gender: _Optional[str] = ..., updated_at: _Optional[str] = ..., is_non_member: _Optional[str] = ..., is_deleted: _Optional[str] = ..., customer_group_id: _Optional[str] = ...) -> None: ...

class CustomerGroup(_message.Message):
    __slots__ = ("id", "shop_id", "group_no", "platform_id", "group_name", "updated_at", "is_deleted")
    ID_FIELD_NUMBER: _ClassVar[int]
    SHOP_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_NO_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_DELETED_FIELD_NUMBER: _ClassVar[int]
    id: str
    shop_id: str
    group_no: str
    platform_id: str
    group_name: str
    updated_at: str
    is_deleted: str
    def __init__(self, id: _Optional[str] = ..., shop_id: _Optional[str] = ..., group_no: _Optional[str] = ..., platform_id: _Optional[str] = ..., group_name: _Optional[str] = ..., updated_at: _Optional[str] = ..., is_deleted: _Optional[str] = ...) -> None: ...
