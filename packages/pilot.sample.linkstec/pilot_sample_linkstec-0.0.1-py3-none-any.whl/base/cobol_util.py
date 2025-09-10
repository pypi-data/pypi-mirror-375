import re
from typing import Dict, List, Tuple

def pic_to_java_type(pic: str) -> Tuple[str, bool]:
    pic = pic.upper()
    if pic.startswith("X"):
        return "String", False
    if pic.startswith('G'):
        return 'String', False
    if pic.startswith("S9") or "V" in pic:
        return "BigDecimal", True
    if pic.startswith("9"):
        m = re.search(r"9\((\d+)\)", pic)
        length = int(m.group(1)) if m else 0
        return ("long", False) if length > 9 else ("int", False)
    return "String", False

def to_java_const_name(cobol_name: str) -> str:
    return cobol_name.replace("-", "_").upper()

def get_fields_info(field_type ,key, fields_info_list, main_flg:bool = False):
    for fields_info in fields_info_list:
        if not main_flg:
            if fields_info.get(field_type) == key:
                return fields_info
        else:
            if to_camel_case(fields_info.get(field_type)) == key:
                return fields_info

def to_camel_case(name):
    # 将名字转换为小写，并替换开头的数字（假设有对应方法replace_start_number_with_word）
    processed_name = replace_start_number_with_word(name.lower())

    # 使用正则表达式以下划线、短横线或空白字符为分隔符拆分字符串
    parts = re.split(r'[_\-\s]+', processed_name)

    # 将拆分出的每个词首字母大写后连接，形成 CamelCase 风格的字符串并返回
    return ''.join(word.capitalize() for word in parts)

def replace_start_number_with_word(s):
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