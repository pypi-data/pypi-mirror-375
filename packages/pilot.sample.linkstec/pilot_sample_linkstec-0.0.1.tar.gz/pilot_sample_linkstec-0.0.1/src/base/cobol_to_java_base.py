import json
import os
import re
from operator import indexOf

from base.cobol_java_field import JavaCobolField
from base.get_file_encoding import get_file_encoding
from base.java_code_builder import JavaCodeBuilder
from base.make_cst_java import MakeCstJava


class CobolToJavaBase:
    def __init__(self):
        self.code_builder = JavaCodeBuilder()

    def has_leaf_field(self, field: JavaCobolField) -> bool:
        """
        判断某个字段节点及其子孙是否含有叶子字段(即pic字段非None)
        """
        if field.pic is not None:
            return True
        for child in field.children:
            if self.has_leaf_field(child):
                return True
        return False

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

    # -------- 解析一行COBOL字段 ----------
    def parse_cobol_line(self, line):
        line = line[6:].strip().replace(':Q:-', '')
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

    # -------- 解析整个COBOL文件，建立树 ----------
    def parse_cobol_file(self,  cobol_lines):
        # 创建根节点，层级0，名称为"Root"
        root = JavaCobolField(0, "Root")
        # 用栈结构维护嵌套层级，初始栈中只有根节点
        stack = [root]

        lines = cobol_lines
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
            field = self.parse_cobol_line(line)  # 解析单条COBOL语句，返回CobolField实例
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

    # -------- 生成Java代码 (内部类实现) ---------
    def has_occurs(self, field: JavaCobolField):
        if field.occurs_count > 0:
            return True
        for child in field.children:
            if self.has_occurs(child):
                return True
        return False

    def import_dto_recursive(self,fields_info_list, package_name,
                             parent_name, imported=None, imported_list=None,
                             parent_path_list=None, cache_left=None, cache_right=None):
        cb = JavaCodeBuilder()

        if imported is None:
            imported = set()
        if imported_list is None:
            imported_list = []
        if parent_path_list is None:
            parent_path_list = []
        if cache_left is None:
            cache_left = {}
        if cache_right is None:
            cache_right = {}

        for field in fields_info_list:
            if field.get('parent') == parent_name and field.get('type', '').lower() in ('dto', 'list'):
                current_name_raw = field.get('name')
                current_name = cb.to_camel_case(current_name_raw)

                if current_name in imported:
                    continue

                if not cb.has_leaf_dto(fields_info_list, current_name_raw, cache_left):
                    continue

                if not cb.has_right_child(fields_info_list, current_name_raw, cache_right):
                    continue
                # 新路径累积
                new_path_list = parent_path_list + [current_name]

                # 直接生成完整路径import
                full_path = '.'.join([package_name] + new_path_list)
                import_stmt = f'import {full_path};'
                if import_stmt not in imported_list:
                    imported_list.append(import_stmt)
                    imported.add(current_name)

                # 继续递归
                self.import_dto_recursive(fields_info_list, package_name,
                                     parent_name=current_name_raw,
                                     imported=imported,
                                     imported_list=imported_list,
                                     parent_path_list=new_path_list,
                                     cache_left=cache_left,
                                     cache_right=cache_right)
        return imported_list


    def generate_class_code(self, field: JavaCobolField, package_name, fields_info_list, is_top_level=True):
        # 先判定该字段是否含叶子，没有叶子则不生成class
        if not self.has_leaf_field(field):
            return "", ""  # 直接返回空字符串，跳过生成

        cb = JavaCodeBuilder()
        class_name = cb.to_class_name(field.name).split('.')[0]

        if is_top_level:
            # Javaクラス
            cb.writeln(f"package {package_name};\n")
            for fields_info in fields_info_list:
                if fields_info.get('type') == 'list':
                    cb.writeln("import java.util.List;")
                    cb.writeln("import java.util.ArrayList;\n")
                    break

        # import情報を取得する
        import_package = package_name + '.' + class_name
        imported_list = self.import_dto_recursive(fields_info_list, import_package, 'Root')
        if len(imported_list) > 0:
            for imported_info in imported_list:
                cb.writeln(f"{imported_info}")

        root_member_fields = cb.get_group_root_info(class_name, field, False, True)

        cb.add_inner_class(field, root_member_fields, fields_info_list, False)

        # 代理getter/setter也跳过没有叶子的复合字段
        for child in field.children:
            if child.pic is None:
                if not self.has_leaf_field(child):
                    continue
                field_name = cb.to_field_name(child.name)
                is_list = child.occurs_count is not None and child.occurs_count > 0
                lines = self.generate_proxy_getters_setters(fields_info_list, child, [(field_name, is_list)])
                for line in lines:
                    cb.writeln(line)
        cb.writeln("}\n")
        return class_name, cb.get_code()

    def generate_proxy_getters_setters(self, fields_info_list, parent_field: JavaCobolField,
                                       prefix_chain_with_list_flag=None,
                                       ancestor_is_list=False,
                                       list_redefines_flg=False):
        """
        递归生成代理getter/setter方法，支持多维索引调用。

        :param fields_info_list:
        :param parent_field: 当前字段，JavaCobolField
        :param prefix_chain_with_list_flag: 列表，元素是 (字段名, 是否List)，表示访问链上的字段和是否是List。
        :param ancestor_is_list: 当前节点祖先是否存在List字段，控制是否传递索引参数
        :param list_redefines_flg: 处理redefines相关的标志，影响生成逻辑
        :return: 生成的代码行列表
        """
        if prefix_chain_with_list_flag is None:
            prefix_chain_with_list_flag = []

        lines = []
        cb = self.code_builder  # 假设有code_builder属性，负责命名转换等辅助方法
        current_is_list = parent_field.occurs_count > 0

        for child in parent_field.children:
            if 'FILLER' in child.name:
                continue
            fname = cb.to_field_name(child.name)
            Fname = fname[0].upper() + fname[1:]
            child_is_list = child.occurs_count > 0

            # 继承或生成新的list_redefines_flg标记
            new_list_redefines_flg = list_redefines_flg
            if not list_redefines_flg:
                if (child_is_list and parent_field.redefines is not None) or (
                        child_is_list and child.redefines is not None):
                    new_list_redefines_flg = True

            in_list_context = ancestor_is_list or current_is_list or child_is_list

            # 新的访问链，包含字段名和是否list标志
            new_prefix = prefix_chain_with_list_flag + [(fname, child_is_list)]

            def build_access_call(base="this"):
                call = base
                index_vars = []
                for field_name, is_list in new_prefix[:-1]:  # 跳过最后一个字段（它是目标字段）
                    cap_field = field_name[0].upper() + field_name[1:]
                    call += f".get{cap_field}()"
                    if is_list:
                        idx_var = f"index{len(index_vars)}"
                        call += f".get({idx_var})"
                        index_vars.append(idx_var)
                return call, index_vars, new_prefix[-1][0], new_prefix[-1][1]

            if child.pic is None:
                # 复合字段，内部类
                java_type = cb.to_class_name(child.name)
                getter_call, index_vars, last_field_name, last_is_list = build_access_call()

                cap_last_field = last_field_name[0].upper() + last_field_name[1:]
                cap_last_field_info = cb.get_fields_info('name', cap_last_field, fields_info_list, True)

                if cap_last_field_info.get('type') != 'list':
                    list_type = java_type

                # ==> 新增：拼接形参字符串
                index_params = ", ".join([f"int {v}" for v in index_vars])

                if child_is_list:
                    # 子字段是List，需生成 多重索引 getXxxList / setXxxList + 单元素 getXxx / setXxx

                    # 带索引的方法参数：已有索引 + 额外 index 参数
                    if index_params:
                        method_params_list = index_params + ", int index"
                        method_params_list_1 = index_params
                    else:
                        method_params_list = "int index"
                        method_params_list_1 = method_params_list

                    # getXxxList
                    lines.append(f"    public List<{java_type}> get{cap_last_field}List({method_params_list_1}) " + "{")
                    lines.append(f"        return {getter_call}.get{cap_last_field}();")
                    lines.append(f"    }}")

                    # setXxxList
                    lines.append(
                        f"    public void set{cap_last_field}List(List<{java_type}> {last_field_name}, {method_params_list_1}) " + "{")
                    lines.append(f"        {getter_call}.set{cap_last_field}({last_field_name});")
                    lines.append(f"    }}\n")

                    # getXxx 单元素
                    lines.append(f"    public {java_type} get{cap_last_field}({method_params_list}) " + "{")
                    lines.append(f"        return {getter_call}.get{cap_last_field}().get(index);")
                    lines.append(f"    }}")

                    # setXxx 单元素
                    lines.append(f"    public void set{cap_last_field}({method_params_list}, {java_type} value) " + "{")
                    lines.append(f"        {getter_call}.get{cap_last_field}().set(index, value);")
                    lines.append(f"    }}\n")
                else:
                    # 非List复合字段，根据是否处于list上下文决定是否传索引参数

                    # ==> 改为只要index_params不空就带参数声明
                    if index_params:
                        lines.append(f"    public {java_type} get{cap_last_field}({index_params}) " + "{")
                        lines.append(f"        return {getter_call}.get{cap_last_field}();")
                        lines.append(f"    }}")
                        lines.append(
                            f"    public void set{cap_last_field}({index_params}, {java_type} {last_field_name}) " + "{")
                        lines.append(f"        {getter_call}.set{cap_last_field}({last_field_name});")
                        lines.append(f"    }}\n")
                    else:
                        lines.append(f"    public {java_type} get{cap_last_field}() " + "{")
                        lines.append(f"        return {getter_call}.get{cap_last_field}();")
                        lines.append(f"    }}")
                        lines.append(f"    public void set{cap_last_field}({java_type} {last_field_name}) " + "{")
                        lines.append(f"        {getter_call}.set{cap_last_field}({last_field_name});")
                        lines.append(f"    }}\n")

                # 递归调用生成复合字段的代理方法
                lines.extend(
                    self.generate_proxy_getters_setters(fields_info_list, child, new_prefix, in_list_context, new_list_redefines_flg))

            else:
                # 叶子字段，基础类型处理
                java_type = cb.get_java_type(child)
                list_type = cb.get_List_type(java_type)
                getter_call, index_vars, last_field_name, last_is_list = build_access_call()
                cap_last_field = last_field_name[0].upper() + last_field_name[1:]
                cap_last_field_info = cb.get_fields_info('name',cap_last_field,fields_info_list, True)
                if cap_last_field_info.get('type') != 'list':
                    list_type = java_type
                # ==> 新增：拼接形参字符串
                index_params = ", ".join([f"int {v}" for v in index_vars])

                if current_is_list or ancestor_is_list:
                    if new_list_redefines_flg:
                        if index_params:
                            method_params = index_params + ", int index"
                        else:
                            method_params = "int index"
                        if java_type.lower() in ('string', 'int', 'double', 'long') :
                            lines.append(f"    public {java_type} get{cap_last_field}({method_params}) " + "{")
                            lines.append(f"        return {getter_call}.get{cap_last_field}();")
                            lines.append(f"    }}")
                            lines.append(f"    public void set{cap_last_field}({method_params}, {java_type} value) " + "{")
                            lines.append(f"        {getter_call}.set{cap_last_field}(value);")
                            lines.append(f"    }}\n")
                        else:
                            lines.append(f"    public {java_type} get{cap_last_field}({method_params}) " + "{")
                            lines.append(f"        return {getter_call}.get{cap_last_field}({self.extract_var_names(method_params)});")
                            lines.append(f"    }}")
                            lines.append(f"    public void set{cap_last_field}({method_params}, {java_type} value) " + "{")
                            lines.append(f"        {getter_call}.set{cap_last_field}({self.extract_var_names(method_params)}, value);")
                            lines.append(f"    }}\n")
                    else:
                        if index_params and 'index' in getter_call:
                            lines.append(f"    public {list_type} get{cap_last_field}({index_params}) " + "{")
                        else:
                            lines.append(f"    public {list_type} get{cap_last_field}() " + "{")
                        lines.append(f"        return {getter_call}.get{cap_last_field}();")
                        lines.append(f"    }}")
                        if index_params and 'index' in getter_call:
                            lines.append(f"    public void set{cap_last_field}({index_params} , {list_type} value) " + "{")
                        else:
                            lines.append(f"    public void set{cap_last_field}({list_type} value) " + "{")
                        lines.append(f"        {getter_call}.set{cap_last_field}(value);")
                        lines.append(f"    }}\n")
                elif child.occurs_count > 0:
                    # 同时支持多维访问
                    if index_params:
                        method_params = index_params + ", int index"
                    else:
                        method_params = "int index"

                    # 单个元素访问
                    lines.append(f"    public {java_type} get{cap_last_field}({method_params}) " + "{")
                    lines.append(f"        return {getter_call}.get{cap_last_field}({self.extract_var_names(method_params)});")
                    lines.append(f"    }}")
                    lines.append(f"    public void set{cap_last_field}({method_params}, {java_type} value) " + "{")
                    lines.append(f"        {getter_call}.set{cap_last_field}({self.extract_var_names(method_params)}, value);")
                    lines.append(f"    }}\n")

                    # 整个List访问
                    lines.append(f"    public {list_type} get{cap_last_field}() " + "{")
                    lines.append(f"        return {getter_call}.get{cap_last_field}();")
                    lines.append(f"    }}")
                    lines.append(f"    public void set{cap_last_field}({list_type} value) " + "{")
                    lines.append(f"        {getter_call}.set{cap_last_field}(value);")
                    lines.append(f"    }}\n")
                else:
                    # 普通叶子字段Getter/Setter

                    # ==> 改为只要index_params不空就带参数声明
                    if index_params:
                        lines.append(f"    public {java_type} get{cap_last_field}({index_params}) " + "{")
                    else:
                        lines.append(f"    public {java_type} get{cap_last_field}() " + "{")
                    lines.append(f"        return {getter_call}.get{cap_last_field}();")
                    lines.append(f"    }}")

                    if index_params:
                        lines.append(
                            f"    public void set{cap_last_field}({index_params}, {java_type} {last_field_name}) " + "{")
                    else:
                        lines.append(f"    public void set{cap_last_field}({java_type} {last_field_name}) " + "{")
                    lines.append(f"        {getter_call}.set{cap_last_field}({last_field_name});")
                    lines.append(f"    }}\n")

        return lines

    def extract_var_names(self, param_str):
        pattern = r'\b\w+\s+(\w+)'  # 匹配类型+空白+变量名，提取变量名
        var_names = re.findall(pattern, param_str)
        return ",".join(var_names)

    # -------- 将CobolField递归转dict ----------
    def cobol_field_to_dict(self, field: JavaCobolField):
        """
        递归将 CobolField 转成 dict 以便json序列化
        """
        info = {
            "name": field.name,
            "type": "",
            "pic": field.pic or "",
            "length": field.length or 0,
            "parent": None,
            "redefines": field.redefines
        }
        if field.level == 0 and field.name == "Root":
            field_type = "Root"
        elif field.occurs_count > 0:
            field_type = "List"
        elif field.pic is None:
            field_type = "DTO"
        else:
            field_type = "Field"
        info["type"] = field_type.lower()
        # parent parameter 在递归调用中传入
        return info

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

    # -------- 文件写入 --------
    def write_java_file(self, outdir, class_name, code, file_encoding):
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, f"{class_name}.java")
        with open(path, "w", encoding=file_encoding) as f:
            f.write(code)
        print(f"生成文件：{path}")

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

    def generate_all(self, filepath, package_name, out_file_path, json_file_name = "fields_info.json"):

        # 确保目标输出目录存在，如果不存在则创建
        os.makedirs(out_file_path, exist_ok=True)

        # 自动检测输入文件的编码格式，确保正确读取
        file_encoding = get_file_encoding(filepath)

        # 读取文件所有行，指定编码
        with open(filepath, encoding=file_encoding) as f:
            lines = f.readlines()

        file_name = os.path.basename(filepath).split('.')[0]
        if file_name.upper() in ('PZG10030', 'KRG00002', 'KRG0A002'):
            make_cst_obj = MakeCstJava()
            make_cst_obj.process_cbl_files(file_name, lines, out_file_path)
        else:
            # 解析 Cobol 文件，生成字段树结构的根节点
            root = self.parse_cobol_file(lines)
            # 计算并分配每个字段的偏移量（offset），用于定位字段字节
            self.assign_offsets(root)

            # 调用改进后的 collect_field_info，获取扁平化的字段信息列表
            fields_info_list = self.update_json_item(self.collect_field_info(root))

            # 准备写入字段信息的 JSON 文件路径
            json_path = os.path.join(out_file_path, json_file_name)

            # 将字段信息列表以 JSON 格式写入文件，方便后续查看或调试
            with open(json_path, "w", encoding="utf-8") as json_file:
                json.dump(fields_info_list, json_file, ensure_ascii=False, indent=4)

            # 生成顶层 Java 代码，所有子类定义在顶层类内部
            # 包名顶层修改为 dto + 目录名，方便模块管理

            # 为避免根节点类名是默认的 Root，将其更改为文件名（去扩展名）
            root.name = os.path.splitext(os.path.basename(filepath))[0]

            # 调用生成类代码方法，返回类名和生成的源码字符串
            class_name, code = self.generate_class_code(root, package_name, fields_info_list, is_top_level=True)

            # 将生成的 Java 代码写入对应的文件，指定文件编码
            self.write_java_file(out_file_path, class_name, code, file_encoding)
