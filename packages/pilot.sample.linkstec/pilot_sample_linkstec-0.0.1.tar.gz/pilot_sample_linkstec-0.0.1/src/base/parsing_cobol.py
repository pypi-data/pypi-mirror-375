import re

from base.cobol_java_field import JavaCobolField


class ParsingCobol:

    # -------- 解析整个COBOL文件，建立树 ----------
    def parse_cobol_file(self,  cobol_lines, replace_str:str = ''):
        # 创建根节点，层级0，名称为"Root"
        root = JavaCobolField(0, "Root")
        # 用栈结构维护嵌套层级，初始栈中只有根节点
        stack = [root]

        # --------------------------------------------------------------
        # ① 把任意输入统一为 List[str]
        # --------------------------------------------------------------
        if isinstance(cobol_lines, list):
            lines = cobol_lines  # 已经是列表，直接使用
        else:
            # 不是列表 → 当作整体字符串处理。
            # 使用 str.splitlines() 能一次识别 \\n、\\r\\n、\\r，且会把结尾的换行符去掉。
            # 为了兼容可能传入的 bytes，也先做一次 decode（默认 utf‑8）。
            if isinstance(cobol_lines, (bytes, bytearray)):
                cobol_str = cobol_lines.decode("utf-8", errors="replace")
            else:
                cobol_str = str(cobol_lines)  # 确保是 str
            lines = cobol_str.splitlines()  # → List[str]

        lines_processed = []  # 存放合并拼接后的有效COBOL语句行
        buffer_line = ""  # 拼接缓冲区，用于合并多行成一条完整语句

        i = 0
        while i < len(lines):
            # COBOL代码有效文本部分，从第7个字符开始读取（COBOL固定格式，前6为行号或空白）
            line_check = lines[i][6:].strip().rstrip('\n')
            line = lines[i].rstrip('\n')

            # 如果该行（去除前6个字符后）是空，跳过
            if not line_check:
                i += 1
                continue

            # 忽略注释行（以*开头）
            if not line_check.startswith("*"):
                # 如果buffer为空则直接赋值，否则用空格连接，拼接多行语句
                if not buffer_line:
                    buffer_line = line
                else:
                    buffer_line += " " + line

            # 如果拼接字符串以点号（.）结尾，说明这是一个完整的COBOL语句
            if buffer_line.endswith('.'):
                lines_processed.append(buffer_line)  # 加入最终语句列表
                buffer_line = ""  # 清空buffer，准备下一条语句
            else:
                # 如果已到文件末尾，最后一次也将buffer写入，以防最后一句缺失点号
                if i == len(lines) - 1:
                    lines_processed.append(buffer_line)
                    buffer_line = ""
            i += 1

        # 遍历所有拼接好的语句，解析为字段（field）结构
        for line in lines_processed:
            field = self.parse_cobol_line(line, replace_str)  # 解析单条COBOL语句，返回CobolField实例
            if field is None:
                continue  # 如果解析失败跳过

            # if field.name.strip().upper() == 'FILLER':
            #     continue  # 如果FILLER跳过

            # 如果字段节点(level)为1，且pic属性为None或者空字符串，则直接挂到根节点
            if field.level == 1 and (not hasattr(field, 'pic') or field.pic in (None, '', 'NONE')):
                root.children.append(field)
                stack = [root]
                continue

            # 使用栈结构找合适的父层节点（层级小于当前field为父节点）
            while stack and stack[-1].level >= field.level:
                stack.pop()

            parent = stack[-1]  # 获取父节点
            parent.children.append(field)  # 将当前field加入父节点的children列表
            stack.append(field)  # 当前field入栈，成为后续字段的父节点候选

        return root  # 返回解析完成的根节点，整个字段树结构

    # -------- 解析一行COBOL字段 ----------
    def parse_cobol_line(self, line, replace_str):
        line = line[6:].strip().replace(':Q:-', replace_str)
        if not line or line.startswith('*'):
            return None

        pattern = re.compile(
            r'(\d+)\s+([^\s\.]+)'  # 1 level number, 2 field name
            r'(?:\s+(?:'  # non-capturing group, repeated 0~2 times to匹配任意顺序PIC或REDEFINES
            r'REDEFINES\s+([^\s\.]+)'  # 3 redefines field name
            r'|'
            r'PIC\s+((?:(?!\s+(?:REDEFINES|VALUE|OCCURS)\b).)*)'  # 4 PIC clause内容，排除REDEFINES VALUE OCCURS作为结束 
            r')){0,2}'
            r'(?:\s+OCCURS\s+(\d+))?'  # 5 OCCURS
            r'(?:\s+VALUE\s+(?:'  # optional VALUE
            r'\'([^\']*)\'|'  # 6 单引号value
            r'"([^"]*)"|'  # 7 双引号value
            r'([^\s\.]+)'  # 8 无引号value
            r'))?'
            r'\s*\.?'  # 可选句点结尾及空白
            r'(.*)',  # 9 剩余注释或空白
            re.IGNORECASE
        )

        match = pattern.match(line)
        level = None
        name = ''
        pic = None
        length = 0
        decimal = False
        comp3 = False
        default = ''
        comment = ''
        occurs_count = 0
        redefines_field_name = None
        if not match:
            return None

        if match:
            level = int(match.group(1))
            name = match.group(2)
            redefines_field_name = match.group(3)
            pic_str = match.group(4).strip() if match.group(4) else None
            occurs_count = int(match.group(5)) if match.group(5) else 0
            default = match.group(6) or match.group(7) or match.group(8)
            comment = match.group(9).strip() if match.group(9) else ""

            if 'PIC' in comment and pic_str is None:
                pic_str = comment.strip()
            pic = None
            length = 0
            decimal = False
            comp3 = False
            if pic_str:
                pic, length, decimal, comp3 = self.parse_pic(pic_str)

        return JavaCobolField(level, name, pic, length, decimal, comp3, default, comment, occurs_count,
                              redefines=redefines_field_name)

    # -------- 解析PIC格式 ----------
    def parse_pic(self, pic_str):
        comp3 = False
        if pic_str is None:
            return None, 0, False, comp3
        pic_str = pic_str.upper().strip()
        if "COMP-3" in pic_str:
            comp3 = True
            pic_str = pic_str.replace("COMP-3", "").strip()
        # 兼容 PIC X(000050) 或 PIC 9(0050)V9(002) 等格式
        pattern = r'([A-Z9X])\((0*\d+)\)(?:V9\((0*\d+)\))?'
        match = re.match(pattern, pic_str)
        if not match:
            if 'V9' in pic_str or 'Z9' or 'S9' in pic_str:
                pic_type = '9'
                length = 0
                decimal = True
                arr = pic_str.split('(')
                str_1 = 0
                str_2 = 0
                if len(arr) > 1:
                    str_1 = int(arr[1].split(')')[0])
                    if len(arr) > 2:
                        str_2 = int(arr[2].split(')')[0])
                    length = str_1 + str_2
                else:
                    if 'Z9' in pic_str:
                        str_1 = len(pic_str)
                    else:
                        # str_1 = int(arr[1].split(')')[0])
                        if len(arr) > 1:
                            arr_index = 1
                        else:
                            arr_index = 0

                        if ')' in arr[arr_index]:
                            str_1 = int(arr[arr_index].split(')')[0])
                        else:
                            if '-' in arr[arr_index]:
                                str_1 = len(arr[arr_index].replace('-', ''))
                            else:
                                str_1 = 0

                    length = str_1
                return pic_type, length, decimal, comp3
            if '-9.9' or '-9' in pic_str:
                pic_type = '9'
                decimal = True
                pic_str_del_h = pic_str.replace('-', '')
                if '.' in pic_str_del_h:
                    length = len(pic_str_del_h.split('.')[0]) + len(pic_str_del_h.split('.')[1])
                else:
                    length = len(pic_str_del_h)
                return pic_type, length, decimal, comp3
            return None, 0, False, comp3
        pic_type = match.group(1)
        length_str = match.group(2)
        decimal_str = match.group(3)

        length = int(length_str.lstrip('0') or '0') if length_str else 1
        decimal_digits = int(decimal_str.lstrip('0') or '0') if decimal_str else 0
        decimal = decimal_digits > 0

        return pic_type, length, decimal, comp3

    # -------- 计算offset ----------
    def assign_offsets(self, field: JavaCobolField):
        """
        递归给子字段分配offset_in_parent偏移量:
        - 普通字段顺序累加长度
        - REDEFINES字段offset与被redefines字段一致
        """
        offset = 0
        name_to_field = {}

        for child in field.children:
            if child.redefines is None:
                child.offset_in_parent = offset
                offset += child.length
                name_to_field[child.name] = child

        for child in field.children:
            if child.redefines:
                if child.redefines in name_to_field:
                    child.offset_in_parent = name_to_field[child.redefines].offset_in_parent
                else:
                    print(f"[WARN] ReDefines 找不到字段: {child.redefines}")
                    child.offset_in_parent = 0

        for child in field.children:
            if child.pic is None and child.children:
                self.assign_offsets(child)

    def update_json_item(self, fields_info_list):
        # 先处理 same_obj
        # 用一个字典统计 (name, parent) 出现次数
        count_dict = {}
        for item in fields_info_list:
            key = (item["name"], item["parent"])
            count_dict[key] = count_dict.get(key, 0) + 1

        # 针对重复的，把 same_obj 置为 True
        for item in fields_info_list:
            key = (item["name"], item["parent"])
            if count_dict[key] > 1:
                item["same_obj"] = True
            else:
                item["same_obj"] = False

        # 然后处理 all_fillers
        # 首先创建 parent -> children 映射
        parent_map = {}
        for item in fields_info_list:
            parent = item["parent"]
            if parent not in parent_map:
                parent_map[parent] = []
            parent_map[parent].append(item)

        # 遍历所有项目，找到 type == 'dto' 的，判断其孩子的 type 是否全部为 'filler'
        for item in fields_info_list:
            if item["type"] == "dto":
                children = parent_map.get(item["name"], [])
                if children and all(child["name"] == "FILLER" for child in children):
                    item["all_fillers"] = True
                else:
                    item["all_fillers"] = False

        return fields_info_list

    def collect_field_info(self, field: JavaCobolField, parent_name=None, parent_type=None):
        if field.level == 0 and field.name == "Root":
            field_type = "Root"
        elif field.occurs_count > 0:
            field_type = "List"
        elif field.pic is None:
            field_type = "DTO"
        else:
            field_type = "Field"

        if field_type == "DTO":
            parent_type_val = parent_type if parent_type else ""
        elif field_type == "Field":
            parent_type_val = "DTO"
        else:
            parent_type_val = ""

        info = {
            "name": field.name,
            "type": field_type.lower(),
            "pic": field.pic or "",
            "length": field.length or 0,
            "value": field.default,
            "parent": parent_name,
            "redefines": field.redefines,
            "all_fillers": False,
            "same_obj":False
        }

        children_info = []
        for child in field.children:
            children_info.extend(self.collect_field_info(child, parent_name=field.name, parent_type=field_type))

        return [info] + children_info