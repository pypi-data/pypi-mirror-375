from dataclasses import asdict, dataclass, field
from typing import Dict, List, Literal, Text, Union

from ...._constants import PYTHON_VERSION
from ....utils.types import B24APIResult, JSONDict, JSONList
from ..bitrix_api_response_time import BitrixAPIResponseTime
from .bitrix_api_response import BitrixAPIResponse

_DATACLASS_KWARGS = {"repr": False, "eq": False, "frozen": True}

if PYTHON_VERSION >= (3, 10):
    _DATACLASS_KWARGS["slots"] = True


@dataclass(**_DATACLASS_KWARGS)
class B24APIBatchResult:
    """"""

    result: Union[Dict[Text, B24APIResult], List[B24APIResult]]
    result_error: Union[JSONDict, JSONList]
    result_total: Union[Dict[Text, int], List[int]]
    result_next: Union[Dict[Text, int], List[int]]
    result_time: Union[Dict[Text, BitrixAPIResponseTime], List[BitrixAPIResponseTime]]

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"result=<{type(self.result).__name__}: {len(self.result)}>, "
            f"result_error=<{type(self.result_error).__name__}: {len(self.result_error)}>, "
            f"result_total=<{type(self.result_total).__name__}: {len(self.result_total)}>, "
            f"result_next=<{type(self.result_next).__name__}: {len(self.result_next)}>, "
            f"result_time=<{type(self.result_time).__name__}: {len(self.result_time)}>)"
        )

    @classmethod
    def from_dict(cls, json_response: JSONDict) -> "B24APIBatchResult":
        json_result_time = json_response["result_time"]

        if isinstance(json_result_time, dict):
            result_time = dict()

            for key, time_value in json_result_time.items():
                result_time[key] = BitrixAPIResponseTime.from_dict(time_value)

        else:
            result_time = list()

            for time_value in json_result_time:
                result_time.append(BitrixAPIResponseTime.from_dict(time_value))

        return cls(
            result=json_response["result"],
            result_error=json_response["result_error"],
            result_total=json_response["result_total"],
            result_next=json_response["result_next"],
            result_time=result_time,
        )

    def to_dict(self) -> JSONDict:
        return asdict(self)


@dataclass(**_DATACLASS_KWARGS)
class BitrixAPIBatchResponse(BitrixAPIResponse):
    """"""

    result: B24APIBatchResult
    next: Literal[None] = field(init=False, default=None)
    total: Literal[None] = field(init=False, default=None)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"result={self.result}, "
            f"time={self.time})"
        )

    @classmethod
    def from_dict(cls, json_response: JSONDict) -> "BitrixAPIBatchResponse":
        return cls(
            result=B24APIBatchResult.from_dict(json_response["result"]),
            _time=BitrixAPIResponseTime.from_dict(json_response["time"]),
        )
