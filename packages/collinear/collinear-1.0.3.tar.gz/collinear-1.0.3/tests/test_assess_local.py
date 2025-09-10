"""Tests for local assess flow (no platform calls)."""

from __future__ import annotations

import pytest
from _pytest.monkeypatch import MonkeyPatch

from collinear.assess.local import LocalSafetyAssessor
from collinear.client import Client
from collinear.schemas.assessment import Score
from collinear.schemas.persona import SimulationResult


def test_assess_local_returns_scores(monkeypatch: MonkeyPatch) -> None:
    """Client.assess uses LocalSafetyAssessor and returns expected shape."""

    # Avoid any network access by stubbing the scorer.
    def fake_score_one(
        _self: LocalSafetyAssessor,
        _conv_prefix: list[dict[str, object]],
        _response_text: str,
    ) -> Score:
        return Score(score=4.0, rationale="ok")

    monkeypatch.setattr(LocalSafetyAssessor, "score_one", fake_score_one)

    client = Client(
        assistant_model_url="https://example.test/v1",  # not used by stub
        assistant_model_api_key="key",
        assistant_model_name="gpt-test",
    )

    sims: list[SimulationResult] = [
        SimulationResult(conv_prefix=[{"role": "user", "content": "hi"}], response="a"),
        SimulationResult(conv_prefix=[{"role": "user", "content": "hi2"}], response="b"),
    ]

    res = client.assess(dataset=sims)

    expected_count = 2
    expected_score = 4.0

    assert res.message == "Conversation evaluated"
    assert len(res.evaluation_result) == expected_count
    # Each item is a dict[str, Score]
    for item in res.evaluation_result:
        assert len(item) == 1
        score = next(iter(item.values()))
        assert isinstance(score, Score)
        assert score.score == expected_score
        assert score.rationale == "ok"


def test_assess_local_raises_on_empty() -> None:
    """Empty datasets are rejected."""
    client = Client(
        assistant_model_url="https://example.test/v1",
        assistant_model_api_key="key",
        assistant_model_name="gpt-test",
    )
    with pytest.raises(ValueError, match="Dataset cannot be empty"):
        client.assess(dataset=[])
