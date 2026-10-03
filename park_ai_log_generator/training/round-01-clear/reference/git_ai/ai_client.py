from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .errors import GitAIError


@dataclass(slots=True)
class AIConfig:
    api_url: str
    api_key: str
    model: str
    temperature: float
    max_tokens: int

    @classmethod
    def from_runtime(cls, model: str, temperature: float, max_tokens: int) -> "AIConfig":
        api_url = os.environ.get("AI_API_URL", "").strip()
        api_key = os.environ.get("AI_API_KEY", "").strip()
        if not api_url:
            raise GitAIError("AI_API_URL 환경변수가 필요합니다.")
        if not api_key:
            raise GitAIError("AI_API_KEY 환경변수가 필요합니다. 실제 Key를 코드/GitHub에 저장하지 마세요.")
        return cls(api_url, api_key, model, temperature, max_tokens)


class AIClient:
    """Small REST client for an OpenAI-compatible chat-completions style endpoint.

    The endpoint itself is supplied at runtime so the repository does not hard-code
    credentials or a provider account. The parser also accepts a top-level
    `output_text` string for simple compatible gateways.
    """

    def generate(self, config: AIConfig, prompt: str) -> str:
        payload = {
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "messages": [
                {"role": "user", "content": prompt},
            ],
        }
        request = urllib.request.Request(
            config.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer {}".format(config.api_key),
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise GitAIError("AI API HTTP 오류 {}: {}".format(exc.code, detail or exc.reason)) from exc
        except urllib.error.URLError as exc:
            raise GitAIError("AI API 네트워크 오류: {}".format(exc.reason)) from exc
        except TimeoutError as exc:
            raise GitAIError("AI API 요청 시간이 초과되었습니다.") from exc

        try:
            data: Any = json.loads(body)
        except json.JSONDecodeError as exc:
            raise GitAIError("AI API 응답이 JSON 형식이 아닙니다.") from exc

        output_text = data.get("output_text") if isinstance(data, dict) else None
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GitAIError("AI API 응답에서 생성 텍스트를 찾을 수 없습니다.") from exc

        if not isinstance(content, str) or not content.strip():
            raise GitAIError("AI API가 빈 텍스트를 반환했습니다.")
        return content.strip()
