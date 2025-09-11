"""Ensure SimulationRunner sends only the canonical Steer API header.

This test monkeypatches httpx.Client.post to capture the headers passed
to the Steer Steer endpoint and verifies that only the `API-Key`
header is included and populated with the provided steer key, and
that the legacy `X-API-Key` header is not sent.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict
from typing import cast

import httpx
from _pytest.monkeypatch import MonkeyPatch
from typing_extensions import Self

if TYPE_CHECKING:
    from types import TracebackType

from collinear.schemas.steer import SteerConfig
from collinear.simulate.runner import SimulationRunner


def test_steer_headers_use_api_key_only(monkeypatch: MonkeyPatch) -> None:
    """USER calls include only `API-Key` header (no `X-API-Key`)."""

    class Captured(TypedDict):
        url: str
        headers: dict[str, str]
        json: dict[str, object]

    captured: Captured = {"url": "", "headers": {}, "json": {}}

    class FakeClient:
        def __init__(self, timeout: float | None = None) -> None:
            self._timeout = timeout

        def __enter__(self) -> Self:
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            return None

        def post(
            self,
            url: str,
            *,
            headers: dict[str, str],
            json: dict[str, object],
        ) -> httpx.Response:
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            # Return a minimal 200 OK JSON response
            return httpx.Response(
                status_code=200,
                json=cast("dict[str, object]", {"response": "ok"}),
            )

    monkeypatch.setattr(httpx, "Client", cast("type[httpx.Client]", FakeClient))

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="k",
        assistant_model_name="gpt-test",
        steer_api_key="steer-secret",
    )

    cfg = SteerConfig(
        ages=["25"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"impatience": [1]},
    )

    # Run a minimal simulation; network is mocked.
    res = runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0)
    assert res  # sanity
    assert res[0].response

    # Verify headers: only API-Key present, and no X-API-Key.
    headers: dict[str, str] = captured["headers"]
    assert headers.get("API-Key") == "steer-secret"
    assert "X-API-Key" not in headers or headers.get("X-API-Key") is None
