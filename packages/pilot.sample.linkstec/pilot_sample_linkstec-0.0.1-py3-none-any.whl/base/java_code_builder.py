import re
from collections.abc import Iterable

from base.cobol_java_field import JavaCobolField

class JavaCodeBuilder:
    def __init__(self, indent_str="    "):
        """
        初始化Java代码构建器

        :param indent_str: 缩进字符串，默认为4个空格
        """
        self.lines = []              # 存储代码每一行的字符串列表
        self.current_indent = 0      # 当前缩进层级
        self.indent_str = indent_str # 缩进单位字符串

    def indent(self):
        """增加缩进层级"""
        self.current_indent += 1

    def dedent(self):
        """减少缩进层级（确保不小于0）"""
        if self.current_indent > 0:
            self.current_indent -= 1

    def writeln(self, line=""):
        """
        写入一行代码，根据当前缩进自动添加缩进空格

        :param line: 代码行内容，默认空行
        """
        self.lines.append(self.indent_str * self.current_indent + line)

    def get_code(self):
        """
        获取已生成的完整代码字符串

        :return: 多行代码拼接的字符串
        """
        return "\n".join(self.lines)

    def replace_start_number_with_word(self, s):
        # 数字映射表
        num_map = {
            '0': 'zero',
            '1': 'one',
            '2': 'two',
            '3': 'three',
            '4': 'four',
            '5': 'five',
            '6': 'six',
            '7': 'seven',
            '8': 'eight',
            '9': 'nine'
        }

        if not s:
            return s

        # 判断第一个字符是否是数字
        first_char = s[0]
        if first_char in num_map:
            # 用对应英文替换第一个字符
            return num_map[first_char] + s[1:]
        else:
            return s

    # --------- 命名相关工具方法 ---------

    def to_class_name(self, name):
        """
        将字段名转成Java类名格式（首字母大写驼峰）

        :param name: 原始字段名
        :return: 转换后的类名字符串
        """
        parts = re.split(r'[_\-\s]+', self.replace_start_number_with_word(name.lower()))  # 按下划线、短横线、空格分割
        parts = [p.capitalize() for p in parts if p]  # 每部分首字母大写
        return ''.join(parts) if parts else "Field"

    def to_field_name(self, name):
        """
        将字段名转成Java成员变量名格式（首字母小写驼峰）

        :param name: 原始字段名
        :return: 转换后的成员变量名字符串
        """
        if name is None:
            return "field"

        raw = self.replace_start_number_with_word(str(name))

        if '_' not in raw and '-' not in raw:
            # 不包含下划线和横线，首字母小写返回
            return raw.lower() if raw else "field"
        else:
            # 含有分隔符，拆分，首个小写，后续首字母大写驼峰
            parts = re.split(r'[_\-\s]+', raw.lower())
            parts = [p for p in parts if p]  # 过滤空串
            if not parts:
                return "field"
            first = parts[0]
            rest = [p.capitalize() for p in parts[1:]]
            return first + ''.join(rest)

    def to_camel_case(self, name):
        # 将名字转换为小写，并替换开头的数字（假设有对应方法replace_start_number_with_word）
        processed_name = self.replace_start_number_with_word(name.lower())

        if '_' not in name and '-' not in name:
            return name
        # 使用正则表达式以下划线、短横线或空白字符为分隔符拆分字符串
        parts = re.split(r'[_\-\s]+', processed_name)

        # 将拆分出的每个词首字母大写后连接，形成 CamelCase 风格的字符串并返回
        return ''.join(word.capitalize() for word in parts)

    def has_right_child(self, fields_info_list, dto_name, cache=None):
        """
        判断 dto_name 是否有子节点（type是dto或list的右边结构）
        若无，返回False，不生成import
        """
        if cache is None:
            cache = {}
        if dto_name in cache:
            return cache[dto_name]

        # 查找 dto_name 的子节点中 type是dto或者list的节点
        children = [f['name'] for f in fields_info_list
                    if f.get('parent') == dto_name and f.get('type', '').lower() in ('dto', 'list', 'field')]

        if not children:
            cache[dto_name] = False
            return False

        # 递归检查子节点是否至少一个有右边子结构（深层次）
        result = any(self.has_right_child(fields_info_list, c, cache) for c in children)

        cache[dto_name] = True if result else True  # 若只要有子结构就True，这里直接True即可
        return True  # 这里简化：有子dto/list即算有右边结构

    def has_leaf_dto(self, fields_info_list, dto_name, cache=None):
        if cache is None:
            cache = {}
        if dto_name in cache:
            return cache[dto_name]

        children_dtos = [f['name'] for f in fields_info_list if
                         f.get('parent') == dto_name and f.get('type', '').lower() == 'dto']
        if not children_dtos:
            cache[dto_name] = True
            return True
        result = any(self.has_leaf_dto(fields_info_list, child, cache) for child in children_dtos)
        cache[dto_name] = result
        return result

    def get_group_root_info(self, group_name, field, all_fillers_flg, is_top_level:bool= False):
        member_fields = {}
        if field.pic is None:
            self.writeln(f"public class {group_name} {{\n")
            self.indent()

            self.add_field('String', self.to_field_name(group_name))

            self.add_class_method(group_name, field)
            index = 1
            for child in field.children:
                # 过滤掉没有叶子的复合字段，不生成对应字段变量
                if child.pic is None and not self.has_leaf_field(child):
                    continue
                if all_fillers_flg:
                    java_type = self.get_java_type(child)
                    field_name = self.to_field_name(child.name) + str(index)
                    index = index + 1
                else:
                    field_name = self.to_field_name(child.name)
                    if child.occurs_count > 0:
                        if child.pic is None:
                            java_type = f"List<{self.to_class_name(child.name)}>"
                        else:
                            list_type = self.get_List_type(self.get_java_type(child))
                            java_type = list_type
                    else:
                        java_type = self.get_java_type(child)

                member_fields[field_name] = [java_type, child.name, child]
        else:
            if field.occurs_count > 0:
                list_type = self.get_List_type(self.get_java_type(field))
                java_type = list_type
                member_fields[group_name] = [java_type, field.name, field]
            else:
                member_fields[group_name] = [self.get_java_type(field), field.name, field]

        return member_fields

    def get_group_info(self, group_name, field, all_fillers_flg, fields_info_list, is_top_level: bool = False, redefines = None):
        """
        递归生成完整内部类，包括子内部类嵌套。
        返回当前类的字段成员字典，用于构建getter/setter。

        :param group_name: 当前类名
        :param field: 当前层JavaCobolField
        :param all_fillers_flg: 是否全部为填充字段（特殊字段）
        :param fields_info_list:
        :param is_top_level: 是否是顶层，预留
        :return: 当前类的成员字段字典
        """
        member_fields = {}
        redefines_field_info = None
        if redefines is None:
            if field.redefines:
                redefines = field.redefines
                redefines_field_info = self.get_fields_info('name', redefines, fields_info_list)

        if field.pic is None:
            self.writeln(f"public class {group_name} " + "{")
            self.indent()
            field_name = self.to_field_name(field.name)
            field_type = 'String'
            self.add_field(field_type, field_name)
            if all_fillers_flg:
                self.add_class_method_all_fillers(group_name, field)
            else:
                self.add_class_method(group_name, field)
            self.add_getter(field_type, field_name)
            self.add_setter(field_type, field_name)
            index = 1
            for child in field.children:
                if child.pic is None and not self.has_leaf_field(child):
                    # 过滤没有叶子的复合字段，不生成
                    continue

                json_field_info = self.get_fields_info('name', child.name, fields_info_list)
                group_name = json_field_info.get('name')
                group_type = json_field_info.get('type')
                group_is_list = False
                pic_val = json_field_info.get('pic')
                if pic_val is None:
                    if group_type == 'list' :
                        group_is_list = True

                group_length = self.get_group_length_main(field)
                if all_fillers_flg:
                    java_type = self.get_java_type(child)
                    field_name = self.to_field_name(child.name) + str(index)
                    index += 1
                    member_fields[field_name] = [java_type, child.name, child]

                    default_value = self.get_field_default_value(child)

                    self.add_field(java_type, field_name, child, default_value)
                else:
                    field_name = self.to_field_name(child.name)
                    if child.occurs_count > 0:
                        if child.pic is None:
                            # 复合且有OCCURS，是List内部类
                            java_type = f"List<{self.to_class_name(child.name)}>"
                            member_fields[field_name] = [java_type, child.name, child]
                            self.add_field(java_type, field_name, child)
                            self.add_setter(java_type, field_name)
                            self.add_getter(java_type, field_name)
                            # 递归生成内部类定义
                            self.get_group_info(self.to_class_name(child.name), child, all_fillers_flg, fields_info_list, False, redefines)
                        else:
                            if field_name.lower() != 'filler':
                                java_type = self.get_List_type(self.get_java_type(child))
                                member_fields[field_name] = [java_type, child.name, child]
                                method_name = field_name[0].upper() + field_name[1:]+ 'List'
                                self.add_field(java_type, field_name, child)
                                self.add_setter(java_type, field_name, method_name, redefines)
                                self.add_getter(java_type, field_name, method_name, redefines)

                                self.add_field_set_get(field, child, group_name, is_top_level, group_is_list,
                                                    group_length, redefines_field_info)
                    else:
                        if child.pic is None:
                            # 复合单体字段，先定义字段
                            java_type = self.to_class_name(child.name)
                            member_fields[field_name] = [java_type, child.name, child]
                            self.add_field(java_type, field_name, child)
                            # 递归生成子类
                            self.get_group_info(java_type, child, all_fillers_flg, fields_info_list, False, redefines)
                            self.add_setter(java_type, field_name)
                            self.add_getter(java_type, field_name)
                        else:
                            if field_name.lower() != 'filler':
                                #  基础字段，没有子类
                                java_type = self.get_java_type(child)
                                member_fields[field_name] = [java_type, child.name, child]
                                self.add_field(java_type, field_name, child)
                                self.add_field_set_get(field, child, group_name, is_top_level, group_is_list,
                                                        group_length, redefines_field_info)

            self.dedent()
            self.writeln("}\n")
        else:
            if field.name.lower() != 'filler':
                # 基础字段，没有子字段
                if field.occurs_count > 0:
                    java_type = self.get_List_type(self.get_java_type(field))
                    redefines = None
                else:
                    java_type = self.get_java_type(field)
                self.add_field(java_type, field.name, field)
                self.add_setter(java_type, field.name, None, redefines)
                self.add_getter(java_type, field.name, None, redefines)

                member_fields[group_name] = [java_type, field.name, field]

        return member_fields

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

    def get_List_type(self, list_type):
        match list_type:
            case 'String':
                return 'List<String>'
            case 'int':
                return 'List<Integer>'
            case 'double':
                return 'List<Double>'
            case 'long':
                return 'List<Long>'


    def get_java_type(self, field):
        """
        根据CobolField对象确定对应的Java类型字符串

        :param field: CobolField实例
        :return: 对应的Java类型，如String, long, double 或自定义类名
        """
        if field.pic is None:
            # 复合类型使用类名
            return self.to_class_name(field.name)
        is_list_flg = False
        if field.occurs_count > 0:
            is_list_flg = True
        pic = field.pic
        decimal = field.decimal
        comp3 = field.comp3
        field_type = "String"
        if pic == "X" or pic == "G":
            field_type =  "String"
        elif pic == "9":
            if decimal:
                field_type =  "double"
            else:
                # COMP-3时用int，否则用long
                if comp3:
                    field_type = "int"
                else:
                    field_type = "long"
        return field_type

    # --------- List类型字段成员变量和访问器 ---------
    def add_list(self, field: JavaCobolField):
        """
        生成List字段成员变量及getter/setter，并返回构造器中初始化该List的代码字符串

        :param field: CobolField对象，对应OCCURS字段
        :return: 构造器中初始化该List变量的代码行
        """
        fname = self.to_field_name(field.name)
        if field.pic is None:
            java_type = f"List<{self.to_class_name(field.name)}>"  # 复合类型
        else:
            java_type = self.get_List_type(self.get_java_type(field)) # 基本类型集合
        self.add_field(java_type, fname, field)
        self.add_getter(java_type, fname)
        self.add_setter(java_type, fname)
        # 返回构造函数初始化代码(调用方需插入构造函数)
        return f"this.{fname} = new ArrayList<>({field.occurs_count});"

    def get_java_default_value(self, field: JavaCobolField):
        if field.default is None:
            return None
        # 处理基础类型
        java_type = self.get_java_type(field)
        val = field.default

        if 'SPACE' in val.strip().upper():
            val = ''

        if 'ZERO' in val.strip().upper():
            val = 0

        if java_type == "String":
            # 字符串类型，加双引号，转义等
            escaped_val = str(val).replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped_val}"'
        elif java_type == "double":
            try:
                float(val)  # 校验可转换
                # 保证有小数点（加上d结尾可选）
                return val if ('.' in val or 'e' in val.lower()) else val + ".0"
            except Exception:
                return "0.0"
        elif java_type in ("int", "long"):
            try:
                int(val)
                return val
            except Exception:
                return "0"
        else:
            # 其他类型默认不设置默认值
            return None

    def add_class_method_all_fillers(self, method_name, main_field_info):
        self.writeln(f"public {method_name}() {{")
        self.indent()
        field_name = self.to_field_name(main_field_info.name)

        # self.add_field("String", field_name)

        self.writeln(f"StringBuilder sb = new StringBuilder();")

        for filler_info in main_field_info.children:
            filler_type = self.get_java_type(filler_info)
            filler_len = filler_info.length
            filler_val = self.pad_default_value(filler_type, filler_len, filler_info.default)
            self.writeln(f"sb.append(String.valueOf(\"{filler_val}\"));")
        self.writeln(f"{field_name} = sb.toString();")
        self.dedent()
        self.writeln("}\n")

    def pad_default_value(self, field_type, field_length, default_value):
        """
        根据字段类型、字段长度和默认值，补足默认值长度。

        参数:
        - field_type: str, 字段类型，比如 "string"、"array"、"int"、"long"、"float"
        - field_length: int, 字段长度
        - default_value: 默认值，类型根据field_type不同可以是str、list或数值等

        返回:
        - 补足长度后的值，string类型返回string，array返回list，数字类型返回string（方便长度控制）
        """

        if field_type.lower() == "string":
            default_value = "" if default_value is None else str(default_value)
            if len(default_value) < field_length:
                return default_value.ljust(field_length, ' ')
            else:
                return default_value[:field_length]

        elif field_type.lower() == "array":
            if default_value is None:
                default_value = []
            elif isinstance(default_value, str):
                default_value = list(default_value)

            if len(default_value) < field_length:
                pad_len = field_length - len(default_value)
                return ['0'] * pad_len + default_value
            else:
                return default_value[-field_length:]

        elif field_type.lower() in ["int", "long", "float", "double"]:
            # 把默认值转成字符串
            if default_value is None:
                default_str = ""
            else:
                default_str = str(default_value)
            # 如果是float，保留小数点，按字符串长度处理
            if len(default_str) < field_length:
                return default_str.rjust(field_length, '0')
            else:
                # 超长截取右边部分
                return default_str[-field_length:]

        else:
            # 其他类型，直接转换成字符串左补空格（可根据需求修改）
            default_value = "" if default_value is None else str(default_value)
            if len(default_value) < field_length:
                return default_value.ljust(field_length, ' ')
            else:
                return default_value[:field_length]

    def add_class_method(self, method_name, main_field_info,redefines_flg:bool = False):

        if redefines_flg:
            redefines_name = self.to_field_name(main_field_info.name)
            self.writeln(f"private String {redefines_name};")
            self.writeln(f"public {method_name}(String val) {{")
            self.writeln(f"    {redefines_name} = val;")
        else:
            self.writeln(f"public {method_name}() {{")
        self.get_default_value(main_field_info)
        self.writeln("")
        for field_info in main_field_info.children:
            if field_info.pic is None and len(field_info.children) > 0:
                class_name = self.to_class_name(field_info.name)
                field_name = self.to_field_name(field_info.name)
                self.writeln(f"{class_name} {field_name} = new {class_name}();")
        self.dedent()
        self.writeln("}\n")

    def get_field_default_value(self, field: JavaCobolField):
        if field.default is None:
            return None
        # 处理基础类型
        java_type = self.get_java_type(field)
        val = field.default

        if 'SPACE' in val.strip().upper():
            val = ''

        if 'ZERO' in val.strip().upper():
            val = 0

        if java_type == "String":
            # 字符串类型，加双引号，转义等
            escaped_val = str(val).replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped_val}"'
        elif java_type == "double":
            try:
                float(val)  # 校验可转换
                # 保证有小数点（加上d结尾可选）
                return val if ('.' in val or 'e' in val.lower()) else val + ".0"
            except Exception:
                return "0.0"
        elif java_type in ("int", "long"):
            try:
                int(val)
                return val
            except Exception:
                return "0"
        else:
            # 其他类型默认不设置默认值
            return None

    def add_list_obj(self, index, child_name):
        obj_name = self.to_field_name(child_name) + str(index)
        obj_class_name = self.to_class_name(child_name)

        return f"{obj_class_name} {obj_name}= new {obj_class_name}({index});"

    def get_fields_info(self, field_type ,key, fields_info_list, main_flg:bool = False):
        if not isinstance(fields_info_list, Iterable):
            return None

        for fields_info in fields_info_list:
            if not main_flg:
                if fields_info.get(field_type) == key:
                    return fields_info
            else:
                if self.to_camel_case(fields_info.get(field_type)) == key:
                    return fields_info

    def get_field_begin_end_index(self, group_info, field_info):
        field_name = field_info.name
        begin_index = 0
        end_index = 0
        if isinstance(group_info, list):
            iterable = group_info
        else:
            iterable = getattr(group_info, 'children', [])

        for field_info_loop in iterable:
            if field_info_loop.name == field_name:
                if field_info_loop.occurs_count > 0:
                    end_index = begin_index + field_info_loop.occurs_count * int(field_info_loop.length)
                else:
                    end_index = begin_index  + int(field_info_loop.length)
                break
            else:
                if field_info_loop.occurs_count > 0:
                    begin_index = begin_index + field_info_loop.occurs_count * int(field_info_loop.length)
                else:
                    begin_index = begin_index + int(field_info_loop.length)
        return begin_index, end_index

    def get_group_begin_end_index(self,parent_info,current_group_info):
        group_name = current_group_info.name

        group_begin_index = 0
        group_end_index = 0
        for group_or_field_info in parent_info.children:
            if group_or_field_info.pic is None:
                group_length = self.get_group_length_main(group_or_field_info)
            else:
                if group_or_field_info.occurs_count > 0:
                    group_length = group_or_field_info.occurs_count * group_or_field_info.length
                else:
                    group_length = group_or_field_info.length
            if group_or_field_info.name == group_name:
                group_end_index = group_begin_index + group_length
                break
            else:
                group_begin_index = group_begin_index + group_length

        return group_begin_index, group_end_index


    def get_default_value(self, group_info):
        group_name = self.to_field_name(group_info.name)
        group_length = self.get_group_length_main(group_info)
        self.writeln(f"StringBuilder sb = new StringBuilder();")
        self.writeln(f"for (int i = 0; i < {group_length}; i++) {{")
        self.indent()
        self.writeln(f"sb.append(\" \");")
        self.dedent()
        self.writeln("}")
        self.writeln(f"this.{group_name} = sb.toString();")
        self.dedent()

    def get_group_length_main(self, group_info):
        group_length = self.get_group_length(group_info)

        if group_info.occurs_count > 0:
            return group_info.occurs_count * group_length
        else:
            return group_length

    def get_group_length(self, group_info) -> int:
        """
        計算一個 COBOL group（包括所有子 group、occurs）的總長度。

        - `group_info` 必須是具有 `children`、`pic`、`length`、`occurs_count`
          屬性的物件（通常是 `JavaCobolField`）。
        - 回傳值為 **字節數**（或字符數），已經把所有 OCCURS 乘算在內。
        """
        total_len = 0

        for field in group_info.children:
            # -------------------------------------------------
            # 1️⃣ 子 group（沒有 PIC，代表是另一個 DTO)
            # -------------------------------------------------
            if field.pic is None:  # 這是一個 group
                sub_len = self.get_group_length(field)  # 先算子 group 本身的長度
                if field.occurs_count and field.occurs_count > 0:
                    # 子 group 本身也可能有 OCCURS
                    total_len += sub_len * int(field.occurs_count)
                else:
                    total_len += sub_len
                continue

            # -------------------------------------------------
            # 2️⃣ 基本欄位（有 PIC）
            # -------------------------------------------------
            base_len = int(field.length)  # 單個實例的長度
            if field.occurs_count and field.occurs_count > 0:
                total_len += base_len * int(field.occurs_count)
            else:
                total_len += base_len

        return total_len

    def change_redefines_field(self, field):
        if field is None:
            _redefines_field = field
        else:
            _redefines_field = self.to_field_name(field)

        return _redefines_field[0].upper() + _redefines_field[1:]

    def string_to_other(self, field_type):
        match field_type:
            case "String":
                return 'new String'
            case "int":
                return 'Integer.parseInt'
            case "long":
                return 'Long.parseLong'
            case 'double':
                return 'Double.parseDouble'

    def camel_to_kebab(self, s):
        # 在小写字母和大写字母之间插入 -
        s1 = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s)
        # 全部转小写
        return s1.upper()

    def add_inner_class(self, parent_info, member_fields_arr, fields_info_list, redefines_flg:bool, is_top_level=True,
                        group_is_list:bool = False, group_length:int = 0):
        for field_name, field_info in member_fields_arr.items():
            field_name_cbl = field_info[1]
            fields_info = field_info[2]
            class_name = self.to_class_name(field_name_cbl)
            json_field_info = self.get_fields_info('name', field_name_cbl, fields_info_list)
            all_fillers_flg = json_field_info['all_fillers']
            if fields_info.pic is None:
                if len(fields_info.children) > 0:
                    if fields_info.occurs_count > 0 :
                        group_is_list = True
                        group_length = self.get_group_length_main(fields_info)
                    else:
                        group_is_list = False
                        group_length = 0
                    self.add_group_set_get(field_name, is_top_level, group_is_list, fields_info)
                    self.get_group_info(class_name, fields_info, all_fillers_flg, fields_info_list)
            else:
                if fields_info.name != 'FILLER':
                    field_default_value = self.get_field_default_value(fields_info)
                    field_type = self.get_java_type(fields_info)
                    field_name = self.to_field_name(fields_info.name)
                    redefines = fields_info.redefines
                    self.add_field(field_type, field_name, fields_info, field_default_value)
                    self.add_getter(field_type, field_name,None, redefines)
                    self.add_setter(field_type, field_name,None, redefines)

    def add_group_set_get(self, group_name , is_top_level, group_is_list, fields_info):
        if group_is_list:
            group_type = f"List<{group_name[0].upper() + group_name[1:]}>"
        else:
            group_type = group_name[0].upper() + group_name[1:]
        if is_top_level:
            self.add_field(group_type, group_name, fields_info)
        self.add_getter(group_type, group_name)
        self.add_setter(group_type, group_name)

    def add_field_set_get(self,parent_info, fields_info, group_name, is_top_level, group_is_list, group_length, redefines):

        field_default_value = self.get_field_default_value(fields_info)
        field_type = self.get_java_type(fields_info)
        field_name = self.to_field_name(fields_info.name)

        if is_top_level:
            self.add_field(field_type, field_name, fields_info, field_default_value)
            self.add_getter(field_type, field_name)
            self.add_setter(field_type, field_name)
        else:
            redefines_flg = False
            redefines_method_get = None
            redefines_method_set = None
            if redefines:
                redefines_flg = True
                redefines_method_set, redefines_method_get = self.get_redefines_method(redefines)

            field_begin_index, field_end_index = self.get_field_begin_end_index(parent_info.children, fields_info)
            self.add_getter_group(field_begin_index, field_end_index, parent_info, fields_info, field_type, field_name,
                                  group_is_list, group_length, redefines_method_get, redefines_flg)
            self.add_setter_group(field_begin_index, field_end_index, parent_info, fields_info, field_type, field_name,
                                  group_is_list, group_length, redefines_method_set, redefines_flg)


# --------- 成员变量及getter/setter生成 ---------
    def add_field(self, java_type, name, field= None, default_value=None):
        """
        生成成员变量定义行，支持默认值

        :param field:
        :param java_type: Java类型字符串
        :param name: 变量名
        :param default_value: 成员变量的默认值字符串（可选）
        """
        if default_value is not None:
            self.writeln(f"private {java_type} {name} = {default_value};")
        else:
            if 'List' in java_type:
                self.writeln(f"private {java_type} {name} = new ArrayList<>({field.occurs_count});")
            else:
                self.writeln(f"private {java_type} {name};")

    def add_getter(self, java_type, field_name, method_name:str = None, redefines:str =None):
        """
        生成标准的getter方法

        :param java_type: 返回类型
        :param field_name: 字段名（成员变量名）
        """
        if method_name is None:
            method_name = field_name[0].upper() + field_name[1:]
        self.writeln(f"public {java_type} get{method_name}() {{")
        self.indent()
        self.writeln(f"return this.{field_name};")
        self.dedent()
        self.writeln("}")

    def add_setter(self, java_type, field_name, method_name:str = None , redefines:str =None):
        """
        生成标准的setter方法

        :param java_type: 参数类型
        :param field_name: 字段名（成员变量名）
        """
        redefines_method = ''
        if method_name is None:
            method_name = field_name[0].upper() + field_name[1:]
        if redefines:
            redefines_method = self.to_camel_case(redefines)
        self.writeln(f"public void set{method_name}({java_type} {field_name}) {{")
        self.indent()
        self.writeln(f"this.{field_name} = {field_name};")
        if redefines and 'List' not in java_type:
            self.writeln(f"set{redefines_method}(this.{field_name});")
        self.dedent()
        self.writeln("}")

    def add_getter_group(self, field_begin_index, field_end_index, parent_info, fields_info, field_type, field_name,
                         group_is_list, group_length, redefines_method_get, redefines_flg:bool = False):
        group_name = self.to_field_name(parent_info.name)
        method_name = field_name[0].upper() + field_name[1:]
        return_field_type = self.string_to_other(field_type)
        if group_is_list:
            if fields_info.occurs_count >0:

                field_length = fields_info.length
                self.writeln(f"public {field_type} get{method_name}(int indexArr, int indexObj) {{")
                self.indent()
                self.writeln(
                    f"return {return_field_type} "
                    f"({group_name}."
                    f"substring({field_begin_index}, {field_begin_index} "
                    f"+ ( indexArr + 1 ) * {group_length} + ( indexObj + 1 ) * {field_length}));")
                self.dedent()
                self.writeln("}\n")
            else:
                self.writeln(f"public {field_type} get{method_name}(int index) {{")
                self.indent()
                self.writeln(f"return {return_field_type} "
                             f"({group_name}."
                             f"substring({field_begin_index},"
                             f" {field_begin_index} + ( index + 1 ) *{group_length}));")
                self.dedent()
                self.writeln("}\n")
        else:
            if fields_info.occurs_count >0:
                list_type = self.get_List_type(field_type)
                self.writeln(f"public {list_type} get{method_name}() {{")
                self.indent()
                self.writeln(
                    f"return this.{field_name};")
                self.dedent()
                self.writeln("}\n")
                field_length = fields_info.length
                self.writeln(f"public {field_type} get{method_name}(int index) {{")
                self.indent()
                self.writeln(
                    f"return {return_field_type} ({group_name}.substring({field_begin_index}, {field_begin_index} + ( index + 1 ) * {field_length}));")
                self.dedent()
                self.writeln("}\n")
            else:
                self.writeln(f"public {field_type} get{method_name}() {{")
                self.indent()
                self.writeln(f"return {return_field_type} ({group_name}.substring({field_begin_index}, {field_end_index}));")
                self.dedent()
                self.writeln("}\n")

    def add_setter_group(self, field_begin_index, field_end_index, parent_info, fields_info, field_type, field_name,
                         group_is_list, group_length, redefines_method_set, redefines_flg:bool = False):

        method_name = field_name[0].upper() + field_name[1:]
        parent_str_name = self.to_field_name(parent_info.name)
        if group_is_list:
            field_length = fields_info.length
            if fields_info.occurs_count > 0:
                self.writeln(f"public void set{method_name}(int indexArr, int indexObj,{field_type} val) {{")
                self.indent()
                self.writeln(f"if ({parent_str_name} == null) {{")
                self.indent()
                self.writeln(f"{parent_str_name} = \"\";")  # 如果null，先初始化为空字符串
                self.dedent()
                self.writeln("}")
                self.writeln(f"StringBuilder sb = new StringBuilder({parent_str_name});")
                self.writeln(f"while (sb.length() < {field_end_index}) {{")
                self.indent()
                self.writeln("sb.append(\" \");")  # 用空格扩充字符串长度，保证可以替换
                self.dedent()
                self.writeln("}")
                self.writeln(
                    f"sb.replace({field_begin_index} + indexArr * {group_length} + indexObj * {field_length}, {field_begin_index} + indexArr * {group_length} + indexObj * {field_length} + ( indexObj + 1 ) * {field_length}, String.valueOf(val));")  # 替换对应子字符串
                if redefines_flg:
                    self.writeln(f"{parent_str_name} = sb.toString();")  # 重新赋值给父字符串字段
                else:
                    self.writeln(f"{parent_str_name} = sb.toString();")  # 重新赋值给父字符串字段

                self.dedent()
                self.writeln("}\n")
            else:
                self.writeln(f"public void set{method_name}(int indexArr, {field_type} val) {{")
                self.indent()
                self.writeln(f"if ({parent_str_name} == null) {{")
                self.indent()
                self.writeln(f"{parent_str_name} = \"\";")  # 如果null，先初始化为空字符串
                self.dedent()
                self.writeln("}")
                self.writeln(f"StringBuilder sb = new StringBuilder({parent_str_name});")
                self.writeln(f"while (sb.length() < {field_end_index}) {{")
                self.indent()
                self.writeln("sb.append(\" \");")  # 用空格扩充字符串长度，保证可以替换
                self.dedent()
                self.writeln("}")
                self.writeln(f"sb.replace((indexArr + 1) * {group_length} + {field_begin_index}, (indexArr + 1) * {group_length} + {field_begin_index} + {field_length}, String.valueOf(val));")  # 替换对应子字符串
                if redefines_flg:
                    self.writeln(f"{redefines_method_set}(sb.toString());")  # 重新赋值给父字符串字段
                    self.writeln(f"{parent_str_name} = sb.toString();")  # 重新赋值给父字符串字段
                else:
                    self.writeln(f"{parent_str_name} = sb.toString();")  # 重新赋值给父字符串字段

                self.dedent()
                self.writeln("}\n")
        else:
            if fields_info.occurs_count >0:
                list_type = self.get_List_type(field_type)

                self.writeln(f"public void set{method_name}({list_type} val) {{")
                self.indent()
                self.writeln(
                    f"this.{field_name} = val;")
                self.dedent()
                self.writeln("}\n")
                field_length = fields_info.length
                self.writeln(f"public void set{method_name}(int index,{field_type} val) {{")
                self.indent()
                self.writeln(f"if ({parent_str_name} == null) {{")
                self.indent()
                self.writeln(f"{parent_str_name} = \"\";")  # 如果null，先初始化为空字符串
                self.dedent()
                self.writeln("}")
                self.writeln(f"StringBuilder sb = new StringBuilder({parent_str_name});")
                self.writeln(f"while (sb.length() < {field_end_index}) {{")
                self.indent()
                self.writeln("sb.append(\" \");")  # 用空格扩充字符串长度，保证可以替换
                self.dedent()
                self.writeln("}")
                self.writeln(f"sb.replace({field_begin_index} + index * {field_length}, {field_begin_index} + ( index + 1 ) * {field_length}, String.valueOf(val));")  # 替换对应子字符串
                if redefines_flg:
                    self.writeln(f"{parent_str_name} = sb.toString();")  # 重新赋值给父字符串字段
                else:
                    self.writeln(f"{parent_str_name} = sb.toString();")  # 重新赋值给父字符串字段

                self.dedent()
                self.writeln("}\n")
            else:
                self.writeln(f"public void set{method_name}({field_type} val) {{")
                self.indent()
                self.writeln(f"if ({parent_str_name} == null) {{")
                self.indent()
                self.writeln(f"{parent_str_name} = \"\";")  # 如果null，先初始化为空字符串
                self.dedent()
                self.writeln("}")
                self.writeln(f"StringBuilder sb = new StringBuilder({parent_str_name});")
                self.writeln(f"while (sb.length() < {field_end_index}) {{")
                self.indent()
                self.writeln("sb.append(\" \");")  # 用空格扩充字符串长度，保证可以替换
                self.dedent()
                self.writeln("}")
                self.writeln(f"sb.replace({field_begin_index}, {field_end_index}, String.valueOf(val));")  # 替换对应子字符串
                if redefines_flg:
                    self.writeln(f"{redefines_method_set}(sb.toString());")  # 重新赋值给父字符串字段
                    self.writeln(f"{parent_str_name} = sb.toString();")  # 重新赋值给父字符串字段
                else:
                    self.writeln(f"{parent_str_name} = sb.toString();")  # 重新赋值给父字符串字段
                self.dedent()
                self.writeln("}\n")

    def get_redefines_method(self, redefines_field):
        redefines_field_name = redefines_field.get('name')
        redefines_field_type = redefines_field.get('pic')
        method_name = self.to_camel_case(redefines_field_name)
        if redefines_field_type is None or redefines_field_type == '':
            redefines_class = self.to_field_name(redefines_field_name) + '.'
        else:
            redefines_class = ''
        redefines_method_name_set = f"{redefines_class}set{method_name}"
        redefines_method_name_get = f"{redefines_class}get{method_name}"

        return redefines_method_name_set, redefines_method_name_get