# -*- coding: utf-8 -*-
# bthlabs-jsonrpc-django | (c) 2022-present Tomek Wójcik | MIT License
from __future__ import annotations

import typing

from bthlabs_jsonrpc_core import Codec, Executor, JSONRPCAccessDeniedError
from django.http import HttpRequest

from bthlabs_jsonrpc_django.serializer import DjangoJSONRPCSerializer

TCanCall = typing.Callable[[HttpRequest, str, list, dict], bool]


class DjangoExecutor(Executor):
    """Django-specific executor"""

    serializer = DjangoJSONRPCSerializer

    def __init__(self,
                 request: HttpRequest,
                 can_call: TCanCall,
                 namespace: str | None = None,
                 codec: Codec | None = None):
        super().__init__(namespace=namespace, codec=codec)
        self.request = request
        self.can_call = can_call

    # pragma mark - Public interface

    def enrich_args(self, args: list) -> list:
        """
        Injects the current :py:class:`django.http.HttpRequest` as the first
        argument.
        """
        return [self.request, *super().enrich_args(args)]

    def before_call(self, method: str, args: list, kwargs: dict):
        """
        Executes *can_call* and raises :py:exc:`JSONRPCAccessDeniedError`
        accordingly.
        """
        can_call = self.can_call(self.request, method, args, kwargs)
        if can_call is False:
            raise JSONRPCAccessDeniedError(data='can_call')
