"""Tests for the high-level Client wrapper."""

from __future__ import annotations

import pytest

from collinear.client import Client
from collinear.simulate.runner import SimulationRunner


def test_client_requires_model_name() -> None:
    """Client raises when model_name is missing or falsy."""
    with pytest.raises(ValueError, match="model_name is required"):
        Client(
            assistant_model_url="https://example.test",
            assistant_model_api_key="k",
            assistant_model_name="",
            steer_api_key="demo-001",
        )


def test_simulation_runner_lazy_instantiation() -> None:
    """Accessing `simulation_runner` returns a SimulationRunner instance."""
    client = Client(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        steer_api_key="demo-001",
    )
    runner = client.simulation_runner
    assert isinstance(runner, SimulationRunner)
