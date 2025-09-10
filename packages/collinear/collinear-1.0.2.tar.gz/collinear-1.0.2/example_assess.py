"""Clean example of using the simplified assess method."""

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
        assistant_model_api_key="<openai-api-key>",
        assistant_model_name="gpt-4o-mini",
        dashboard_api_key="<collinear-dashboard-key>",
        dashboard_api_base="https://stage.collinear.ai",
    )

    simulations = client.simulate(
        persona_config={
            "ages": ["young adult"],
            "genders": ["male"],
            "occupations": ["software engineer"],
            "intents": ["Cancel service"],
            "traits": {"frustrated": [2, 4]},
        },
        k=2,
        num_exchanges=3,
    )

    result = client.assess(dataset=simulations, space_id="<your-space-id>")

    logger.info("Assessment: %s", result.message or "<no message>")

    for scores_map in result.evaluation_result:
        for scores in scores_map.values():
            logger.info("  Score: %s", scores.score)
            logger.info("  Rationale: %s", scores.rationale)


if __name__ == "__main__":
    main()
