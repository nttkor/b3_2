"""Mini Git 예외 계층.

모든 사용자 대상 에러 메시지를 이 모듈 한 곳에서 관리한다.
CLI는 MiniGitError 하나만 잡으면 되므로 예외 처리가 단순해진다.
"""


class MiniGitError(Exception):
    """Mini Git의 모든 예외의 최상위 타입."""


class NotInitializedError(MiniGitError):
    def __init__(self) -> None:
        super().__init__("Repository is not initialized")


class InvalidArgsError(MiniGitError):
    def __init__(self, detail: str | None = None) -> None:
        message = "Invalid args" if detail is None else f"Invalid args: {detail}"
        super().__init__(message)


class UnknownBranchError(MiniGitError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown branch: {name}")


class UnknownCommitError(MiniGitError):
    def __init__(self, ref: str) -> None:
        super().__init__(f"Unknown commit: {ref}")


class AmbiguousCommitError(MiniGitError):
    def __init__(self, ref: str) -> None:
        super().__init__(f"Ambiguous commit: {ref}")


class DuplicateBranchError(MiniGitError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Branch already exists: {name}")


class CycleError(MiniGitError):
    def __init__(self) -> None:
        super().__init__("Commit graph contains a cycle")