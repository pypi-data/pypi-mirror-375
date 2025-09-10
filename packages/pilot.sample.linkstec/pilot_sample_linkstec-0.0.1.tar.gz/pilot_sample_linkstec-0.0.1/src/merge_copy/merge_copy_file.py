import os
import re

from base.get_file_encoding import get_file_encoding


class MergeCopyFile:

    PATTERN_COPY = re.compile(
            r'^\s*COPY\s+([A-Z0-9\-_]+)'  # COPY名
            r'(?:\s+REPLACING\s+==([^=]+)==\s+BY\s+==([^=]+)==)?'  # 可能的REPLACING old,new
            r'\.?\s*$', re.IGNORECASE)

    def expand_copy_in_file(self, file_name, cbl_lines, copy_dir, output_file_path_desc):

        expanded_lines = []
        special_old = ':Q:'
        special_new = 'CST'

        for idx, line in enumerate(cbl_lines, 1):
            m = self.PATTERN_COPY.match(line)
            if m:
                copy_name = m.group(1)
                replacing_old = m.group(2)
                replacing_new = m.group(3)
                copy_file = os.path.join(copy_dir, copy_name, copy_name + '.rec')  # 根据实际路径及后缀修改
                if not os.path.exists(copy_file):
                    print(f'{copy_name} is not found.')
                    continue
                if os.path.isfile(copy_file):
                    copy_file_encoding = get_file_encoding(copy_file)
                    with open(copy_file, 'r', encoding=copy_file_encoding) as cf:
                        copy_content = cf.readlines()

                    # 处理 REPLACING
                    if replacing_old is not None and replacing_new is not None:
                        replaced_content = [l.replace(replacing_old, replacing_new) for l in copy_content]

                        # 如果是特定替换 ==:Q:== BY ==CST==，将替换后的代码追加写入 Constants.java
                        if replacing_old == special_old and replacing_new == special_new:
                            return None
                        expanded_lines.extend(replaced_content)
                    else:
                        expanded_lines.extend(copy_content)
                else:
                    expanded_lines.append(line)
            else:
                expanded_lines.append(line)

        # 写入输出文件（覆盖写）
        output_file = os.path.join(output_file_path_desc, file_name)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(expanded_lines)
        print(f"Finished processing {output_file}")
        # print(f"Constants.java updated at {constants_file}")

        return output_file