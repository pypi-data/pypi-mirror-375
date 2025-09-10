"""Example usage of the Collinear SDK for simulation only."""

import logging

from collinear.client import Client
from collinear.schemas.persona import PersonaConfigInput


def main() -> None:
    """Run a small simulation demo using the SDK.

    This function constructs a ``Client`` and runs a few
    short persona-based simulations, printing nothing but
    exercising the core flow for local smoke testing.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("collinear")

    client = Client(
        assistant_model_url="https://api.openai.com/v1",
        assistant_model_api_key="<openai-api-key>",
        assistant_model_name="gpt-4o-mini",
    )

    persona_config: PersonaConfigInput = {
        "ages": ["young adult", "middle-aged", "senior"],
        "genders": ["man", "woman"],
        "occupations": ["teacher", "software engineer", "nurse", "retired", "small business owner"],
        "intents": [
            "Resolve billing issue",
            "Cancel service",
            "Update plan",
            "Activate internet connectivity",
            "Device troubleshooting",
        ],
        "traits": {
            "impatient": [5],
            "friendly": [3],
            "confused": [2],
            "aggressive": [4],
            "frustrated": [3, 5],
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
        persona_config=persona_config,
        k=k,
        num_exchanges=num_exchanges,
        batch_delay=batch_delay,
    )

    logger.info("Received %d simulation results", len(simulations))

    for i, sim in enumerate(simulations, 1):
        logger.info("Simulation %d/%d", i, len(simulations))
        for msg in sim.conv_prefix:
            role = str(msg.get("role", "")).upper()
            content = str(msg.get("content", ""))
            logger.info("%s: %s", role, content)
        logger.info("ASSISTANT: %s", sim.response)
    logger.info("All simulations complete")


if __name__ == "__main__":
    main()
