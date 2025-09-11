"""Example usage of the Collinear SDK for simulation only.

Adds formatted conversation output similar to `example_parse_hotel.py`.
"""

import logging
import os

from dotenv import load_dotenv

from collinear.client import Client
from collinear.schemas.steer import SteerConfigInput


def _print_header(title: str) -> None:
    line = "=" * len(title)
    print(line)
    print(title)
    print(line)


def main() -> None:
    """Run a small simulation demo using the SDK.

    This function constructs a ``Client`` and runs a few
    short steer-based simulations, printing nothing but
    exercising the core flow for local smoke testing.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("collinear")

    # Load environment from .env, then read required values
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required. Add it to .env.")

    client = Client(
        assistant_model_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        assistant_model_api_key="",
        assistant_model_name=os.getenv("OPENAI_ASSISTANT_MODEL", "gpt-4o-mini"),
        steer_api_key=os.getenv("PERSONA_API_KEY", "demo-001"),
    )

    steer_config: SteerConfigInput = {
        "ages": ["young adult", "middle-aged", "senior"],
        "genders": ["man", "woman"],
        "occupations": [
            "teacher",
            "software engineer",
            "nurse",
            "retired",
            "small business owner",
        ],
        "intents": [
            "Resolve billing issue",
            "Cancel service",
            "Update plan",
            "Activate internet connectivity",
            "Device troubleshooting",
        ],
        "traits": {
            "confusion": [2],
        },
    }

    k = 1
    num_exchanges = 2
    batch_delay = 0.9

    logger.info(
        "Starting simulations: k=%d, exchanges=%d, delay=%.1fs",
        k,
        num_exchanges,
        batch_delay,
    )

    simulations = client.simulate(
        steer_config=steer_config,
        k=k,
        num_exchanges=num_exchanges,
        batch_delay=batch_delay,
    )

    logger.info("Received %d simulation results", len(simulations))

    # Pretty-print the simulated conversations and steer details.
    for i, sim in enumerate(simulations, start=1):
        title = f"Conversation {i}"
        _print_header(title)
        p = sim.steer
        if p is not None:
            print(
                "Steer:\n"
                f"age={p.age}\n"
                f"gender={p.gender}\n"
                f"occupation={p.occupation}\n"
                f"intent={p.intent}\n"
                f"trait={p.trait}\n"
                f"intensity={p.intensity}"
            )
        print("---")
        for msg in sim.conv_prefix:
            role = str(msg.get("role", ""))
            content = str(msg.get("content", ""))
            if content:
                print(f"{role}: {content}")
        print(f"assistant: {sim.response}")
        print()
    logger.info("All simulations complete")


if __name__ == "__main__":
    main()
