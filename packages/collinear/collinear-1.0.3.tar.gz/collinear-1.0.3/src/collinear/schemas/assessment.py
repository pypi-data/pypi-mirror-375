"""Lean dataclasses for assessment responses."""

from dataclasses import field

from pydantic import AliasPath
from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class Score:
    """Per-conversation score info."""

    score: float | None = None
    rationale: str | None = None


@dataclass
class AssessmentResponse:
    """Top-level structure returned from the assessment run endpoint."""

    message: str | None = None
    evaluation_result: list[dict[str, Score]] = field(default_factory=list)


@dataclass
class EvaluationItem:
    """Subset of evaluation entries we actually use."""

    conversation_scores: dict[str, Score]


@dataclass
class AssessmentRunResponse:
    """API response model mapped to a flat shape for assess/run."""

    message: str | None = None
    evaluation_result: list[EvaluationItem] = Field(
        default_factory=list, validation_alias=AliasPath("data", "evaluation_result")
    )


@dataclass
class UploadDatasetData:
    """Data returned by the dataset upload endpoint."""

    dataset_id: str
    rows: int | None = None
    eligible_evaluation_types: dict[str, list[str]] | None = None


@dataclass
class UploadDatasetResponse:
    """Full response shape from the dataset upload endpoint."""

    data: UploadDatasetData
    message: str | None = None


@dataclass
class JudgeResponse:
    """Judge creation response with required id and optional message."""

    id: str
    message: str | None = None
