"""第一轮仅做授权成功查询；-m exercise 显式运行，不使用 xfail 隐藏失败。"""

import pytest

from corpmind.contracts import ToolSuccess
from corpmind.queries import get_order
from tests.fixtures.business import CALLER_A, NOW, FakeBusinessSource, fixed_clock


@pytest.mark.exercise
def test_get_order_authorized_success():
    source = FakeBusinessSource()
    result = get_order(
        {"order_id": "ORDER-A-001"},
        context=CALLER_A,
        source=source,
        clock=fixed_clock,
        request_id="exercise-order-1",
    )
    assert isinstance(result, ToolSuccess)
    assert result.data.order_id == "ORDER-A-001"
    assert result.data.status == "delivered"
    assert result.data.logistics_id == "LOG-A-001"
    assert result.data.record_version == 1
    assert result.observed_at == NOW
    assert result.request_id == "exercise-order-1"
    assert len(result.evidence_refs) == 1
    evidence = result.evidence_refs[0]
    assert evidence.kind == "order"
    assert evidence.record_id == result.data.order_id
    assert evidence.record_version == result.data.record_version
    assert evidence.observed_at == NOW
    assert "team_id" not in result.model_dump_json()
    assert source.calls["get_order"] == 1
    assert source.calls["get_logistics"] == 0
