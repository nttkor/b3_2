"""AI API 통신 및 모델 추론 클라이언트 모듈 (src/ai_client.py).

이 모듈은 OpenAI 호환 표준 REST API 규격을 준수하는 다양한 AI 서비스(Codyssey Gateway,
OpenRouter, OpenAI 공식 API 등)와의 네트워크 통신 및 텍스트 생성을 전담합니다.

주요 특징:
    1. 지능형 환경변수 탐색 및 자동 엔드포인트 라우팅:
       - 동료평가 기준인 `AI_API_KEY`를 최우선으로 탐색하며, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`로 유연하게 폴백합니다.
       - API 키 접두어(`sk-cody-`, `sk-or-`) 또는 명시적 설정(`AI_API_BASE_URL`)에 따라 적절한 프록시 엔드포인트로 자동 라우팅합니다.
    2. 표준화된 예외 처리 및 클린 에러 핸들링:
       - 네트워크 장애, API Key 누락, 인증 실패, 요율 한도 초과 등 발생 가능한 오류를
         친절한 사용자 안내 메시지로 변환하고 `sys.exit(1)`로 일관되게 종료하여 최상의 CLI 경험을 제공합니다.
"""

import os
import sys

from openai import (
    OpenAI,
    AuthenticationError,
    APIConnectionError,
    RateLimitError,
    APIStatusError,
)

# OpenRouter 기본 API 엔드포인트
OPENROUTER_BASE = 'https://openrouter.ai/api/v1'


class AIClient:
    """AI API 호출 및 응답 처리를 전담하는 네트워크 클라이언트 클래스.

    OpenAI 파이썬 SDK를 내부적으로 래핑하여, API 인증키 탐색, 베이스 URL 라우팅,
    하이퍼파라미터 주입 및 예외 상황에 대한 안전한 터미널 안내 출력을 수행합니다.

    Attributes:
        client (OpenAI): 내부에서 사용되는 공식 OpenAI 클라이언트 인스턴스.
        model (str): 추론 요청 대상 AI 모델 식별자 (기본값: 'gpt-5.4-mini').
        temperature (float): 생성 무작위도 파라미터 (0.0: 결정론적 ~ 1.0: 창의적).
        max_tokens (int): 모델이 생성할 수 있는 최대 출력 토큰 수.
    """

    def __init__(self, model: str, temperature: float, max_tokens: int) -> None:
        """AIClient 인스턴스를 초기화하고 API 엔드포인트 및 인증키를 바인딩한다.

        환경변수에서 API 키를 우선순위에 따라 조회하고, 키의 패턴과 환경변수 설정에 맞춰
        최적의 게이트웨이 엔드포인트를 자동 결정한 뒤 OpenAI 클라이언트를 생성합니다.

        Args:
            model (str): 사용할 AI 모델 ID (예: 'gpt-5.4-mini', 'openai/gpt-4o-mini').
            temperature (float): 생성 텍스트의 무작위도 (0.0~1.0).
            max_tokens (int): 생성할 최대 토큰 수 한도.

        Raises:
            SystemExit: `AI_API_KEY` 등 유효한 API 인증키가 환경변수에서 전혀 발견되지 않을 경우,
                친절한 예시와 함께 프로세스를 즉시 종료(`sys.exit(1)`)합니다.
        """
        # 1. API 키 우선순위 탐색: AI_API_KEY(동료평가 표준) -> OPENROUTER_API_KEY -> OPENAI_API_KEY
        api_key = (
            os.environ.get('AI_API_KEY')
            or os.environ.get('OPENROUTER_API_KEY')
            or os.environ.get('OPENAI_API_KEY')
        )
        # 키가 설정되지 않은 경우 표준 규격 에러 메시지 출력 후 종료 (동료평가 항목 1-3 요구사항)
        if not api_key:
            print('[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.')
            print('## 예) export AI_API_KEY="YOUR_KEY"')
            sys.exit(1)

        # 2. 엔드포인트 베이스 URL 자동 라우팅
        explicit_url = os.environ.get('AI_API_BASE_URL') or os.environ.get('OPENAI_BASE_URL')
        if explicit_url:
            # 명시적으로 환경변수에 지정된 베이스 URL 최우선 적용
            base_url = explicit_url
        elif api_key.startswith('sk-cody-'):
            # Codyssey 사내 게이트웨이 키 패턴 감지 시 자동 라우팅
            base_url = 'https://copa.codyssey.kr/v1'
        elif api_key.startswith('sk-or-'):
            # OpenRouter 키 패턴 감지 시 OpenRouter 게이트웨이로 라우팅
            base_url = OPENROUTER_BASE
        else:
            # 그 외의 경우 OpenRouter 기본 엔드포인트 사용
            base_url = OPENROUTER_BASE

        # 3. 내부 OpenAI 클라이언트 인스턴스화 및 하이퍼파라미터 저장
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str) -> str:
        """주어진 프롬프트를 AI 게이트웨이에 전송하고 생성된 텍스트 응답을 반환한다.

        ChatCompletion API를 1회 호출하며, 지정된 하이퍼파라미터(`temperature`, `max_tokens`)를
        요청 페이로드에 포함합니다. 발생 가능한 네트워크 및 인증 오류를 가로채어
        사용자 친화적 에러 메시지를 출력하고 안전하게 종료합니다.

        Args:
            prompt (str): AI 모델에 전달할 지시사항 및 Git 컨텍스트 프롬프트 텍스트.

        Returns:
            str: AI 모델이 생성한 원본 응답 텍스트 (빈 응답일 경우 빈 문자열 '').

        Raises:
            SystemExit: 다음과 같은 API 실패 상황 발생 시 [ERROR] 로그를 출력하고 `sys.exit(1)`로 종료합니다:
                - AuthenticationError: API 키가 잘못되었거나 만료된 경우
                - APIConnectionError: 네트워크 단절 또는 엔드포인트 연결 실패
                - RateLimitError: API 크레딧 소진 또는 초당 요청 한도 초과
                - APIStatusError: 서버 내부 오류(5xx) 또는 잘못된 요청(4xx)
                - Exception: 기타 예기치 못한 런타임 오류
        """
        try:
            # ChatCompletion API 단일 턴 생성 요청
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            # 생성된 텍스트 추출 (None 안전 처리)
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
