"""验证教学资料与故障机制，不验证业务授权或查询函数。"""

import pytest

from tests.fixtures.business import NOW, SIGNED_AT, FakeBusinessSource


def test_fixture_matches_documented_business_facts():
    source = FakeBusinessSource()
    signed = source.logistics["ORDER-A-001"].data
    assert signed.delivered_at == SIGNED_AT
    assert signed.signed_by == "驿站代收"
    delayed = source.logistics["ORDER-A-002"].data
    assert (NOW - delayed.estimated_delivery_at).total_seconds() == 73 * 3600
    assert source.logistics["ORDER-A-003"].data.estimated_delivery_at > NOW
    assert source.orders["ORDER-B-001"].team_id == "B"
    for order_id, order in source.orders.items():
        logistics = source.logistics[order_id]
        assert logistics.team_id == order.team_id
        assert logistics.data.logistics_id == order.data.logistics_id


def test_fake_faults_are_deterministic_and_fixture_instances_are_isolated():
    source = FakeBusinessSource(faults={"get_logistics": ["timeout", None]})
    with pytest.raises(TimeoutError):
        source.read_logistics("ORDER-A-001")
    assert source.read_logistics("ORDER-A-001") is not None
    assert source.calls["get_logistics"] == 2
    assert FakeBusinessSource().calls["get_logistics"] == 0
