"""Tests for split user/assistant endpoints in SimulationRunner.

Verifies USER turns are generated via the Collinear Persona API,
while ASSISTANT turns still use the OpenAI-compatible assistant model.
Network calls are monkeypatched.
"""

from __future__ import annotations

from _pytest.monkeypatch import MonkeyPatch
from openai.types.chat import ChatCompletionMessageParam

from collinear.schemas.persona import PersonaConfig
from collinear.simulate.runner import SimulationRunner


def test_split_endpoints_persona_api_is_used(monkeypatch: MonkeyPatch) -> None:
    """USER turns route to Collinear Persona API; assistant via OpenAI path."""

    def fake_call_collinear_persona_api(
        _self: SimulationRunner,
        *,
        _conversation: list[ChatCompletionMessageParam],
        _system_prompt: str,
        trait: str,
        intensity: float,
    ) -> str:
        assert trait in {"patient", "curious"}
        assert isinstance(intensity, (float, int))

        return "u"

    def fake_call_with_retry(
        _self: SimulationRunner,
        _messages: list[ChatCompletionMessageParam],
        system_prompt: str,
    ) -> str:
        return "a" if "ASSISTANT" in system_prompt else "u"

    monkeypatch.setattr(
        SimulationRunner,
        "_call_collinear_persona_api",
        fake_call_collinear_persona_api,
    )
    monkeypatch.setattr(SimulationRunner, "_call_with_retry", fake_call_with_retry)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="k",
        assistant_model_name="gpt-test",
    )

    config = PersonaConfig(
        ages=["25"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"patient": [1], "curious": [3]},
    )

    results = runner.run(config=config, k=1, num_exchanges=2, batch_delay=0.0)

    assert len(results) == 1
    res = results[0]

    roles = [m["role"] for m in res.conv_prefix]
    contents = [m["content"] for m in res.conv_prefix]
    assert roles == ["user", "assistant", "user"]
    assert contents == ["u", "a", "u"]
    assert res.response == "a"
