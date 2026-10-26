"""骨架检查：通过不代表查询函数、权限控制或 Agent 已实现。"""

import pytest
from pydantic import ValidationError

from corpmind.contracts import EvidenceRef, OrderQuery, ToolError, ToolFailure, ToolSuccess
from tests.fixtures.business import CALLER_A, NOW, FakeBusinessSource


@pytest.mark.parametrize(
    "raw_args",
    [
        {},
        {"order_id": ""},
        {"order_id": "  "},
        {"order_id": 123},
        {"order_id": ["ORDER-A-001", "ORDER-A-002"]},
        {"order_id": "ORDER-A-001", "user_id": "support-b"},
        {"order_id": "ORDER-A-001", "team_id": "B"},
        {"order_id": "ORDER-A-001", "role": "admin"},
        {"order_id": "ORDER-A-001", "confirmed": True},
    ],
)
def test_query_rejects_invalid_or_identity_arguments(raw_args):
    with pytest.raises(ValidationError):
        OrderQuery.model_validate(raw_args)


def test_success_and_failure_have_disjoint_payloads():
    record = FakeBusinessSource().orders["ORDER-A-001"].data
    evidence = EvidenceRef(
        kind="order", record_id=record.order_id, record_version=1, observed_at=NOW
    )
    success = ToolSuccess(
        data=record, evidence_refs=(evidence,), observed_at=NOW, request_id="contract-1"
    )
    failure = ToolFailure(
        error=ToolError(code="RESOURCE_UNAVAILABLE", message="资源不可用", retryable=False),
        observed_at=NOW,
        request_id="contract-2",
    )
    assert "error" not in success.model_dump()
    assert "data" not in failure.model_dump()
    assert failure.evidence_refs == ()
    with pytest.raises(ValidationError):
        ToolFailure.model_validate({**failure.model_dump(), "evidence_refs": (evidence,)})
    with pytest.raises(ValidationError):
        ToolFailure.model_validate({**failure.model_dump(), "data": record})


def test_empty_success_evidence_and_naive_time_are_rejected():
    data = FakeBusinessSource().orders["ORDER-A-001"].data
    with pytest.raises(ValidationError):
        ToolSuccess(data=data, evidence_refs=(), observed_at=NOW, request_id="contract-3")
    with pytest.raises(ValidationError):
        ToolFailure(
            error=ToolError(code="TIMEOUT", message="查询超时", retryable=True),
            observed_at=NOW.replace(tzinfo=None),
            request_id="contract-4",
        )


def test_caller_identity_is_separate_from_model_arguments():
    assert set(OrderQuery.model_json_schema()["properties"]) == {"order_id"}
    assert CALLER_A.team_id == "A"
    assert OrderQuery(order_id=" ORDER-A-001 ").order_id == "ORDER-A-001"
