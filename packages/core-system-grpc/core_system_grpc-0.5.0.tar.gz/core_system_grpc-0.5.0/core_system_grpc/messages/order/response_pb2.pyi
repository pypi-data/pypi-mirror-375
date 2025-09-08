from messages.order import common_pb2 as _common_pb2
from messages.common import pagination_pb2 as _pagination_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetOrdersByShopResponse(_message.Message):
    __slots__ = ("orders", "pagination")
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[_common_pb2.Order]
    pagination: _pagination_pb2.PaginationResponse
    def __init__(self, orders: _Optional[_Iterable[_Union[_common_pb2.Order, _Mapping]]] = ..., pagination: _Optional[_Union[_pagination_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class GetOrderItemsByShopResponse(_message.Message):
    __slots__ = ("order_items", "pagination")
    ORDER_ITEMS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    order_items: _containers.RepeatedCompositeFieldContainer[_common_pb2.OrderItem]
    pagination: _pagination_pb2.PaginationResponse
    def __init__(self, order_items: _Optional[_Iterable[_Union[_common_pb2.OrderItem, _Mapping]]] = ..., pagination: _Optional[_Union[_pagination_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...
