"""模型可见参数、可信模拟身份和工具结果；不包含查询实现。"""

from collections.abc import Callable
from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

ToolName = Literal["get_order", "get_logistics"]
Status = Literal["delivered", "in_transit"]
Clock = Callable[[], datetime]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class OrderQuery(Contract):
    """两个工具共用；身份和权限字段一律不接收。"""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, str_strip_whitespace=True)
    order_id: str = Field(min_length=1)


class CallerContext(Contract):
    """仅由测试夹具/未来可信入口注入，不能从模型参数构造。不是登录系统。"""

    user_id: str = Field(min_length=1)
    team_id: Literal["A", "B"]
    allowed_tools: frozenset[ToolName]


class OrderData(Contract):
    order_id: str
    status: Status
    logistics_id: str
    record_version: int = Field(ge=1)
    updated_at: AwareDatetime


class LogisticsEvent(Contract):
    occurred_at: AwareDatetime
    description: str


class LogisticsData(Contract):
    order_id: str
    logistics_id: str
    status: Status
    events: tuple[LogisticsEvent, ...]
    estimated_delivery_at: AwareDatetime | None
    delivered_at: AwareDatetime | None
    signed_by: str | None
    record_version: int = Field(ge=1)
    updated_at: AwareDatetime


class EvidenceRef(Contract):
    kind: Literal["order", "logistics"]
    record_id: str
    record_version: int = Field(ge=1)
    observed_at: AwareDatetime


class ToolError(Contract):
    code: Literal[
        "INVALID_ARGUMENT",
        "UNAUTHENTICATED",
        "TOOL_NOT_ALLOWED",
        "RESOURCE_UNAVAILABLE",
        "TIMEOUT",
        "SERVICE_UNAVAILABLE",
    ]
    message: str
    retryable: bool


class ToolSuccess[T](Contract):
    ok: Literal[True] = True
    data: T
    evidence_refs: tuple[EvidenceRef, ...] = Field(min_length=1)
    observed_at: AwareDatetime
    request_id: str = Field(min_length=1)


class ToolFailure(Contract):
    ok: Literal[False] = False
    error: ToolError
    evidence_refs: tuple[()] = ()
    observed_at: AwareDatetime
    request_id: str = Field(min_length=1)
