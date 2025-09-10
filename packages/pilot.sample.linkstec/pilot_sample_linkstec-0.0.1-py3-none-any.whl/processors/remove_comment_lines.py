from typing import List

from pilot.processor.code_processor import CodeProcessor

# コメント行の開始文字
COMMENT_LEAD_CHAR = "*"


class RemoveCommentLinesProcessor(CodeProcessor):
    def process(self, lines: List[str]) -> List[str]:
        result = []
        for line in lines:
            if line.lstrip().startswith(COMMENT_LEAD_CHAR):
                continue
            if line.strip() in {"SKIP1", "SKIP2", "SKIP3", "EJECT"}:
                continue
            result.append(line)
        return result
