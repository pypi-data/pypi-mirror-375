import json
import os
from typing import List, Optional

import requests
from pydantic import BaseModel, TypeAdapter

from ..prompts import AssessorPrompts
from .llm import LLM, ScoreResult, Category
from ...utils.cost_calculator import get_openrouter_cost_estimation


class OpenRouter(LLM):
    def __init__(self, model: str = None, prompt_file=None):
        """
        Initialize the OpenRouter client.

        Args:
            model (str, optional): The OpenRouter model to use for requests
            prompt_file (str, optional): Path to text file containing custom prompt template
        """
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        # Use provided model, environment variable, or default
        self.model = model or os.environ.get("OPENROUTER_ASSESSOR_MODEL") or "google/gemini-2.5-flash-lite"
        self.base_url = "https://openrouter.ai/api/v1"
        self.prompt = AssessorPrompts(prompt_file)

    def score(self, text: str) -> ScoreResult:
        """
        Score the text using OpenRouter.

        Args:
            text (str): The text to score

        Returns:
            ScoreResult: The scoring result with categories and scores
        """
        # Format the prompt with the text
        prompt = self.prompt.base_template.format(text=text)

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }

        # Make API request
        response = requests.post(
            f"{self.base_url}/chat/completions", headers=headers, json=data
        )

        # Raise exception for bad status codes
        response.raise_for_status()

        # Parse response
        response_data = response.json()
        # print(json.dumps(response_data, indent=2))
        response_text = response_data["choices"][0]["message"]["content"]

        # Extract generation ID for cost estimation
        generation_id = response_data.get("id")

        # Extract token counts if available
        input_tokens = None
        output_tokens = None
        if "usage" in response_data:
            usage = response_data["usage"]
            input_tokens = usage.get("prompt_tokens")
            output_tokens = usage.get("completion_tokens")

        # Get cost estimation if generation ID is available
        estimated_cost = None
        if generation_id:
            estimated_cost = get_openrouter_cost_estimation(generation_id, self.api_key, self.base_url)

        # Parse the JSON response into ScoreResult
        try:
            response_json = ScoreResult(data=[], status="success")
            response_json.data = TypeAdapter(List[Category]).validate_python(json.loads(response_text))
            response_json.input_tokens = input_tokens
            response_json.output_tokens = output_tokens
            response_json.estimated_cost = estimated_cost
            return response_json
        except Exception as e:
            raise TypeError(f"Failed to parse response into ScoreResult: {e}")


