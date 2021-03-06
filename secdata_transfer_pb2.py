# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: secdata_transfer.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='secdata_transfer.proto',
  package='secdata_transfer',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x16secdata_transfer.proto\x12\x10secdata_transfer\"\x8d\x01\n\x0cKlineRequest\x12\n\n\x02ts\x18\x01 \x01(\x05\x12\x0c\n\x04\x63ode\x18\x02 \x01(\t\x12\x0e\n\x06period\x18\x03 \x01(\t\x12\x0c\n\x04open\x18\x04 \x01(\x01\x12\x0c\n\x04high\x18\x05 \x01(\x01\x12\x0b\n\x03low\x18\x06 \x01(\x01\x12\r\n\x05\x63lose\x18\x07 \x01(\x01\x12\x0b\n\x03vol\x18\x08 \x01(\x03\x12\x0e\n\x06\x61mount\x18\t \x01(\x01\"-\n\nKlineReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x0f\n\x07message\x18\x02 \x01(\t2d\n\rSecdataHandle\x12S\n\x11TransferKlineData\x12\x1e.secdata_transfer.KlineRequest\x1a\x1c.secdata_transfer.KlineReply\"\x00\x62\x06proto3'
)




_KLINEREQUEST = _descriptor.Descriptor(
  name='KlineRequest',
  full_name='secdata_transfer.KlineRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='ts', full_name='secdata_transfer.KlineRequest.ts', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='code', full_name='secdata_transfer.KlineRequest.code', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='period', full_name='secdata_transfer.KlineRequest.period', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='open', full_name='secdata_transfer.KlineRequest.open', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='high', full_name='secdata_transfer.KlineRequest.high', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='low', full_name='secdata_transfer.KlineRequest.low', index=5,
      number=6, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='close', full_name='secdata_transfer.KlineRequest.close', index=6,
      number=7, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='vol', full_name='secdata_transfer.KlineRequest.vol', index=7,
      number=8, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='amount', full_name='secdata_transfer.KlineRequest.amount', index=8,
      number=9, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=45,
  serialized_end=186,
)


_KLINEREPLY = _descriptor.Descriptor(
  name='KlineReply',
  full_name='secdata_transfer.KlineReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='secdata_transfer.KlineReply.status', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='message', full_name='secdata_transfer.KlineReply.message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=188,
  serialized_end=233,
)

DESCRIPTOR.message_types_by_name['KlineRequest'] = _KLINEREQUEST
DESCRIPTOR.message_types_by_name['KlineReply'] = _KLINEREPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

KlineRequest = _reflection.GeneratedProtocolMessageType('KlineRequest', (_message.Message,), {
  'DESCRIPTOR' : _KLINEREQUEST,
  '__module__' : 'secdata_transfer_pb2'
  # @@protoc_insertion_point(class_scope:secdata_transfer.KlineRequest)
  })
_sym_db.RegisterMessage(KlineRequest)

KlineReply = _reflection.GeneratedProtocolMessageType('KlineReply', (_message.Message,), {
  'DESCRIPTOR' : _KLINEREPLY,
  '__module__' : 'secdata_transfer_pb2'
  # @@protoc_insertion_point(class_scope:secdata_transfer.KlineReply)
  })
_sym_db.RegisterMessage(KlineReply)



_SECDATAHANDLE = _descriptor.ServiceDescriptor(
  name='SecdataHandle',
  full_name='secdata_transfer.SecdataHandle',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=235,
  serialized_end=335,
  methods=[
  _descriptor.MethodDescriptor(
    name='TransferKlineData',
    full_name='secdata_transfer.SecdataHandle.TransferKlineData',
    index=0,
    containing_service=None,
    input_type=_KLINEREQUEST,
    output_type=_KLINEREPLY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_SECDATAHANDLE)

DESCRIPTOR.services_by_name['SecdataHandle'] = _SECDATAHANDLE

# @@protoc_insertion_point(module_scope)
