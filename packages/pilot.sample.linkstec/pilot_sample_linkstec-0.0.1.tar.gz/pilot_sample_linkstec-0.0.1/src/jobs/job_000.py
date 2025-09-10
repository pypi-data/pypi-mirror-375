from job import Job


class Job_000(Job):
    # __init__ は省略。BaseJobのものを継承。
    def run(self):
        #print(f"[zzztest Job] step_index: {self.step_index}")
        #print(f"[zzztest Job] current_step: {self.current_step}")
        #print(f"[zzztest Job] get_relative_path: {self.file_path}")
        self.copy_current_file_to_next_step()
        self.create_next_step_todo_trg_file()
        super().run()


