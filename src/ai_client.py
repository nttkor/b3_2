import os
import sys

from openai import (
    OpenAI,
    AuthenticationError,
    APIConnectionError,
    RateLimitError,
    APIStatusError,
)

OPENROUTER_BASE = 'https://openrouter.ai/api/v1'


class AIClient:
    """AI API 호출 및 응답 처리를 전담하는 클라이언트.

    Args:
        model (str): 사용할 AI 모델 ID
        temperature (float): 생성 무작위도 (0.0~1.0)
        max_tokens (int): 생성 최대 토큰 수
    """
    def __init__(self, model: str, temperature: float, max_tokens: int):
        # AI_API_KEY를 최우선으로 확인하고, OPENROUTER_API_KEY / OPENAI_API_KEY 순으로 폴백
        api_key = (
            os.environ.get('AI_API_KEY')
            or os.environ.get('OPENROUTER_API_KEY')
            or os.environ.get('OPENAI_API_KEY')
        )
        if not api_key:
            print('[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.')
            print('## 예) export AI_API_KEY="YOUR_KEY"')
            sys.exit(1)

        explicit_url = os.environ.get('AI_API_BASE_URL') or os.environ.get('OPENAI_BASE_URL')
        if explicit_url:
            base_url = explicit_url
        elif api_key.startswith('sk-cody-'):
            base_url = 'https://copa.codyssey.kr/v1'
        elif api_key.startswith('sk-or-'):
            base_url = OPENROUTER_BASE
        else:
            base_url = OPENROUTER_BASE

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return resp.choices[0].message.content or ''
        except AuthenticationError:
            print('[ERROR] API 인증 실패: AI_API_KEY를 확인하세요.')
            sys.exit(1)
        except APIConnectionError as e:
            print(f'[ERROR] 네트워크 연결 오류: {e}')
            sys.exit(1)
        except RateLimitError:
            print('[ERROR] API 요청 한도 초과. 잠시 후 다시 시도하세요.')
            sys.exit(1)
        except APIStatusError as e:
            print(f'[ERROR] API 오류 ({e.status_code}): {e.message}')
            sys.exit(1)
        except Exception as e:
            print(f'[ERROR] API 호출 실패: {e}')
            sys.exit(1)
