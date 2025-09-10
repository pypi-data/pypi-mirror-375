import os
import threading

from pilot.logging.logger import get_logger
from job import Job


class Job_004(Job):
    _begin_file_lock = threading.Lock()

    def __init__(self):
        self.logger = get_logger(__name__)
        super().__init__()

    def run(self):
        with Job_004._begin_file_lock:
            if not self.change_current_trg_to_begin():
                self.logger.warning(f"current_step: {self.current_step}、非同期処理済み SKIP")
                return
        self.logger.debug(f"current_step_file_path: {self.file_path}")

        try:
            # SECTION結合
            directory = self.file_path.rsplit('.', 1)[0] + '/PROCEDURE'
            java_files = sorted([f for f in os.listdir(directory) if f.endswith('.java')])
            with open(self.file_path, 'w', encoding='utf-8') as outfile:
                for java_file in java_files:
                    vcb_path = os.path.join(directory, java_file)
                    with open(vcb_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read() + '\n\n')
        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        self.change_current_trg_to_end()
        super().run()
