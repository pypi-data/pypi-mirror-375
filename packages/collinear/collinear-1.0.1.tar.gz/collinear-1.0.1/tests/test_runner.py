"""Tests exercising the conversation runner without network calls."""

from __future__ import annotations

from _pytest.monkeypatch import MonkeyPatch
from openai.types.chat import ChatCompletionMessageParam

from collinear.schemas.persona import PersonaCombination
from collinear.schemas.persona import PersonaConfig
from collinear.schemas.persona import Role
from collinear.simulate.runner import SimulationRunner


def test_run_builds_conversation_and_returns_results(monkeypatch: MonkeyPatch) -> None:
    """Monkeypatch turn generation to validate run() behavior without network."""

    def fake_generate(
        _self: SimulationRunner,
        _combo: PersonaCombination,
        _conversation: list[ChatCompletionMessageParam],
        role: Role,
    ) -> str:
        return "u" if role is Role.USER else "a"

    monkeypatch.setattr(SimulationRunner, "_generate_turn", fake_generate)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
    )

    config = PersonaConfig(
        ages=["25"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"patient": [1]},
    )

    results = runner.run(config=config, k=1, num_exchanges=2, batch_delay=0.0)
    assert len(results) == 1
    res = results[0]

    assert [m["role"] for m in res.conv_prefix] == ["user", "assistant", "user"]
    assert res.response == "a"
