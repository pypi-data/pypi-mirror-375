"""Cobolデータ部の分割ツール"""

import os.path
import threading

from pilot.logging.logger import get_logger
from job import Job
from parsing_data_division.parsing_data_division import ParsingDataDivision



class Job_0024(Job):
    _begin_file_lock = threading.Lock()

    def __init__(self):
        self.logger = get_logger(__name__)
        super().__init__()

    def run(self):
        if 'DATA' not in self._file_path:
            return

        with Job_0024._begin_file_lock:
            if not self.change_current_trg_to_begin():
                self.logger.warning(f"current_step: {self.current_step}、非同期処理済み SKIP")
                return
        self.logger.debug(f"current_step_file_path: {self.file_path}")

        try:

            lines = self.read_file_lines()

            file_name = os.path.basename(self._file_path)

            output_file_path_desc = os.path.join(os.path.dirname(self._file_path), 'dto')

            if not os.path.exists(output_file_path_desc):
                os.makedirs(output_file_path_desc, exist_ok=True)

            Parsing_Data_Division_obj = ParsingDataDivision()
            written_files = Parsing_Data_Division_obj.split_cobol_with_flexible_copy(lines, output_file_path_desc)

            for written_file in written_files:
                next_step_file = self.copy_input_file_to_next_step(written_file)
                self.create_current_step_end_trg_file_from_input(written_file)
                self.create_next_step_todo_trg_file_from_input(next_step_file)

        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        self.change_current_trg_to_end()
        super().run()
