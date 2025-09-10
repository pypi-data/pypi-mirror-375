import typing
from typing import Optional, cast

import requests
from requests import Session

if typing.TYPE_CHECKING:
    from yayarl import URL


class RequestsMixin:
    # should only be used in URL!!!
    _default_session: Session | None = None

    def _get_session(self, session: Optional[Session] | None) -> Session:
        return cast(Session, session or self._default_session or requests)

    def options(self, session: Optional[Session] = None, **kwargs):
        return self._get_session(session).options(str(self), **kwargs)

    def head(self, session: Optional[Session] = None, **kwargs):
        return self._get_session(session).head(str(self), **kwargs)

    def get(self, session: Optional[Session] = None, **kwargs):
        return self._get_session(session).get(str(self), **kwargs)

    def post(self, session: Optional[Session] = None, **kwargs):
        return self._get_session(session).post(str(self), **kwargs)

    def patch(self, session: Optional[Session] = None, **kwargs):
        return self._get_session(session).patch(str(self), **kwargs)

    def put(self, session: Optional[Session] = None, **kwargs):
        return self._get_session(session).put(str(self), **kwargs)

    def delete(self, session: Optional[Session] = None, **kwargs):
        return self._get_session(session).delete(str(self), **kwargs)

    def __and__(self, other: Optional[Session]) -> "URL":
        cls = cast(typing.Type["URL"], self.__class__)
        new = cls(str(self))  # create a copy
        new._default_session = other
        return new
