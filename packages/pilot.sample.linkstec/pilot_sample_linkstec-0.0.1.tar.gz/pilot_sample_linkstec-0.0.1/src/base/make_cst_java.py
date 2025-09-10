#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MakeCstJava – 将 COBOL 常量定义 (*.cbl) 转成
    1. Java constants 类（常量位于类内部，符合示例）
    2. 对应的字段信息 JSON（保持原实现）
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

from base import cobol_util
from base.java_code_builder import JavaCodeBuilder
from base.parsing_cobol import ParsingCobol

# --------------------------------------------------------------
# 正则（保持不变）
# --------------------------------------------------------------
COBOL_CONST_RE = re.compile(
    r"""^\s*\d+\s+                # 行号（可有可无） + 空格
        (?P<name>[\w-]+)          # 变量名（可能包含 -）
        \s+PIC\s+(?P<pic>[XS9Vv()0-9]+)   # PIC 描述
        \s+VALUE\s+(?P<value>
            (?:X'[0-9A-Fa-f]{2}'      # 十六进制字符常量
            |'(?:[^'\\]|\\.)*'        # 单引号字符串（支持转义）
            |SPACE                     # 关键字 SPACE
            |[-\d\.]+)                # 数值（正负、整数或小数）
        )\s*\.
    """,
    re.MULTILINE | re.VERBOSE,
)


class CobolParseError(RuntimeError):
    """在解析 COBOL 常量或字段树时抛出的统一异常"""
# --------------------------------------------------------------
# 小工具（保持原实现）
# --------------------------------------------------------------
def to_java_const_name(cobol_name: str) -> str:
    return cobol_name.replace("-", "_").upper()

def literal_from_cobol(value_raw: str, java_type: str, pic: str) -> str:
    if value_raw == "SPACE":
        return '" "'
    if value_raw.startswith("X'"):
        hex_body = value_raw[2:-1]
        return f'"\\x{hex_body}"'
    if value_raw.startswith("'") and value_raw.endswith("'"):
        inner = value_raw[1:-1]
        m = re.search(r"\((\d+)\)", pic)
        length = int(m.group(1)) if m else len(inner)
        if len(inner) < length:
            inner = inner.ljust(length)
        escaped = inner.replace("\\", r"\\").replace('"', r'\"')
        return f'"{escaped}"'
    if java_type == "BigDecimal":
        return f'new BigDecimal("{value_raw}")'
    return value_raw


# --------------------------------------------------------------
# 5️⃣ JavaFileBuilder（改成“常量在类内部”）
# --------------------------------------------------------------
class JavaFileBuilder:
    """帮助构造符合示例的 Java 常量类"""

    INDENT = " " * 4

    def __init__(self, package: str = "constants"):
        self.package = package
        self.constants: List[Tuple[str, str, str]] = []   # (type, name, literal)
        self.class_name: str | None = None

    def set_class_name(self, name: str) -> None:
        self.class_name = name

    def add_constant(self, java_type: str, const_name: str, literal: str) -> None:
        self.constants.append((java_type, const_name, literal))

    def render(self) -> str:
        if self.class_name is None:
            raise RuntimeError("class name not set")

        lines: List[str] = [f"package {self.package};", ""]   # package + blank line
        lines.append(f"public class {self.class_name} {{")

        for jt, cn, lit in self.constants:
            lines.append(f"{self.INDENT}public static final {jt} {cn} = {lit};")

        lines.append("}")
        return "\n".join(lines)


# --------------------------------------------------------------
# 6️⃣ 主业务类（只改动 parse_cobol_code 部分）
# --------------------------------------------------------------
class MakeCstJava:
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.log = logger or logging.getLogger(__name__)

    @staticmethod
    def _parse_one_const(match: re.Match) -> Tuple[str, str, str, bool]:
        name_raw = match.group("name")
        if name_raw.upper() == "FILLER":
            raise CobolParseError()
        const_name = to_java_const_name(name_raw)
        pic = match.group("pic")
        value_raw = match.group("value").strip()
        java_type, need_bd = cobol_util.pic_to_java_type(pic)
        literal = literal_from_cobol(value_raw, java_type, pic)
        return const_name, java_type, literal, need_bd

    def parse_cobol_code(self, cobol_code: str | List[str], class_name: str) -> str:
        # 统一为字符串并做 :Q: → CST 替换
        cobol_src = "\n".join(cobol_code) if isinstance(cobol_code, list) else cobol_code
        cobol_src = cobol_src.replace(":Q:", "CST")

        builder = JavaFileBuilder(package="constants")
        builder.set_class_name(class_name)

        for m in COBOL_CONST_RE.finditer(cobol_src):
            try:
                const_name, java_type, literal, _ = self._parse_one_const(m)
            except CobolParseError:
                continue
            builder.add_constant(java_type, const_name, literal)

        return builder.render()

    # ----------------- JSON 相关保持不变 -----------------
    @staticmethod
    def _write_json(data: List[Dict], target_path: Path) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def process_cbl_files(
        self,
        file_name: str,
        cobol_code: str | List[str],
        output_folder: Path | str,
        json_file_path: Path | str,
    ) -> None:
        out_dir = Path(output_folder)
        json_dir = Path(json_file_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        json_dir.mkdir(parents=True, exist_ok=True)

        # 生成类名（保持原来的 JavaCodeBuilder 用法）
        class_name = JavaCodeBuilder().to_class_name(Path(file_name).stem)
        java_src = self.parse_cobol_code(cobol_code, class_name)
        java_path = out_dir / f"{class_name}.java"
        java_path.write_text(java_src, encoding="utf-8")
        self.log.info("Wrote Java file: %s", java_path)

        # ---------- JSON ----------
        cobol_parser = ParsingCobol()
        root_node = cobol_parser.parse_cobol_file(cobol_code, "CST-")
        cobol_parser.assign_offsets(root_node)
        fields_info = cobol_parser.update_json_item(
            cobol_parser.collect_field_info(root_node)
        )
        json_path = json_dir / f"{Path(file_name).stem}_fields_info.json"
        self._write_json(fields_info, json_path)
        self.log.info("Wrote JSON file: %s", json_path)