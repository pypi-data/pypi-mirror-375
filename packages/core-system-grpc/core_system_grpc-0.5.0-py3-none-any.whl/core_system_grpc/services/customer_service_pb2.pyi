from messages.customer import request_pb2 as _request_pb2
from messages.customer import response_pb2 as _response_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import service as _service
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class CustomerService(_service.service): ...

class CustomerService_Stub(CustomerService): ...
