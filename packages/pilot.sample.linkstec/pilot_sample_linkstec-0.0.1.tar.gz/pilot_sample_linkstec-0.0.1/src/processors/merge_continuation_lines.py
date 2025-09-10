from typing import List, Set

from pilot.processor.code_processor import CodeProcessor

# COBOLキーワード（処理対象の語句の開始を判定）
COBOL_KEYWORDS = {
    'CALL',
    'COMPUTE',
    'CONTINUE',
    'DIVIDE',
    'DISPLAY',
    'ELSE',
    'END-EVALUATE',
    'END-IF',
    'END-PERFORM',
    'EVALUATE',
    'EXEC',
    'GOBACK',
    'GO TO',
    'IF',
    'INITIALIZE',
    'MOVE',
    'PERFORM',
    'THEN',
    'WHEN',
    'INSPECT',
}

# 関数定義行のパターン
FUNCTION_ENTRY_PATTERN = "SECTION."

# 関数終了行のパターン
FUNCTION_EXIT_PATTERN = "-EXT."

# 結合時の空白文字
CONTINUATION_SPACE = " "


class MergeContinuationLinesProcessor(CodeProcessor):
    def __init__(self, keywords: Set[str] = None):
        self.keywords = keywords or COBOL_KEYWORDS

    def process(self, lines: List[str]) -> List[str]:
        result = []
        current_line = ""
        in_function_body = False  # SECTION. 以降、-EXT. 以前を対象
        after_function_exit = False  # -EXT. 以降の行を処理しない

        for line in lines:
            stripped = line.strip()

            # 関数定義行判定
            if not in_function_body and stripped.endswith(FUNCTION_ENTRY_PATTERN):
                if current_line:
                    result.append(current_line)
                    current_line = ""
                result.append(line)
                in_function_body = True
                continue

            # 関数終了行判定
            if in_function_body and stripped.endswith(FUNCTION_EXIT_PATTERN):
                if current_line:
                    result.append(current_line)
                    current_line = ""
                result.append(line)
                after_function_exit = True
                continue

            # -EXT. 以降の行：処理せずそのまま出力
            if after_function_exit:
                result.append(line)
                continue

            # 本体処理（SECTION. から -EXT. まで）
            if in_function_body:
                # 空行処理
                if not stripped:
                    if current_line:
                        result.append(current_line)
                        current_line = ""
                    result.append(line)
                    continue

                # キーワード開始行判定
                if self._starts_with_keyword(stripped):
                    if current_line:
                        result.append(current_line)
                    current_line = line
                else:
                    # 継続行：前行に結合
                    if current_line:
                        current_line = f"{current_line.rstrip()}{CONTINUATION_SPACE}{line.lstrip()}"
                    else:
                        current_line = line
            else:
                # SECTION. 以前の行は、処理せずそのまま出力
                result.append(line)

        # 最終行の追加
        if current_line:
            result.append(current_line)

        return result

    def _starts_with_keyword(self, line: str) -> bool:
        if not line:
            return False
        upper_line = line.upper()
        return any(
            upper_line.startswith(kw.upper()) for kw in self.keywords
        )
