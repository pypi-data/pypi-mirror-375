"""Steer configuration schemas."""

from enum import Enum
from itertools import product
from typing import TypedDict

from openai.types.chat import ChatCompletionMessageParam
from pydantic.dataclasses import dataclass

ALLOWED_TRAITS: set[str] = {"impatience", "confusion", "skeptical"}


MIN_INTENSITY: float = 0.0
MAX_INTENSITY: float = 5.0


class Role(Enum):
    """Conversation role for a single turn."""

    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class SteerCombination:
    """Type definition for steer combinations.

    Each combination represents one concrete steer sample.
    """

    age: str
    gender: str
    occupation: str
    intent: str
    trait: str
    intensity: float


@dataclass
class SimulationResult:
    """Type definition for simulation results."""

    conv_prefix: list[ChatCompletionMessageParam]
    response: str
    steer: SteerCombination | None = None


@dataclass
class SteerConfig:
    """Configuration for steer generation.

    ``traits`` maps each trait name to a list of intensity levels (1-5).
    The generator emits one combination per intensity value for each trait.

    Valid trait names are constrained to: ["impatience", "confusion", "skeptical"].
    """

    ages: list[str]
    genders: list[str]
    occupations: list[str]
    intents: list[str]
    traits: dict[str, list[int]]

    def combinations(self) -> list[SteerCombination]:
        """Generate all steer combinations from this config.

        The number of combinations is the Cartesian product of ages, genders,
        occupations, intents, multiplied by the total number of intensity
        levels across all traits. Each emitted ``SteerCombination`` contains
        one trait and one intensity value.
        """
        combinations: list[SteerCombination] = []

        trait_names = set(self.traits.keys())
        invalid = sorted(trait_names - ALLOWED_TRAITS)
        if invalid:
            allowed = ", ".join(sorted(ALLOWED_TRAITS))
            bad = ", ".join(invalid)
            msg = f"Invalid trait(s): {bad}. Allowed: {allowed}."
            raise ValueError(msg)

        trait_levels: list[tuple[str, float]] = []
        for trait, levels in self.traits.items():
            for lvl in levels:
                try:
                    f = float(lvl)
                except (ValueError, TypeError):
                    f = None
                if f is not None and MIN_INTENSITY <= f <= MAX_INTENSITY:
                    trait_levels.append((trait, f))

        for age, gender, occupation, intent in product(
            self.ages, self.genders, self.occupations, self.intents
        ):
            for trait, level in trait_levels:
                combinations.append(
                    SteerCombination(
                        age=age,
                        gender=gender,
                        occupation=occupation,
                        intent=intent,
                        trait=trait,
                        intensity=level,
                    )
                )
        return combinations


class SteerConfigInput(TypedDict):
    """TypedDict describing the expected SteerConfig input shape."""

    ages: list[str]
    genders: list[str]
    occupations: list[str]
    intents: list[str]
    traits: dict[str, list[int]]
