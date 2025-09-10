"""Main Client class for Collinear SDK."""

import json
import logging
from datetime import datetime
from datetime import timezone

import httpx
from pydantic import TypeAdapter

from collinear.schemas.assessment import AssessmentResponse
from collinear.schemas.assessment import AssessmentRunResponse
from collinear.schemas.assessment import JudgeResponse
from collinear.schemas.assessment import UploadDatasetResponse
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
        dashboard_api_key: str | None = None,
        dashboard_api_base: str | None = None,
    ) -> None:
        """Initialize the Collinear client.

        Args:
            assistant_model_url: OpenAI-compatible endpoint URL for the assistant model
            assistant_model_api_key: API key for the assistant model
            assistant_model_name: Assistant model name to use (required)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            rate_limit_retries: Maximum retries for rate limit errors (with exponential backoff)
            dashboard_api_key: API key for the Collinear Dashboard API (required for assess)
            dashboard_api_base: Base URL for the Dashboard API

        """
        if not assistant_model_name:
            raise ValueError("model_name is required")
        self.assistant_model_url = assistant_model_url
        self.assistant_model_api_key = assistant_model_api_key
        self.assistant_model_name = assistant_model_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_retries = rate_limit_retries
        self.dashboard_api_key = dashboard_api_key
        self.dashboard_api_base = dashboard_api_base or "https://api.collinear.ai"
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
        space_id: str,
        name: str | None = None,
        judge: str = "collinear-guard",
    ) -> AssessmentResponse:
        """Submit simulated data for safety assessment.

        Args:
            dataset: List of simulation results to assess
            space_id: Space ID for the assessment
            name: Name for the assessment (auto-generated if not provided)
            judge: Judge name (default: "collinear-guard")

        Returns:
            API response with evaluation results

        """
        if not dataset:
            raise ValueError("Dataset cannot be empty")
        if not self.dashboard_api_key:
            raise ValueError("dashboard_api_key required")
        generated_name: str = name or (
            f"assessment-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        )
        dataset_rows = [{"conv_prefix": s.conv_prefix, "response": s.response} for s in dataset]
        with httpx.Client(timeout=self.timeout) as client:
            headers = {"Authorization": f"Bearer {self.dashboard_api_key}"}
            file_payload = ("data.json", json.dumps(dataset_rows), "application/json")
            form_data: dict[str, str] = {
                "dataset_name": generated_name,
                "space_id": space_id,
                "evaluation_type": "safety",
                "skip_context_check": "true",
            }
            response = client.post(
                f"{self.dashboard_api_base}/api/v1/dataset/upload/platform",
                headers=headers,
                files={"file": file_payload},
                data=form_data,
            )
            response.raise_for_status()
            upload_env = TypeAdapter(UploadDatasetResponse).validate_json(response.text)
            dataset_id = upload_env.data.dataset_id
            judge_name = f"{judge}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            judge_payload: dict[str, str] = {
                "judge_name": judge_name,
                "model_name": "collinear_guard",
                "space_id": space_id,
            }
            response = client.post(
                f"{self.dashboard_api_base}/api/v1/judge/create/sdk",
                headers={**headers, "Content-Type": "application/json"},
                json=judge_payload,
            )
            response.raise_for_status()
            judge_resp = TypeAdapter(JudgeResponse).validate_json(response.text)
            judge_id = judge_resp.id
            assess_payload: dict[str, str | bool | list[str]] = {
                "dataset_id": dataset_id,
                "judge_ids": [judge_id],
                "space_id": space_id,
                "name": generated_name,
                "roll_data": True,
            }
            response = client.post(
                f"{self.dashboard_api_base}/api/v1/dataset/assess/run",
                headers={**headers, "Content-Type": "application/json"},
                json=assess_payload,
            )
            response.raise_for_status()
            run = TypeAdapter(AssessmentRunResponse).validate_json(response.text)
            evaluation_result = [ev.conversation_scores for ev in run.evaluation_result]
            return AssessmentResponse(message=run.message, evaluation_result=evaluation_result)
