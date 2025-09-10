"""Copyファイルの内容はCobolファイルにマージツール"""

import os
import os.path
import threading

from pilot.logging.logger import get_logger
from job import Job
from merge_copy.merge_copy_file import MergeCopyFile


class Job_0025(Job):
    _begin_file_lock = threading.Lock()

    def __init__(self):
        self.logger = get_logger(__name__)
        super().__init__()

    def run(self):
        if 'DATA' not in self._file_path:
            if 'dto' not in self._file_path:
                return

        with Job_0025._begin_file_lock:
            if not self.change_current_trg_to_begin():
                self.logger.warning(f"current_step: {self.current_step}、非同期処理済み SKIP")
                return
        self.logger.debug(f"current_step_file_path: {self.file_path}")

        try:

            lines = self.read_file_lines()

            copy_file_path = self.config_dto.copy_path

            file_name = os.path.basename(self._file_path)

            output_file_path_desc = os.path.join(os.path.dirname(self._file_path), 'dto_after')

            if not os.path.exists(output_file_path_desc):
                os.makedirs(output_file_path_desc, exist_ok=True)

            merge_copy_obj = MergeCopyFile()

            written_file = merge_copy_obj.expand_copy_in_file(file_name, lines, copy_file_path, output_file_path_desc)

            next_step_file = self.copy_input_file_to_next_step(written_file)
            self.create_current_step_end_trg_file_from_input(written_file)

            self.create_next_step_todo_trg_file_from_input(next_step_file)

        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        self.change_current_trg_to_end()
        super().run()




