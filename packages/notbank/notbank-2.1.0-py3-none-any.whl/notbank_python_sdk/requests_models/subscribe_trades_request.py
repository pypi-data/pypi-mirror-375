from dataclasses import dataclass

from notbank_python_sdk.requests_models.with_oms_id import WithOMSId


@dataclass
class SubscribeTradesRequest(WithOMSId):
    instrument_id: int
    include_last_count: int
