from typing import List

from pilot.processor.code_processor import CodeProcessor

# 先頭置換対象の文字数
LEADING_CHARS_COUNT = 6

# 置換後の文字（空白）
REPLACEMENT_CHAR = " "


class TrimLeadingCharsToSpacesProcessor(CodeProcessor):
    def __init__(self, num_chars: int = 6):
        self.num_chars = num_chars

    def process(self, lines: List[str]) -> List[str]:
        result = []
        for line in lines:
            # 空行処理
            if not line.strip():
                result.append(line)
                continue

            # 文字未満 → そのまま出力
            if len(line) < LEADING_CHARS_COUNT:
                result.append(line)
                continue

            # 置換処理
            replaced_line = self._replace_leading_chars_with_spaces(line)
            result.append(replaced_line)

        return result

    def _replace_leading_chars_with_spaces(self, line: str) -> str:
        # 文字を ' ' に置き換え
        return f"{REPLACEMENT_CHAR * LEADING_CHARS_COUNT}{line[LEADING_CHARS_COUNT:]}"
