

from pilot.unit.impl.base_unit import BaseUnit
from job import Job
from jobs.job_000 import Job_000
from jobs.job_001 import Job_001
from jobs.job_002 import Job_002
from jobs.job_003 import Job_003
from jobs.job_004 import Job_004


class Unit(BaseUnit):

    def run(self, index: int = 0):
        print(f'Unit run: {index}')
        super().run(index)

    def _init_job(self, current_step):
        # 重要  stepe毎に　Jobを切り替える
        stepsList = self.config_dto.steps
        if current_step == stepsList[0]:
            return Job_000()
        elif current_step == stepsList[1]:
            return Job_001()
        elif current_step == stepsList[2]:
            return Job_002()
        elif current_step == stepsList[3]:
            return Job_003()
        elif current_step == stepsList[4]:
            return Job_004()
        else:
            print("不明なステップ")
        return Job()

    def job_need_run(self, job:Job ,filename: str, step_index: int):
        if step_index == 0:
            return True
        file_ext =  file_ext = filename.split('.')[-1]
        if file_ext == "trg":
            # ★ trgファイルは、jobのfile_pathに設定する
            job.current_trg_file_path = job.file_path
            job.file_path = job.file_path.rsplit('.trg', 1)[0]
            return True
        elif file_ext == "end":
            job.copy_input_file_to_next_step(job.file_path.rsplit('.', 1)[0])
            job.create_next_step_end_trg_file()
            return False
        elif file_ext  == "begin":
            #job.create_next_step_begin_trg_file()
            return False
        else:
            return False



