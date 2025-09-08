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
    id: int
    shop_id: int
    member_id: str
    platform_id: str
    name: str
    cellphone: str
    email: str
    birthday: str
    created_date: str
    last_login_date: str
    last_order_date: str
    is_empty_basket: bool
    sms: bool
    news_mail: bool
    gender: str
    updated_at: str
    is_non_member: bool
    is_deleted: bool
    customer_group_id: int
    def __init__(self, id: _Optional[int] = ..., shop_id: _Optional[int] = ..., member_id: _Optional[str] = ..., platform_id: _Optional[str] = ..., name: _Optional[str] = ..., cellphone: _Optional[str] = ..., email: _Optional[str] = ..., birthday: _Optional[str] = ..., created_date: _Optional[str] = ..., last_login_date: _Optional[str] = ..., last_order_date: _Optional[str] = ..., is_empty_basket: bool = ..., sms: bool = ..., news_mail: bool = ..., gender: _Optional[str] = ..., updated_at: _Optional[str] = ..., is_non_member: bool = ..., is_deleted: bool = ..., customer_group_id: _Optional[int] = ...) -> None: ...
