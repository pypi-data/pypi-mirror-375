"""Clean example of using the local assess method (no platform)."""

import logging

from collinear.client import Client


def main() -> None:
    """Run a small assessment demo using the SDK.

    Configures logging, runs a short simulation, then submits the
    results for safety assessment and logs the key outputs.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("collinear")

    client = Client(
        assistant_model_url="https://api.openai.com/v1",
        assistant_model_api_key="<your-openai-key>",
        assistant_model_name="gpt-4o-mini",
    )

    simulations = client.simulate(
        persona_config={
            "ages": ["young adult"],
            "genders": ["male", "female"],
            "occupations": ["software engineer"],
            "intents": ["Cancel service", "Upgrade Service"],
            "traits": {"patience": [0, 2, 3]},
        },
        k=5,
        num_exchanges=2,
    )

    result = client.assess(dataset=simulations)

    logger.info("Assessment: %s", result.message or "<no message>")

    for scores_map in result.evaluation_result:
        for scores in scores_map.values():
            logger.info("  Score: %s", scores.score)
            logger.info("  Rationale: %s", scores.rationale)


if __name__ == "__main__":
    main()
