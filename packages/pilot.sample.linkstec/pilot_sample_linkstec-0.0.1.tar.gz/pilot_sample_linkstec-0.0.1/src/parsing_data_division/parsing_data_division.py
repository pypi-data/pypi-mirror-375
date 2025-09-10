import os
import re


class ParsingDataDivision():


    def flush_current(self, current_part, current_part_name, parts):
        if current_part:
            if current_part_name is not None and current_part_name.upper() != 'FILLER':
                # print(f"Flush block '{current_part_name}' with {len(current_part)} lines")
                parts.append((current_part_name, current_part))
        # 返回空列表和None，表示清空状态
        return [], None

    def split_cobol_with_flexible_copy(self, file_lines, out_put_path):

        parts = []  # 用来保存结果块: 元组(name, list_of_lines)
        current_part = []
        current_part_name = None

        # 更宽松的01行匹配，只要是01开头并捕获紧跟的名称，允许后面有任意内容
        pattern_01 = re.compile(r'^\s*01\s+([A-Z0-9\-_]+)', re.IGNORECASE)
        pattern_copy = re.compile(r'^\s*COPY\s+([A-Z0-9\-_]+)(\s.*)?\.?\s*$', re.IGNORECASE)
        pattern_comment = re.compile(r'^\s*\*')

        for idx, line in enumerate(file_lines, 1):
            if pattern_comment.match(line):
                # 过滤注释行
                continue

            m_01 = pattern_01.match(line)
            m_copy = pattern_copy.match(line)

            if m_01:
                # 遇到新的01块，先flush旧块
                current_part, current_part_name = self.flush_current(current_part, current_part_name, parts)
                name = m_01.group(1).upper()

                if name == 'FILLER':
                    # FILLER块不作为单独文件输出，同时不积累内容
                    current_part_name = None
                    current_part = []
                else:
                    current_part_name = name
                    current_part = [line]

            elif m_copy:
                copy_name = m_copy.group(1).upper()
                if current_part_name is not None:
                    # COPY属于当前01块，加入
                    current_part.append(line)
                else:
                    # COPY独立存在，单独拆文件
                    current_part, current_part_name = self.flush_current(current_part, current_part_name, parts)
                    parts.append((copy_name, [line]))
            else:
                # 普通行，只有当前有活动块才加入
                if current_part_name is not None:
                    current_part.append(line)

        # 循环结束flush剩余块
        current_part, current_part_name = self.flush_current(current_part, current_part_name, parts)

        written_files = []
        # 写文件
        for name, block_lines in parts:
            filename = os.path.join(out_put_path, f"{name}.java")
            with open(filename, 'w', encoding='utf-8') as fw:
                fw.writelines(block_lines)

            written_files.append(filename)

        return written_files
