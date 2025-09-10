"""Main Client class for Collinear SDK."""

import logging

from collinear.assess.local import LocalGuardConfig
from collinear.assess.local import LocalSafetyAssessor
from collinear.schemas.assessment import AssessmentResponse
from collinear.schemas.persona import PersonaConfig
from collinear.schemas.persona import PersonaConfigInput
from collinear.schemas.persona import SimulationResult
from collinear.simulate.runner import SimulationRunner


class Client:
    """Main client for Collinear simulation."""

    def __init__(
        self,
        assistant_model_url: str,
        assistant_model_api_key: str,
        assistant_model_name: str,
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit_retries: int = 6,
    ) -> None:
        """Initialize the Collinear client.

        Args:
            assistant_model_url: OpenAI-compatible endpoint URL for the assistant model
            assistant_model_api_key: API key for the assistant model
            assistant_model_name: Assistant model name to use (required)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            rate_limit_retries: Maximum retries for rate limit errors (with exponential backoff)

        """
        if not assistant_model_name:
            raise ValueError("model_name is required")
        self.assistant_model_url = assistant_model_url
        self.assistant_model_api_key = assistant_model_api_key
        self.assistant_model_name = assistant_model_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_retries = rate_limit_retries
        self.logger = logging.getLogger("collinear")
        self._simulation_runner: SimulationRunner | None = None

    @property
    def simulation_runner(self) -> SimulationRunner:
        """Lazy load simulation runner."""
        if self._simulation_runner is None:
            self._simulation_runner = SimulationRunner(
                assistant_model_url=self.assistant_model_url,
                assistant_model_api_key=self.assistant_model_api_key,
                assistant_model_name=self.assistant_model_name,
                timeout=self.timeout,
                max_retries=self.max_retries,
                rate_limit_retries=self.rate_limit_retries,
            )
        return self._simulation_runner

    def simulate(
        self,
        persona_config: PersonaConfigInput,
        k: int = 10,
        num_exchanges: int = 2,
        batch_delay: float = 0.1,
    ) -> list[SimulationResult]:
        """Run simulations with personas against the model.

        Args:
            persona_config: Configuration dict with personas, intents, traits.
                Expected keys:
                  - "ages": list[str]
                  - "genders": list[str]
                  - "occupations": list[str]
                  - "intents": list[str]
                  - "traits": dict[str, list[int]]  (trait -> intensities 1-5)
                    where trait is in {"patience", "confusion", "fluency"}
            k: Number of simulation samples to generate
            num_exchanges: Number of user-assistant exchanges (e.g., 2 = 2 user
                turns + 2 assistant turns)
            batch_delay: Delay between simulations to avoid rate limits
                (seconds)

        Returns:
            List of simulation results with conv_prefix and response

        Note:
            The SDK implements automatic retry with backoff logic to handle rate limits.
            If you're hitting rate limits frequently, increase the batch_delay parameter.

        """
        config = PersonaConfig(**persona_config)
        return self.simulation_runner.run(
            config=config,
            k=k,
            num_exchanges=num_exchanges,
            batch_delay=batch_delay,
        )

    def assess(
        self,
        dataset: list[SimulationResult],
        *,
        judge_model_url: str | None = None,
        judge_model_api_key: str | None = None,
        judge_model_name: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> AssessmentResponse:
        """Assess simulated data locally using a user-provided model.

        This bypasses the Collinear platform entirely. It prompts an OpenAI-compatible
        model with a safety rubric and returns a compact ``AssessmentResponse``.

        Args:
            dataset: List of simulation results to assess.
            judge_model_url: Optional override for the judge's endpoint URL.
            judge_model_api_key: Optional override for the judge's API key.
            judge_model_name: Optional override for the judge model name.
            temperature: Sampling temperature for the judge.
            max_tokens: Max tokens for the judge completion.

        Returns:
            AssessmentResponse with scores and rationales per conversation.

        """
        if not dataset:
            raise ValueError("Dataset cannot be empty")

        cfg = LocalGuardConfig(
            api_url=judge_model_url or self.assistant_model_url,
            api_key=judge_model_api_key or self.assistant_model_api_key,
            model=judge_model_name or self.assistant_model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout,
        )
        assessor = LocalSafetyAssessor(cfg)
        return assessor.score_dataset(dataset)
