from typing import List, Set

from pilot.processor.code_processor import CodeProcessor

# 置換対象の語句（大文字で判定）
REPLACE_KEYWORDS = {
    'CALL', 'EXEC', 'GO TO', 'INITIALIZE', 'PERFORM'
}

# 置換後のコメント文字列
TODO_COMMENT = "// TODO "


class ReplaceWithTodoProcessor(CodeProcessor):
    def __init__(self, keywords: Set[str] = None):
        self.keywords = keywords or REPLACE_KEYWORDS

    def process(self, lines: List[str]) -> List[str]:
        result = []

        for line in lines:
            stripped = line.strip()
            # 行の先頭スペースを保持
            indent = line[: len(line) - len(line.lstrip())]

            # 空行処理
            if not stripped:
                result.append(line)
                continue

            # 大文字で判定
            upper_line = stripped.upper()

            # PERFORM ... UNTIL は置換しない
            if upper_line.startswith("PERFORM") and "UNTIL" in upper_line:
                result.append(line)
                continue

            # 置換対象キーワードで始まるか判定
            if self._is_replacement_target(upper_line):
                todo_line = f"{TODO_COMMENT}{stripped}"
                # 保持元のインデント
                result.append(f"{indent}{todo_line}\n")
            else:
                result.append(line)

        return result

    def _is_replacement_target(self, line: str) -> bool:
        return any(
            line.startswith(kw) for kw in self.keywords
        )
