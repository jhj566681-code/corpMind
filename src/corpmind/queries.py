"""开发者练习区。未实现时明确失败，不返回伪造的业务结果。"""

from corpmind.contracts import (
    CallerContext,
    Clock,
    LogisticsData,
    OrderData,
    ToolFailure,
    ToolSuccess,
)
from corpmind.ports import BusinessSource


def get_order(
    raw_args: object,
    *,
    context: CallerContext | None,
    source: BusinessSource,
    clock: Clock,
    request_id: str,
) -> ToolSuccess[OrderData] | ToolFailure:
    """练习1：先使客服A查询 ORDER-A-001 的成功用例通过。

    后续再增加参数、身份、工具权限、业务组与故障分支。
    业务组在可信记录中，不能采信 raw_args 提供的身份。
    返回契约和检查顺序见 docs/m1-001-learning.md。
    """
    raise NotImplementedError("请先完成练习1：get_order 的授权成功查询")


def get_logistics(
    raw_args: object,
    *,
    context: CallerContext | None,
    source: BusinessSource,
    clock: Clock,
    request_id: str,
) -> ToolSuccess[LogisticsData] | ToolFailure:
    """后续练习：直接调用也要校验授权；一次调用只作一次查询尝试。

    超时转为安全的 TIMEOUT 结果；最多一次重试留给后续调用方练习，
    不在此处隐藏重试或实现 Agent 核心循环。
    """
    raise NotImplementedError("订单练习通过后，再完成物流查询")
