import base64
from typing import Any

from .schema import ProviderResult


def _usage_to_dict(usage: Any) -> dict[str, Any]:
    if usage is None:
        return {}
    if isinstance(usage, dict):
        return dict(usage)
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "__dict__"):
        return dict(vars(usage))
    return {}


class OpenAIProvider:
    def __init__(self, client: Any, model: str):
        self.client = client
        self.model = model

    def complete_images(self, prompt: str, images: list[bytes]) -> ProviderResult:
        content = [{"type": "input_text", "text": prompt}]
        for image in images:
            encoded = base64.b64encode(image).decode("ascii")
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{encoded}",
                }
            )
        response = self.client.responses.create(
            model=self.model,
            input=[{"role": "user", "content": content}],
        )
        return _openai_result(response)

    def complete_text(self, prompt: str) -> ProviderResult:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                }
            ],
        )
        return _openai_result(response)


class DeepSeekProvider:
    def __init__(self, client: Any, model: str):
        self.client = client
        self.model = model

    @classmethod
    def from_api_key(
        cls, api_key: str, model: str, client_factory: Any | None = None
    ) -> "DeepSeekProvider":
        if client_factory is None:
            from openai import OpenAI

            client_factory = OpenAI
        client = client_factory(api_key=api_key, base_url="https://api.deepseek.com")
        return cls(client, model=model)

    def complete_text(self, prompt: str) -> ProviderResult:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return ProviderResult(
            raw_text=response.choices[0].message.content,
            model=response.model,
            usage=_usage_to_dict(getattr(response, "usage", None)),
        )


def _openai_result(response: Any) -> ProviderResult:
    return ProviderResult(
        raw_text=response.output_text,
        model=response.model,
        usage=_usage_to_dict(getattr(response, "usage", None)),
        system_fingerprint=getattr(response, "system_fingerprint", None),
    )
