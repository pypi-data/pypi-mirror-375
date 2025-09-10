import threading

from pilot.conver.nkf_converter import NkfConverter
from pilot.logging.logger import get_logger

from job import Job


class Job_001(Job):
    _begin_file_lock = threading.Lock()


    def run(self):
        with Job_001._begin_file_lock:
            if not self.change_current_trg_to_begin():
                self.logger.warning(f"current_step: {self.current_step}、非同期処理済み SKIP")
                return
        self.logger.debug(f"current_step_file_path: {self.file_path}")

        try:
            # ファイルの文字コードをUTF-8に変換する
            NkfConverter().convert(self.file_path)
        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        self.copy_current_file_to_next_step()
        self.change_current_trg_to_end()
        self.create_next_step_todo_trg_file()
        super().run()
