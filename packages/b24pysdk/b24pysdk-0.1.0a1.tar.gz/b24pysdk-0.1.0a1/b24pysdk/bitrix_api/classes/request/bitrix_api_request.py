from typing import TYPE_CHECKING, Dict, Optional, Text, Tuple

from ....utils.types import B24APIResult, JSONDict, Timeout
from ...bitrix_token import AbstractBitrixToken
from ..bitrix_api_response_time import BitrixAPIResponseTime
from ..response import BitrixAPIResponse

if TYPE_CHECKING:
    from .bitrix_api_list_request import BitrixAPIFastListRequest, BitrixAPIListRequest


class BitrixAPIRequest:
    """"""

    __slots__ = ("_api_method", "_bitrix_token", "_kwargs", "_params", "_response", "_timeout")

    _bitrix_token: AbstractBitrixToken
    _api_method: Text
    _params: Optional[JSONDict]
    _timeout: Timeout
    _response: Optional[BitrixAPIResponse]
    _kwargs: Dict

    def __init__(
            self,
            *,
            bitrix_token: AbstractBitrixToken,
            api_method: Text,
            params: Optional[JSONDict] = None,
            timeout: Timeout = None,
            **kwargs: Dict,
    ):
        self._bitrix_token = bitrix_token
        self._api_method = api_method
        self._params = params
        self._timeout = timeout
        self._response = None
        self._kwargs = kwargs

    def __str__(self):
        return f"<{self.__class__.__name__} {self._api_method}({self._param_string})>"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"bitrix_token={self._bitrix_token}, "
            f"api_method='{self._api_method}', "
            f"params={self._params}, "
            f"timeout={self._timeout})"
        )

    @property
    def _as_tuple(self) -> Tuple[Text, Optional[JSONDict]]:
        """"""
        return self._api_method, self._params

    @property
    def bitrix_token(self) -> AbstractBitrixToken:
        """"""
        return self._bitrix_token

    @property
    def api_method(self) -> Text:
        """"""
        return self._api_method

    @property
    def params(self) -> Optional[JSONDict]:
        """"""
        return self._params

    @property
    def _param_string(self) -> Text:
        """"""
        if isinstance(self._params, dict):
            return ", ".join(f"{key}={value}" for key, value in self._params.items())
        else:
            return ""

    @property
    def timeout(self) -> Timeout:
        """"""
        return self._timeout

    @property
    def response(self) -> BitrixAPIResponse:
        """"""
        return self._response or self.call()

    @property
    def result(self) -> B24APIResult:
        """"""
        return self.response.result

    @property
    def time(self) -> BitrixAPIResponseTime:
        """"""
        return self.response.time

    def _call(self) -> JSONDict:
        """"""
        return self._bitrix_token.call_method(
            api_method=self._api_method,
            params=self._params,
            timeout=self._timeout,
            **self._kwargs,
        )

    def call(self) -> BitrixAPIResponse:
        """"""
        self._response = BitrixAPIResponse.from_dict(self._call())
        return self._response

    def as_list(
            self,
            limit: Optional[int] = None,
    ) -> "BitrixAPIListRequest":
        """"""
        from .bitrix_api_list_request import BitrixAPIListRequest
        return BitrixAPIListRequest(
            bitrix_api_request=self,
            limit=limit,
            **self._kwargs,
        )

    def as_list_fast(
            self,
            descending: bool = False,
            limit: Optional[int] = None,
    ) -> "BitrixAPIFastListRequest":
        """"""
        from .bitrix_api_list_request import BitrixAPIFastListRequest
        return BitrixAPIFastListRequest(
            bitrix_api_request=self,
            descending=descending,
            limit=limit,
            **self._kwargs,
        )
