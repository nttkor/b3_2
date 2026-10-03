# B6-2 R01 Environment

## Golden Path

- Python 3.10+
- Git
- 실제 AI API는 Phase C에서 연결
- 외부 Python package 없이 표준 라이브러리 REST client 사용

## Reference 실행

Repository root에서:

```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 -m git_ai --help
```

실제 API Runtime:

```bash
export AI_API_URL="<provider-compatible-endpoint>"
export AI_API_KEY="<INPUT_ONLY_IN_LOCAL_SHELL>"
python3 -m git_ai commit --model "<runtime-model>" --temperature 0.2 --max-tokens 700
python3 -m git_ai pr --model "<runtime-model>" --temperature 0.2 --max-tokens 900
```

## Secret 원칙

실제 값은 다음에 저장하지 않습니다.

- GitHub tracked file
- `.env`
- README example
- screenshot/Evidence
- terminal copy/paste submitted to evaluator

Repository에는 placeholder만 사용합니다.

## Verify

```bash
bash training/round-01-clear/environment/verify.sh
```

verify는 API를 호출하지 않고 syntax/unit tests/Git diff collector/Secret pattern을 확인합니다. 실제 Provider API와 생성 품질은 Phase C Runtime에서 별도로 검증합니다.
