from typing import Iterable, Optional, Text

from ....bitrix_api.classes import BitrixAPIRequest
from ....utils.functional import type_checker
from ....utils.types import JSONDict, Timeout
from .._productrows import Productrows
from .._userfield import Userfield
from ..details import Details
from ..item.base_item import BaseItem
from ..relationships import Contact
from .recurring import Recurring


class Deal(BaseItem):
    """The methods provide capabilities for managing deals.
    They allow you to retrieve fields, add, update, delete, and get lists of deals.

    Documentation: https://apidocs.bitrix24.com/api-reference/crm/deals/index.html
    """

    ENTITY_TYPE_ID = 2
    ENTITY_TYPE_NAME = "DEAL"
    ENTITY_TYPE_ABBR = "D"
    USER_FIELD_ENTITY_ID = "CRM_DEAL"

    @property
    def contact(self) -> Contact:
        """"""
        return Contact(self)

    @property
    def details(self) -> Details:
        """"""
        return Details(self)

    @property
    def productrows(self) -> Productrows:
        """"""
        return Productrows(self)

    @property
    def recurring(self) -> Recurring:
        """"""
        return Recurring(self)

    @property
    def userfield(self) -> Userfield:
        """"""
        return Userfield(self)

    @type_checker
    def fields(
            self,
            *,
            timeout: Timeout = None,
    ) -> BitrixAPIRequest:
        """Get deal fields.

        Documentation: https://apidocs.bitrix24.com/api-reference/crm/deals/crm-deal-fields.html

        The method the description of deal fields, including custom ones.

        Args:
            timeout: Timeout in seconds.

        Returns:
            Instance of BitrixAPIRequest
        """
        return self._fields(timeout=timeout)

    @type_checker
    def add(
            self,
            fields: JSONDict,
            *,
            params: Optional[JSONDict] = None,
            timeout: Timeout = None,
    ) -> BitrixAPIRequest:
        """Create a new deal.

        The method crm.deal.add creates a new deal.

        Documentation: https://apidocs.bitrix24.com/api-reference/crm/deals/crm-deal-add.html

        Args:
            fields: Object format:

                {
                    field_1: value_1,

                    field_2: value_2,

                    ...,

                    field_n: value_n,
                };

            params: Object containing an additional set of parameters where

                - REGISTER_SONET_EVENT - whether to register the change event in the live feed 'Y' or not 'N';

            timeout: Timeout in seconds.

        Returns:
            Instance of BitrixAPIRequest
        """
        return self._add(
            fields,
            extra_params=params,
            timeout=timeout,
        )

    @type_checker
    def get(
            self,
            bitrix_id: int,
            *,
            timeout: Timeout = None,
    ) -> BitrixAPIRequest:
        """Get deal by ID.

        Documentation: https://apidocs.bitrix24.com/api-reference/crm/deals/crm-deal-get.html

        The method returns a deal by its identifier.

        Args:
            bitrix_id: Identifier of the deal;

            timeout: Timeout in seconds.

        Returns:
            Instance of BitrixAPIRequest
        """
        return self._get(bitrix_id, timeout=timeout)

    @type_checker
    def list(
            self,
            *,
            select: Optional[Iterable[Text]] = None,
            filter: Optional[JSONDict] = None,
            order: Optional[JSONDict] = None,
            start: Optional[int] = None,
            timeout: Timeout = None,
    ) -> BitrixAPIRequest:
        """Get a list of deals.

        Documentation: https://apidocs.bitrix24.com/api-reference/crm/deals/crm-deal-list.html

        The method returns a list of deals based on a filter.

        Args:
            select: List of fields that should be populated for deals in the selection;

            filter: Object format:

                {
                    field_1: value_1,

                    field_2: value_2,

                    ...,

                    field_n: value_n,
                };

            order: Object format:

                {
                    field_1: value_1,

                    ...,
                }

                where

                - field_n is the name of the field by which the selection will be sorted

                - value_n is a string value equals to 'ASC' (ascending sort) or 'DESC' (descending sort);

            start: This parameter is used to manage pagination;

            timeout: Timeout in seconds.

        Returns:
            Instance of BitrixAPIRequest
        """
        return self._list(
            select=select,
            filter=filter,
            order=order,
            start=start,
            timeout=timeout,
        )

    @type_checker
    def update(
            self,
            bitrix_id: int,
            fields: JSONDict,
            *,
            params: Optional[JSONDict] = None,
            timeout: Timeout = None,
    ) -> BitrixAPIRequest:
        """Update deal.

        Documentation: https://apidocs.bitrix24.com/api-reference/crm/deals/crm-deal-update.html

        The method updates an existing deal.

        Args:
            bitrix_id: Identifier of the deal;

            fields: Object format:

                {
                    field_1: value_1,

                    field_2: value_2,

                    ...,

                    field_n: value_n,
                };

            params: Set of additional parameters where

                - REGISTER_SONET_EVENT - whether to register the change event in the activity stream 'Y' or not 'N',

                - REGISTER_HISTORY_EVENT - whether to create a record in history 'Y' or not 'N';

            timeout: Timeout in seconds.

        Returns:
            Instance of BitrixAPIRequest
        """
        return self._update(
            bitrix_id,
            fields,
            extra_params=params,
            timeout=timeout,
        )

    @type_checker
    def delete(
            self,
            bitrix_id: int,
            *,
            timeout: Timeout = None,
    ) -> BitrixAPIRequest:
        """Delete deal.

        Documentation: https://apidocs.bitrix24.com/api-reference/crm/deals/crm-deal-delete.html

        The method removes a deal and all associated objects.

        Deleting a deal will result in the removal of all related objects, such as CRM activities, history, Timeline activities, and others.

        Objects are deleted if they are not linked to other entities or elements. If the objects are linked to other entities, only the link to the deleted deal will be removed.

        Args:
            bitrix_id: Identifier of the deal;

            timeout: Timeout in seconds.

        Returns:
            Instance of BitrixAPIRequest
        """
        return self._delete(bitrix_id, timeout=timeout)
