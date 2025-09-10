import os
from typing import Optional

from .prompts import ExtractorPrompts
from .provider.gemini import Gemini
from .provider.openrouter import OpenRouter
from .provider.provider import SupportedProviders


class Extractor:
    def __init__(
        self, model: str, image_model: Optional[str], audio_model: Optional[str],
        video_model_param: Optional[str] = None, image_model_param: Optional[str] = None, audio_model_param: Optional[str] = None,
        prompt_file: Optional[str] = None
    ):
        self.prompt = ExtractorPrompts(prompt_file)

        # If image_model or audio_model are not specified, use the main model
        if image_model is None:
            image_model = model
        if audio_model is None:
            audio_model = model

        # Validate models
        try:
            selected_model = SupportedProviders(model)
            selected_image_model = SupportedProviders(image_model)
            selected_audio_model = SupportedProviders(audio_model)
        except ValueError:
            supported_providers = ", ".join([m.value for m in SupportedProviders])
            raise ValueError(
                f"Unsupported provider. Supported providers are: {supported_providers}"
            )

        provider_map = {
            SupportedProviders.GEMINI: Gemini,
            SupportedProviders.OPENROUTER: OpenRouter,
        }

        # Create providers for each model type
        self.provider = self._create_provider(provider_map, selected_model, video_model_param, "video")
        self.image_provider = self._create_provider(provider_map, selected_image_model, image_model_param, "image")
        self.audio_provider = self._create_provider(provider_map, selected_audio_model, audio_model_param, "audio")

    def _create_provider(self, provider_map, selected_model, model_param=None, media_type=None):
        """Create a provider instance for the given model."""
        provider_class = provider_map[selected_model]

        api_key = None
        if selected_model == SupportedProviders.GEMINI:
            api_key = os.environ.get("GEMINI_API_KEY")
        elif selected_model == SupportedProviders.OPENROUTER:
            api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                f"API key for provider '{selected_model.value}' not found in environment variables."
            )

        # Pass the model parameter to the provider
        if model_param:
            if media_type == "video":
                return provider_class(api_key, video_model=model_param)
            elif media_type == "image":
                return provider_class(api_key, image_model=model_param)
            elif media_type == "audio":
                return provider_class(api_key, audio_model=model_param)
        else:
            return provider_class(api_key)

    def describe_video(self, video_path: str):
        response = self.provider.describe_video(
            video_path, self.prompt.video_descriptor
        )

        return response

    def describe_images(self, image_paths: list[str]):
        response = self.image_provider.describe_images(
            image_paths, self.prompt.image_descriptor
        )

        return response

    def describe_image(self, image_path: str):
        response = self.image_provider.describe_image(
            image_path, self.prompt.image_descriptor
        )

        return response

    def describe_audio(self, audio_path: str):
        response = self.audio_provider.describe_audio(
            audio_path, self.prompt.audio_descriptor
        )

        return response

