from messages.customer import common_pb2 as _common_pb2
from messages.common import pagination_pb2 as _pagination_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCustomersByShopResponse(_message.Message):
    __slots__ = ("customers", "pagination")
    CUSTOMERS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    customers: _containers.RepeatedCompositeFieldContainer[_common_pb2.Customer]
    pagination: _pagination_pb2.PaginationResponse
    def __init__(self, customers: _Optional[_Iterable[_Union[_common_pb2.Customer, _Mapping]]] = ..., pagination: _Optional[_Union[_pagination_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...
