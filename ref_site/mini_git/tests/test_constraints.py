"""과제 제약 사항이 지켜지고 있는지 소스 코드를 정적 분석으로 검사한다.

정규식이 아니라 AST를 쓰는 이유:
    "sorted()를 쓰지 않는다"고 적은 docstring 자체가 정규식에 걸린다.
    실제 호출과 문자열 속 단어를 구분하려면 구문 트리를 봐야 한다.
"""

import ast
import importlib
import inspect
import pathlib
import unittest

PACKAGE = pathlib.Path(__file__).resolve().parent.parent / "minigit"

ALLOWED_STDLIB = {
    "hashlib", "shlex", "time", "collections", "datetime", "dataclasses", "typing",
}
FORBIDDEN_MODULES = {
    "heapq": "heapq 대신 MinHeap을 직접 구현해야 한다",
    "networkx": "그래프 전용 라이브러리 금지",
    "igraph": "그래프 전용 라이브러리 금지",
    "graphlib": "graphlib.TopologicalSorter 는 위상 정렬 전용 API",
    "functools": "cmp_to_key 우회 방지",
}


def source_files() -> list[pathlib.Path]:
    return sorted(PACKAGE.rglob("*.py"))


def parse(path: pathlib.Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def imported_modules(tree: ast.Module) -> set[str]:
    """이 모듈이 import 하는 최상위 모듈 이름들 (상대 import 제외)."""
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module.split(".")[0])
    return modules


class ForbiddenApiTests(unittest.TestCase):
    """정렬 관련 표준 API 전부 금지 / 그래프 전용 라이브러리 금지."""

    def test_no_sorted_builtin_call(self):
        for path in source_files():
            for node in ast.walk(parse(path)):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    with self.subTest(file=path.name, line=node.lineno):
                        self.assertNotEqual(
                            node.func.id, "sorted",
                            f"{path.name}:{node.lineno} sorted() 호출 금지",
                        )

    def test_no_list_sort_method_call(self):
        for path in source_files():
            for node in ast.walk(parse(path)):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    with self.subTest(file=path.name, line=node.lineno):
                        self.assertNotEqual(
                            node.func.attr, "sort",
                            f"{path.name}:{node.lineno} list.sort() 호출 금지",
                        )

    def test_no_forbidden_module_imports(self):
        for path in source_files():
            modules = imported_modules(parse(path))
            for name, reason in FORBIDDEN_MODULES.items():
                with self.subTest(file=path.name, module=name):
                    self.assertNotIn(modules, [name], reason)
                    self.assertNotIn(name, modules, f"{path.name}: {reason}")

    def test_only_standard_library_is_used(self):
        for path in source_files():
            for module in imported_modules(parse(path)):
                with self.subTest(file=path.name, module=module):
                    self.assertIn(
                        module, ALLOWED_STDLIB,
                        f"{path.name}: 허용되지 않은 모듈 {module}",
                    )


class LayeringTests(unittest.TestCase):
    """알고리즘 모듈은 도메인을 몰라야 한다 (구조/품질 요구)."""

    def test_sorting_module_has_no_internal_dependency(self):
        """정렬은 최하위 계층이라 프로젝트 내 어떤 모듈도 참조하지 않는다."""
        tree = parse(PACKAGE / "sorting.py")
        relative = [
            n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.level > 0
        ]
        self.assertEqual(relative, [])

    def test_graph_module_does_not_import_domain(self):
        """graph 는 errors/sorting 만 참조하고 models/repository 는 모른다."""
        tree = parse(PACKAGE / "graph.py")
        imported = {
            n.module for n in ast.walk(tree)
            if isinstance(n, ast.ImportFrom) and n.level > 0
        }
        self.assertEqual(imported, {"errors", "sorting"})

    def test_graph_module_never_references_commit_type(self):
        """docstring 설명이 아니라 실제 코드에 Commit 이 등장하지 않아야 한다."""
        tree = parse(PACKAGE / "graph.py")
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        attributes = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        for symbol in ("Commit", "Repository", "hash", "message", "author"):
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, names | attributes)

    def test_repository_does_not_import_cli_or_formatter(self):
        """도메인이 표현 계층을 참조하면 방향이 뒤집힌다."""
        tree = parse(PACKAGE / "repository.py")
        imported = {
            n.module for n in ast.walk(tree)
            if isinstance(n, ast.ImportFrom) and n.level > 0
        }
        self.assertNotIn("cli", imported)
        self.assertNotIn("formatter", imported)


class DocstringTests(unittest.TestCase):
    """주요 함수/클래스에 docstring 작성 (구조/품질 요구)."""

    def test_every_module_has_docstring(self):
        for path in source_files():
            if path.name == "__init__.py":
                continue
            with self.subTest(module=path.stem):
                self.assertIsNotNone(ast.get_docstring(parse(path)))

    def test_public_callables_have_docstrings(self):
        missing = []
        for path in source_files():
            if path.name == "__init__.py":
                continue
            module = importlib.import_module(f"minigit.{path.stem}")
            for name, obj in vars(module).items():
                if name.startswith("_"):
                    continue
                if getattr(obj, "__module__", None) != module.__name__:
                    continue
                if (inspect.isfunction(obj) or inspect.isclass(obj)) and not obj.__doc__:
                    missing.append(f"{path.stem}.{name}")
        self.assertEqual(missing, [], f"docstring 없는 공개 심볼: {missing}")

    def test_public_methods_have_docstrings(self):
        from minigit.repository import Repository
        from minigit.index import InvertedIndex
        from minigit.sorting import MinHeap

        missing = []
        for owner in (Repository, InvertedIndex, MinHeap):
            for name, member in vars(owner).items():
                if name.startswith("_") or not callable(member):
                    continue
                target = member.__func__ if isinstance(member, staticmethod) else member
                if not getattr(target, "__doc__", None):
                    missing.append(f"{owner.__name__}.{name}")
        self.assertEqual(missing, [], f"docstring 없는 공개 메서드: {missing}")


class ComplexityAnnotationTests(unittest.TestCase):
    """알고리즘 함수는 시간복잡도를 docstring에 명시한다.

    '설명할 수 있다'가 과제 목표이므로 근거를 코드 옆에 남긴다.
    """

    def test_graph_functions_document_complexity(self):
        from minigit import graph

        for name in ("topological_order", "ancestors", "bfs_distances", "smallest_shortest_path"):
            with self.subTest(function=name):
                self.assertIn("복잡도", getattr(graph, name).__doc__ or "")

    def test_sort_functions_document_complexity_and_stability(self):
        from minigit.sorting import insertion_sort, merge_sort

        for function in (merge_sort, insertion_sort):
            with self.subTest(function=function.__name__):
                doc = function.__doc__ or ""
                self.assertIn("복잡도", doc)
                self.assertIn("안정", doc)


if __name__ == "__main__":
    unittest.main()