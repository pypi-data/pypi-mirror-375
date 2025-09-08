# -*- coding: utf-8 -*-
# bthlabs-jsonrpc-django | (c) 2022-present Tomek Wójcik | MIT License
from __future__ import annotations

import typing

from bthlabs_jsonrpc_core import JSONCodec
from django.core.serializers.json import DjangoJSONEncoder


class DjangoJSONCodec(JSONCodec):
    """Django-specific JSON codec"""

    # pragma mark - Public interface

    def encode(self, payload: typing.Any, **encoder_kwargs) -> str:
        """
        Before handing off control to the superclass, this method will default
        the *cls* encoder kwarg to
        :py:class:`django.core.serializers.json.DjangoJSONEncoder`.
        """
        effective_encoder_kwargs = {
            'cls': DjangoJSONEncoder,
            **encoder_kwargs,
        }

        return super().encode(payload, **effective_encoder_kwargs)
