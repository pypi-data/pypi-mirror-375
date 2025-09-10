"""Persona configuration schemas."""

from enum import Enum
from itertools import product
from typing import TypedDict

from openai.types.chat import ChatCompletionMessageParam
from pydantic.dataclasses import dataclass

# Valid persona intensity bounds (inclusive)
MIN_INTENSITY: float = 1.0
MAX_INTENSITY: float = 5.0


class Role(Enum):
    """Conversation role for a single turn."""

    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class PersonaCombination:
    """Type definition for persona combinations.

    Each combination represents one concrete persona sample.
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


@dataclass
class PersonaConfig:
    """Configuration for persona generation.

    ``traits`` maps each trait name to a list of intensity levels (1-5).
    The generator emits one combination per intensity value for each trait.
    """

    ages: list[str]
    genders: list[str]
    occupations: list[str]
    intents: list[str]
    traits: dict[str, list[int]]

    def combinations(self) -> list[PersonaCombination]:
        """Generate all persona combinations from this config.

        The number of combinations is the Cartesian product of ages, genders,
        occupations, intents, multiplied by the total number of intensity
        levels across all traits. Each emitted ``PersonaCombination`` contains
        one trait and one intensity value.
        """
        combinations: list[PersonaCombination] = []

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
                    PersonaCombination(
                        age=age,
                        gender=gender,
                        occupation=occupation,
                        intent=intent,
                        trait=trait,
                        intensity=level,
                    )
                )
        return combinations


class PersonaConfigInput(TypedDict):
    """TypedDict describing the expected PersonaConfig input shape."""

    ages: list[str]
    genders: list[str]
    occupations: list[str]
    intents: list[str]
    traits: dict[str, list[int]]
