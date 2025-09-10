"""Unit tests for persona configuration helpers."""

from __future__ import annotations

from collinear.schemas.persona import PersonaConfig


def test_combinations_count_and_contents() -> None:
    """Generate all combinations and validate counts and fields."""
    config = PersonaConfig(
        ages=["25", "30"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"patient": [1], "curious": [1]},
    )

    combos = config.combinations()

    expected_count = 2 * 1 * 1 * 1 * (1 + 1)
    assert len(combos) == expected_count

    assert {c.age for c in combos} == {"25", "30"}
    assert {c.trait for c in combos} == {"patient", "curious"}
    assert {int(c.intensity) for c in combos} == {1}
