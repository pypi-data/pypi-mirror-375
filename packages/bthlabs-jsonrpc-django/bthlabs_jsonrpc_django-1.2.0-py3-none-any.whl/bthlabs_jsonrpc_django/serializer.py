# -*- coding: utf-8 -*-
# bthlabs-jsonrpc-django | (c) 2022-present Tomek Wójcik | MIT License
from __future__ import annotations

import typing

from bthlabs_jsonrpc_core import JSONRPCSerializer
from django.db.models import QuerySet


class DjangoJSONRPCSerializer(JSONRPCSerializer):
    """Django-specific serializer"""
    SEQUENCE_TYPES: typing.Any = (QuerySet, *JSONRPCSerializer.SEQUENCE_TYPES)
