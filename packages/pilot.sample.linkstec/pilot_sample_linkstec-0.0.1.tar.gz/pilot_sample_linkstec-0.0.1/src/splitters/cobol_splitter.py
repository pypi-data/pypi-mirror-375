import os
import re
from typing import List, Dict

from pilot.logging.logger import get_logger


class CobolSplitter:
    """
    COBOL ファイル分割器、COBOL ソースファイルを DIVISION と SECTION に分割する
    """
    DIVISION_HEADER_PATTERN = re.compile(
        r"^\s*(IDENTIFICATION|ENVIRONMENT|DATA|PROCEDURE)\s+DIVISION",
        re.IGNORECASE
    )
    SECTION_HEADER_PATTERN = re.compile(
        r"^\s*([A-Z0-9\-_]+)\s+SECTION",
        re.IGNORECASE
    )

    def __init__(self, input_file: str, lines: List[str]):
        self.logger = get_logger(__name__)
        self.input_file = input_file
        self.lines = lines
        self.divisions: Dict[str, List[str]] = {
            "IDENTIFICATION": [],
            "ENVIRONMENT": [],
            "DATA": [],
            "PROCEDURE": []
        }
        self.procedure_sections: Dict[str, List[str]] = {}

    def _parse_file(self):
        """
        COBOL コード行のリストを解析し、DIVISION と SECTION に分割
        """
        self.logger.debug("COBOL コードを解析中")

        # 全体の行を処理
        current_division = None
        temp_lines = []

        # DIVISION の分割処理
        for line in self.lines:
            # 新しい DIVISION 開始を確認
            match = self.DIVISION_HEADER_PATTERN.match(line)
            if match:
                # 以前の DIVISION があれば保存
                if current_division and temp_lines:
                    self.divisions[current_division].extend(temp_lines)

                # 新しい DIVISION を開始
                current_division = match.group(1).upper()
                temp_lines = []
                self.logger.debug(f"{current_division} DIVISION を発見しました")
            else:
                temp_lines.append(line)

        # 最後の DIVISION を保存
        if current_division and temp_lines:
            self.divisions[current_division].extend(temp_lines)

        # PROCEDURE DIVISION の SECTION 分割
        self._split_procedure_sections()

        self.logger.debug("COBOL コードの解析完了")

    def _split_procedure_sections(self):
        """
        PROCEDURE DIVISION 内容を SECTION ごとに分割
        """
        self.logger.debug("PROCEDURE DIVISION を SECTION に分割中")

        # PROCEDURE DIVISION の内容を取得
        procedure_lines = self.divisions["PROCEDURE"]
        if not procedure_lines:
            return

        # SECTION で分割
        current_section = None
        current_lines = []

        for line in procedure_lines:
            # SECTION 開始を確認
            match = self.SECTION_HEADER_PATTERN.match(line)
            if match:
                # 以前の SECTION があれば保存
                if current_section is not None and current_lines:
                    self.procedure_sections[current_section] = current_lines.copy()

                # 新しい SECTION を開始
                current_section = match.group(1).upper()
                current_lines = [line]
                self.logger.debug(f"SECTION '{current_section}' を発見しました")
            else:
                # SECTION 内の行を追加
                if current_section is not None:
                    current_lines.append(line)
                else:
                    # SECTION がない場合、MAIN を作成
                    current_section = "MAIN"
                    current_lines = [line]

        # 最後の SECTION を保存
        if current_section is not None and current_lines:
            self.procedure_sections[current_section] = current_lines.copy()

        self.logger.debug(f"合計 {len(self.procedure_sections)} 個の SECTION を発見しました")

    def _write_division_files(self, output_dir: str, base_name: str, file_ext: str) -> List[str]:
        """
        DIVISION の内容をファイルに書き込む

        :param output_dir: 出力ディレクトリのパス
        :param base_name: ファイル名（拡張子を除く）
        :param file_ext: ファイルの拡張子（ドット付き）
        :return: 書き込まれたファイルのパスリスト
        """
        self.logger.debug("DIVISION ファイルを書き込み中")

        written_files = []

        # DIVISION ディレクトリを作成
        division_dirs = ["IDENTIFICATION", "ENVIRONMENT", "DATA"]
        for div_dir in division_dirs:
            div_output_dir = os.path.join(output_dir, div_dir)
            os.makedirs(div_output_dir, exist_ok=True)

            # DIVISION の内容をファイルに書き込み
            content = self.divisions.get(div_dir, [])
            if content:
                file_path = os.path.join(
                    div_output_dir,
                    f"{base_name}_{div_dir}{file_ext}"
                )
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(content)
                written_files.append(file_path)
                self.logger.debug(f"DIVISION ファイルを書き込みました: {file_path}")

        return written_files

    def _write_procedure_section_files(self, output_dir: str, base_name: str, file_ext: str) -> List[str]:
        """
        PROCEDURE DIVISION の SECTION をファイルに書き込む

        :param output_dir: 出力ディレクトリのパス
        :param base_name: ファイル名（拡張子を除く）
        :param file_ext: ファイルの拡張子（ドット付き）
        :return: 書き込まれたファイルのパスリスト
        """
        self.logger.debug("PROCEDURE DIVISION の SECTION ファイルを書き込み中")

        written_files = []

        # PROCEDURE ディレクトリを作成
        proc_output_dir = os.path.join(output_dir, "PROCEDURE")
        os.makedirs(proc_output_dir, exist_ok=True)

        # SECTION をファイルに書き込み（序号付き）
        for index, (section_name, section_lines) in enumerate(self.procedure_sections.items(), 1):
            # 3桁のゼロ埋め序号を作成
            seq_number = f"{index:03d}"

            # ファイル名を構築
            file_path = os.path.join(
                proc_output_dir,
                f"{base_name}_{seq_number}_{section_name}{file_ext}"
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(section_lines)
            written_files.append(file_path)
            self.logger.debug(f"SECTION ファイルを書き込みました: {file_path}")

        return written_files

    def run(self) -> List[str]:
        """
        COBOL コードを解析し、ファイルに書き込む

        :return: 書き込まれたファイルのパスリスト
        """
        self.logger.debug("COBOL コードの解析とファイル書き込みを開始")

        # 解析処理
        self._parse_file()

        # 出力ディレクトリの作成
        input_dir = os.path.dirname(self.input_file)
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        file_ext = os.path.splitext(self.input_file)[1]
        output_dir = os.path.join(input_dir, base_name)
        os.makedirs(output_dir, exist_ok=True)

        # ファイル書き込み
        written_files = []

        # DIVISION ファイルの書き込み
        division_files = self._write_division_files(output_dir, base_name, file_ext)
        written_files.extend(division_files)

        # SECTION ファイルの書き込み
        section_files = self._write_procedure_section_files(output_dir, base_name, file_ext)
        written_files.extend(section_files)

        self.logger.debug(f"ファイル書き込み完了。合計 {len(written_files)} 個のファイルを書き込みました")
        return written_files
