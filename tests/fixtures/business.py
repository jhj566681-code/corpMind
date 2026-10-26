"""fixture-v1：沿用测试计划的四个订单，补充合成版本与物流标识。"""

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from corpmind.contracts import (
    CallerContext,
    LogisticsData,
    LogisticsEvent,
    OrderData,
    ToolName,
)
from corpmind.ports import LogisticsRecord, OrderRecord

FIXTURE_VERSION = "m1-001-fixture-v1"
NOW = datetime.fromisoformat("2026-10-26T10:00:00+08:00")
UPDATED_AT = datetime.fromisoformat("2026-10-26T09:00:00+08:00")
SIGNED_AT = datetime.fromisoformat("2026-10-25T16:30:00+08:00")

CALLER_A = CallerContext(
    user_id="support-a", team_id="A", allowed_tools=frozenset({"get_order", "get_logistics"})
)
CALLER_A2 = CALLER_A.model_copy(update={"user_id": "support-a2"})
CALLER_B = CallerContext(
    user_id="support-b", team_id="B", allowed_tools=frozenset({"get_order", "get_logistics"})
)


def fixed_clock() -> datetime:
    return NOW


def order_records() -> dict[str, OrderRecord]:
    return {
        order_id: OrderRecord(
            team_id=team,
            data=OrderData(
                order_id=order_id,
                status="delivered" if order_id == "ORDER-A-001" else "in_transit",
                logistics_id=order_id.replace("ORDER", "LOG"),
                record_version=1,
                updated_at=UPDATED_AT,
            ),
        )
        for order_id, team in (
            ("ORDER-A-001", "A"),
            ("ORDER-A-002", "A"),
            ("ORDER-A-003", "A"),
            ("ORDER-B-001", "B"),
        )
    }


def logistics_records() -> dict[str, LogisticsRecord]:
    expected = {
        "ORDER-A-002": datetime.fromisoformat("2026-10-23T09:00:00+08:00"),
        "ORDER-A-003": datetime.fromisoformat("2026-10-27T18:00:00+08:00"),
    }
    return {
        order_id: LogisticsRecord(
            team_id=record.team_id,
            data=LogisticsData(
                order_id=order_id,
                logistics_id=record.data.logistics_id,
                status=record.data.status,
                events=(
                    LogisticsEvent(
                        occurred_at=SIGNED_AT if record.data.status == "delivered" else UPDATED_AT,
                        description="驿站代收" if record.data.status == "delivered" else "运输中",
                    ),
                ),
                estimated_delivery_at=expected.get(order_id),
                delivered_at=SIGNED_AT if record.data.status == "delivered" else None,
                signed_by="驿站代收" if record.data.status == "delivered" else None,
                record_version=1,
                updated_at=UPDATED_AT,
            ),
        )
        for order_id, record in order_records().items()
    }


Fault = Literal["timeout", "unavailable"]


@dataclass
class FakeBusinessSource:
    """纯内存原始数据源。调用计数和故障队列仅用于测试，不是业务写入。"""

    orders: dict[str, OrderRecord] = field(default_factory=order_records)
    logistics: dict[str, LogisticsRecord] = field(default_factory=logistics_records)
    calls: Counter[ToolName] = field(default_factory=Counter)
    faults: dict[ToolName, list[Fault | None]] = field(default_factory=dict)

    def _before_read(self, tool: ToolName) -> None:
        self.calls[tool] += 1
        queue = self.faults.get(tool, [])
        fault = queue.pop(0) if queue else None
        if fault == "timeout":
            raise TimeoutError("模拟超时：内部信息不得直接返回")
        if fault == "unavailable":
            raise ConnectionError("模拟不可用：内部信息不得直接返回")

    def read_order(self, order_id: str) -> OrderRecord | None:
        self._before_read("get_order")
        return self.orders.get(order_id)

    def read_logistics(self, order_id: str) -> LogisticsRecord | None:
        self._before_read("get_logistics")
        return self.logistics.get(order_id)
