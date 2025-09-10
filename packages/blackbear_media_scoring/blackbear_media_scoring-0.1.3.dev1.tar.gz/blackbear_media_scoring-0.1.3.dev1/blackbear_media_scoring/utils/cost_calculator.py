"""
Cost calculation utilities for BlackBear Media Scoring using LiteLLM.
"""

import logging
import time
from typing import Optional

import requests

try:
    from litellm import cost_per_token
except ImportError:
    cost_per_token = None
    logging.warning("litellm not available for cost calculation")


def calculate_gemini_cost(input_tokens: Optional[int], output_tokens: Optional[int], model: str = "gemini-2.5-flash") -> Optional[float]:
    """
    Calculate the estimated cost for Gemini API calls using LiteLLM's cost_per_token function.
    
    Args:
        input_tokens: Number of input tokens used in the request
        output_tokens: Number of output tokens generated in the response
        model: The Gemini model identifier (default: "gemini-2.5-flash")
    
    Returns:
        Estimated cost in USD, or None if cost cannot be calculated
    
    Note:
        LiteLLM expects model names in a specific format. For Gemini models, it should be:
        - "gemini-2.5-flash" instead of "models/gemini-2.5-flash"
        - "gemini-pro" instead of "models/gemini-pro"
        etc.
    """
    if cost_per_token is None:
        logging.warning("LiteLLM not available, cannot calculate cost")
        return None
    
    # Validate token counts
    if input_tokens is None or output_tokens is None:
        logging.warning("Cannot calculate cost: missing token counts")
        return None
    
    if input_tokens < 0 or output_tokens < 0:
        logging.warning("Cannot calculate cost: invalid token counts")
        return None
    
    # Convert Google's model format to LiteLLM format
    # Remove "models/" prefix if present
    if model.startswith("models/"):
        model = model.replace("models/", "")
    
    # Map to LiteLLM's expected format
    model_mapping = {
        "gemini-2.5-flash": "gemini/gemini-2.5-flash",
        "gemini-2.5-pro": "gemini/gemini-2.5-pro",
        "gemini-pro": "gemini/gemini-pro",
        "gemini-pro-vision": "gemini/gemini-pro-vision",
    }
    
    litellm_model = model_mapping.get(model, f"gemini/{model}")
    
    try:
        # Calculate cost using LiteLLM
        cost = cost_per_token(
            model=litellm_model,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens
        )
        
        # Handle different return formats from LiteLLM
        if isinstance(cost, dict):
            # If it's a dictionary, extract the total cost
            total_cost = cost.get("total_cost", 0.0)
        elif isinstance(cost, (list, tuple)) and len(cost) >= 2:
            # If it's a tuple/list, it might contain (prompt_cost, completion_cost)
            # Sum them up to get total cost
            total_cost = float(cost[0]) + float(cost[1])
        elif cost is not None:
            # If it's a single numeric value
            total_cost = float(cost)
        else:
            total_cost = 0.0
            
        return total_cost
        
    except Exception as e:
        logging.warning(f"Failed to calculate cost using LiteLLM: {e}")
        return None


def get_openrouter_cost_estimation(generation_id: str, api_key: str, base_url: str = "https://openrouter.ai/api/v1") -> Optional[float]:
    """
    Get cost estimation for an OpenRouter generation ID with retry logic.
    
    Args:
        generation_id (str): The generation ID to fetch cost estimation for
        api_key (str): The OpenRouter API key
        base_url (str): The OpenRouter API base URL
        
    Returns:
        Optional[float]: The estimated cost, or None if failed
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    max_retries = 10
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            cost_response = requests.get(
                f"{base_url}/generation?id={generation_id}", headers=headers
            )
            # If we get a 404, retry
            if cost_response.status_code == 404:
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(retry_delay)
                    continue
            # Raise exception for other bad status codes
            cost_response.raise_for_status()
            cost_data = cost_response.json()
            return cost_data.get("data", {}).get("total_cost")
        except requests.exceptions.RequestException as e:
            # Log error but don't fail the request
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                time.sleep(retry_delay)
                continue
            print(f"Warning: Failed to fetch cost estimation after {max_retries} attempts: {e}")
            return None
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Failed to fetch cost estimation: {e}")
            return None
        
    return None