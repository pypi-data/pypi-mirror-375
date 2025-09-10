# Collinear Python SDK

Persona‑driven chat simulation for OpenAI‑compatible endpoints.

Requires Python 3.10+.

## Install (uv)

```bash
uv venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv add collinear
uv sync
```

## Quickstart

```python
import os
from collinear.client import Client

client = Client(
    assistant_model_url="https://api.openai.com/v1",
    assistant_model_api_key=os.environ["OPENAI_API_KEY"],
    assistant_model_name="gpt-4o-mini",
)

persona_config = {
    "ages": ["young adult"],
    "genders": ["woman"],
    "occupations": ["teacher"],
    "intents": ["Resolve billing issue"],
    "traits": {"patience": [0, 2, 4]},
}
results = client.simulate(persona_config, k=1, num_exchanges=2)
assessment = client.assess(results)

for row in assessment.evaluation_result:
    for score in row.values():
        print("score=", score.score, "rationale=", score.rationale)
```

