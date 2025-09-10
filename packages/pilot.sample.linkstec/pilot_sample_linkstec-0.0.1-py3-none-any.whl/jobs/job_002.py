import threading

from pilot.logging.logger import get_logger
from pilot.processor.code_processor_pipeline import CodeProcessorPipeline
from job import Job
from processors.remove_comment_lines import RemoveCommentLinesProcessor
from processors.trim_leading_chars_to_spaces import TrimLeadingCharsToSpacesProcessor
from splitters.cobol_splitter import CobolSplitter


class Job_002(Job):
    _begin_file_lock = threading.Lock()

    def __init__(self):
        self.logger = get_logger(__name__)
        super().__init__()

    def run(self):
        with Job_002._begin_file_lock:
            if not self.change_current_trg_to_begin():
                self.logger.warning(f"current_step: {self.current_step}、非同期処理済み SKIP")
                return
        self.logger.debug(f"current_step_file_path: {self.file_path}")

        try:
            # 先頭6桁置換、コメント削除
            lines = self.read_file_lines()
            pipeline = CodeProcessorPipeline(processors=[
                TrimLeadingCharsToSpacesProcessor(),
                RemoveCommentLinesProcessor(),
            ])
            processed_lines = pipeline.run(lines)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.writelines(processed_lines)
            # DIVISION、SECTION分割
            splitter = CobolSplitter(self.file_path, processed_lines)
            written_files = splitter.run()
            for written_file in written_files:
                next_step_file = self.copy_input_file_to_next_step(written_file)
                self.create_current_step_end_trg_file_from_input(written_file)
                self.create_next_step_todo_trg_file_from_input(next_step_file)
        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        self.change_current_trg_to_end()
        super().run()

    def read_file_lines(self):
        with open(self._file_path, 'r', encoding='utf-8') as f:
            _lines = f.readlines()
        return _lines