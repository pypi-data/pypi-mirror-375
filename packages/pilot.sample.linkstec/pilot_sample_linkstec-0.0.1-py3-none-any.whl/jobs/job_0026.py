"""Cobol　⇒　Java　Dtoの変換ツール"""
import os.path
import threading

from pilot.logging.logger import get_logger
from base.cobol_to_java_base import CobolToJavaBase
from base.make_cst_java import MakeCstJava
from job import Job


class Job_0026(Job):
    _begin_file_lock = threading.Lock()

    def __init__(self):
        self.logger = get_logger(__name__)
        super().__init__()

    def run(self):
        if 'DATA' not in self._file_path:
            if 'dto_after' not in self._file_path:
                return

        with Job_0026._begin_file_lock:
            if not self.change_current_trg_to_begin():
                self.logger.warning(f"current_step: {self.current_step}、非同期処理済み SKIP")
                return
        self.logger.debug(f"current_step_file_path: {self.file_path}")

        try:

            input_file_path = self._file_path

            file_name = os.path.basename(self._file_path)

            module_name = os.path.basename(os.path.dirname(input_file_path.split('DATA')[0]))

            package_name = module_name + '.dto'

            json_file_name = file_name.split('.')[0] + '_fields_info.json'

            output_file_path_desc = os.path.join(os.path.dirname(self._file_path), 'dto')

            json_file_path =os.path.join(self.config_dto.json_file_path , module_name)

            if not os.path.exists(output_file_path_desc):
                os.makedirs(output_file_path_desc, exist_ok=True)

            if not os.path.exists(json_file_path):
                os.makedirs(json_file_path, exist_ok=True)

            if file_name.startswith('CST'):
                line = self.read_file_lines()
                MakeCstToJava = MakeCstJava()
                MakeCstToJava.process_cbl_files(file_name, line, output_file_path_desc, json_file_path)
            else:
                MakeCblToJava = CobolToJavaBase()
                MakeCblToJava.generate_all(input_file_path, package_name, output_file_path_desc)

        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        self.change_current_trg_to_end()
        super().run()
