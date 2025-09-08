# -*- coding: utf-8 -*-
# bthlabs-jsonrpc-django | (c) 2022-present Tomek Wójcik | MIT License
from .auth_checks import (  # noqa: F401
    has_perms,
    is_authenticated,
    is_staff,
)
from .codecs import DjangoJSONCodec  # noqa: F401
from .executor import DjangoExecutor  # noqa: F401
from .serializer import DjangoJSONRPCSerializer  # noqa: F401
from .views import JSONRPCView  # noqa: F401

__version__ = '1.2.0'
