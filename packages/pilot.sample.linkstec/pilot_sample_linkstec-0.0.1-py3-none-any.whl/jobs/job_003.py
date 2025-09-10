import os
import threading
from pathlib import Path
from typing import List
import time

from pilot.generater.vertexai import VertexAISingleton
from pilot.logging.logger import get_logger
from pilot.processor.code_processor_pipeline import CodeProcessorPipeline
from job import Job
from processors.merge_continuation_lines import MergeContinuationLinesProcessor
from processors.replace_with_todo import ReplaceWithTodoProcessor


class Job_003(Job):
    _begin_file_lock = threading.Lock()

    def __init__(self):
        self.logger = get_logger(__name__)
        super().__init__()

    def run(self):
        with Job_003._begin_file_lock:
            if not self.change_current_trg_to_begin():
                self.logger.warning(f"current_step: {self.current_step}、非同期処理済み SKIP")
                return
        self.logger.debug(f"current_step_file_path: {self.file_path}")

        if os.path.basename(os.path.dirname(self.file_path)) != 'PROCEDURE':
            self.change_current_trg_to_end()
            self.copy_file_and_todo_trg_to_next_step(self.file_path)
            return
        try:
            # 行結合、TODOコメント
            lines = self.read_file_lines()
            pipeline = CodeProcessorPipeline(processors=[
                MergeContinuationLinesProcessor(),
                ReplaceWithTodoProcessor(),
            ])
            processed_lines = pipeline.run(lines)
            #self.write_file_lines(processed_lines)

            # AI転換
            cobol_content = ''.join(processed_lines)

            # テンプレートファイルを読み込んで変数置換
            cwd = os.getcwd()
            template_file_path = os.path.join(cwd, 'input', 'conver_cobol.txt')
            with open(template_file_path, 'r', encoding='utf-8') as f:
                template_file = f.read()

            cobol_content = template_file.replace("{{COBOL_SOURCE_CODE}}", cobol_content)
            # トークン数チェック
            vertexai = VertexAISingleton.get_instance()


            start = time.time()
            result_content = vertexai.generate_content(str(cobol_content))
            end = time.time()
            print(f"vertexai 処理時間 {self.file_path}: {end - start:.2f}秒")

            java_file_path = self.file_path.rsplit('.', 1)[0] + '.java'
            with open(java_file_path, 'w', encoding='utf-8') as f:
                f.write(result_content.get('response', ''))
            self.copy_input_file_to_next_step(java_file_path)
            self.create_current_step_end_trg_file_from_input(java_file_path)
        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        self.change_current_trg_to_end()

        if self.are_all_vcb_files_processed():
            directory = os.path.dirname(self.file_path)
            parent_directory = os.path.dirname(directory)
            next_step_file = parent_directory + '.java'
            Path(next_step_file).touch()
            self.create_next_step_todo_trg_file_from_input(next_step_file)
        super().run()

    def are_all_vcb_files_processed(self):
        directory = os.path.dirname(self.file_path)

        vcd_files = []
        for filename in os.listdir(directory):
            if filename.endswith('.vcb'):
                vcd_files.append(filename)

        for vcd_file in vcd_files:
            vcb_end_file = os.path.splitext(vcd_file)[0] + '.vcb.end'
            vcb_end_path = os.path.join(directory, vcb_end_file)
            if not os.path.exists(vcb_end_path):
                return False

        return True


    def read_file_lines(self):
        with open(self._file_path, 'r', encoding='utf-8') as f:
            _lines = f.readlines()
        return _lines

    def remove_markdown_code_block(self,content):
        content = content.strip()
        if content.startswith('```') and content.endswith('```'):
            lines = content.split('\n')
            if len(lines) >= 3:
                return '\n'.join(lines[1:-1])
            else:
                return '\n'.join(lines[1:-1]) if len(lines) > 2 else ''
        return content

    def write_file_lines_from_input(self,input_file_path: str, lines: List[str]):
        if not input_file_path:
            return None

        with open(input_file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

