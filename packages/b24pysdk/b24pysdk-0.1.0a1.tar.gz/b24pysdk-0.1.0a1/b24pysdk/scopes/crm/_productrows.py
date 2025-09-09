from typing import TYPE_CHECKING, Iterable, Union

from ...bitrix_api.classes import BitrixAPIRequest
from ...utils.functional import type_checker
from ...utils.types import JSONDict, Timeout
from .base_crm import BaseCRM

if TYPE_CHECKING:
    from . import Deal, Lead, Quote


class Productrows(BaseCRM):
    """"""

    def __init__(self, item: Union["Deal", "Lead", "Quote"]):
        super().__init__(item._scope)
        self._path = self._get_path(item)

    @type_checker
    def get(
            self,
            bitrix_id: int,
            *,
            timeout: Timeout = None,
    ) -> BitrixAPIRequest:
        """"""
        return self._get(bitrix_id, timeout=timeout)

    @type_checker
    def set(
            self,
            bitrix_id: int,
            rows: Iterable[JSONDict],
            *,
            timeout: Timeout = None,
    ) -> BitrixAPIRequest:
        """"""

        if rows.__class__ is not list:
            rows = list(rows)

        params = {
            "id": bitrix_id,
            "rows": rows,
        }

        return self._make_bitrix_api_request(
            api_method=self.set,
            params=params,
            timeout=timeout,
        )
