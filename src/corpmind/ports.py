"""业务数据来源接口；这些原始记录只在可信程序内部使用。"""

from typing import Protocol

from corpmind.contracts import Contract, LogisticsData, OrderData


class OrderRecord(Contract):
    team_id: str
    data: OrderData


class LogisticsRecord(Contract):
    team_id: str
    data: LogisticsData


class BusinessSource(Protocol):
    """未来可换适配器；查到记录不等于有权向调用者返回。"""

    def read_order(self, order_id: str) -> OrderRecord | None: ...

    def read_logistics(self, order_id: str) -> LogisticsRecord | None: ...
