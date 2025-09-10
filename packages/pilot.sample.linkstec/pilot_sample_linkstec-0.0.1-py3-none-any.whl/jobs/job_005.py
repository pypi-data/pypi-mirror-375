"""Javaメソッドのパラメーターの変換ツール"""

import os
import threading

from pilot.logging.logger import get_logger
from zzztest.base.get_file_encoding import get_file_encoding
from zzztest.field_change_java.method_field_change import MethodFieldChange
from zzztest.job import Job


class Job_005(Job):
    _begin_file_lock = threading.Lock()

    def __init__(self):
        self.logger = get_logger(__name__)
        super().__init__()

    def run(self):
        with Job_005._begin_file_lock:
            if not self.change_current_trg_to_begin():
                self.logger.warning(f"current_step: {self.current_step}、非同期処理済み SKIP")
                return
        self.logger.debug(f"current_step_file_path: {self.file_path}")

        try:
            java_line = self.read_file_lines()
            module_name = os.path.basename(self.file_path).split('.')[0]

            json_file_path = os.path.join(str(self.config_dto.json_file_path), module_name)

            mapping_data = {}

            field_change = MethodFieldChange()
            for json_root, json_dirs, json_files in os.walk(json_file_path):
                for json_file in json_files:
                    if json_file.lower().endswith('json'):
                        json_file_path = os.path.join(json_root, json_file)
                        if os.path.exists(json_file_path):
                            json_file_key = json_file.replace('_fields_info.json', '')
                            # JSONファイルのエンコーディング取得
                            json_encoding = get_file_encoding(json_file_path)
                            # マッピング読み込み
                            mapping_json_data = field_change.load_work_mapping(json_file_path, json_encoding)
                            mapping_data[json_file_key] = mapping_json_data

            # Javaコードの変換処理
            processed_code = field_change.process_java_code(mapping_data, java_line)
            file_change_desc_path = os.path.join(os.path.dirname(self.file_path), 'java')
            if not os.path.exists(file_change_desc_path):
                os.makedirs(file_change_desc_path, exist_ok=True)

            changed_file_name = os.path.join(file_change_desc_path, module_name + '.java')
            # 変換後コードをUTF-8で書き込み
            with open(changed_file_name, 'w', encoding='utf-8') as f:
                for item in processed_code:
                    if '\n' in item:
                        f.write(item)
                    else:
                        f.write(item + '\n')

        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        self.change_current_trg_to_end()
        super().run()
