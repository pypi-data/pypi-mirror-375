import re
import json

class MethodFieldChange:
    # Javaコードの変換を行うクラス。JobBaseを継承し、抽象基底クラスとして定義。

    def load_work_mapping(self, json_filepath, json_encoding):
        # JSONファイルを指定されたエンコーディングで読み込み、マッピング辞書を作成する。
        with open(json_filepath, 'r', encoding=json_encoding) as f:
            mapping_list = json.load(f)

        return mapping_list

    def to_pascal_case(self, s):
        # 文字列をパスカルケース（大文字で始まるキャメルケース）に変換する。
        return ''.join(word.capitalize() for word in s.lower().split('_'))

    def to_camel_case(self, name, capitalize_first=False):
        # 将COBOL字段名转换为驼峰命名
        # 支持首字母大写（用于类名）或小写（用于字段名）
        # 处理特殊字符如-替换为空格，再拼接驼峰

        name = name.replace(':Q:-', '').replace('-', ' ').replace('$', ' ')
        parts = name.strip().split()
        if not parts:
            return "field" if not capitalize_first else "Field"
        camel = parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
        if capitalize_first:
            camel = camel[0].upper() + camel[1:] + "Dto"
        return camel

    def is_skip_var(self, var_name):
        # 変換処理をスキップすべき変数名か判定（"CNT"または"IDX"で始まる場合）。
        return var_name.startswith("CNT") or var_name.startswith("IDX")

    def extract_parentheses_content(self, copy_mapping, s):
        m = re.search(r'([$\[])(.*?)[$\]]', s)
        if m:
            # 返回括号内的内容，去掉空格后按逗号分割成列表
            content = m.group(2)
            items = [item.strip() for item in content.split(',')]
            change_items = []
            for item in items:
                obj, field, list_flg = self.transform_var(copy_mapping,
                                                                    item)
                if obj is not None and field is not None:
                    change_items.append(obj+'.get'+field+'()')

            if len(change_items) > 0:
                return change_items
            return items
        return []

    def transform_var(self, copy_mapping, var_name):

        var_name = var_name.replace('-', '_')
        if self.is_skip_var(var_name):
            return var_name, None, False

        if '(' in var_name:
            var_name = var_name.split('(')[0]
        mapped_obj = self.find_key_by_value_contains(copy_mapping, var_name, 'name')

        if not mapped_obj:
            return None, None, False
        elif var_name.startswith("CST_"):
            return self.to_camel_case(mapped_obj), var_name, False
        else:
            return self.to_camel_case(mapped_obj), self.to_pascal_case(var_name), False

    def replace_line(self, copy_mapping, line):
        # 1行のコードを受け取り、変換した結果を返す。
        # インデントを除去して保存
        prefix_spaces = ''
        m = re.match(r'^(\s*)', line)
        if m:
            prefix_spaces = m.group(1)
        trimmed_line = line[len(prefix_spaces):]

        # 空行の場合はそのまま返す
        if not trimmed_line.strip():
            return line

        # 1. 多行コメントの開始/終了は外部処理のためここでは無視

        # 2. メソッド宣言行のメソッド名を小駝峰式に変換
        method_decl_pattern = re.compile(
            r'^((?:public|private|protected|static|final|abstract|synchronized|native)\s*)*'  # 修飾子群（空白はオプション）
            r'\s*(void|int|String|boolean|double|float|char|long|short|byte|var)'  # 戻り値タイプ
            r'\s+([A-Z0-9_]+)\s*'  # メソッド名（大文字・数字・アンダースコア）
            r'\([^)]*\)'  # 引数リスト
            r'\s*{'  # 開括弧 `{` の前に空白を許可
        )

        method_match = method_decl_pattern.match(trimmed_line)
        if method_match:
            modifiers = method_match.group(1) or ''  # 修飾子。Noneの場合は空文字に。
            ret_type = method_match.group(2)
            method_name = method_match.group(3)

            modifiers = modifiers.rstrip()  # 末尾の空白除去

            new_method_name = self.to_camel_case(method_name)  # 小駝峰式に変換

            # 元の行からメソッド名の後ろを取得（引数部分と"{")
            idx = trimmed_line.find(method_name) + len(method_name)
            remainder = trimmed_line[idx:]

            # 変換後の行を構成
            parts = []
            if modifiers:
                parts.append(modifiers)
            parts.append(ret_type)
            parts.append(new_method_name)
            parts.append(remainder)
            # 修飾子と戻り値は空白で連結し、メソッド名以下はそのまま連結
            return prefix_spaces + ' '.join(parts[:2]) + ' ' + parts[2] + parts[3]

        # 3. 代入文の処理（=があり、==は除外）
        if ' = ' in trimmed_line and '==' not in trimmed_line and 'for' not in trimmed_line:
            left_side, right_side = trimmed_line.split('=', 1)
            left_side = left_side.strip()
            right_side = right_side.strip()

            has_semicolon = right_side.endswith(';')
            if has_semicolon:
                right_side = right_side[:-1].rstrip()

            left_side_list = []
            right_side_list = []
            if '(' in left_side and ')' in left_side and '.' not in left_side and not left_side.startswith("("):
                left_side_list = self.extract_parentheses_content(copy_mapping, left_side)

            if '[' in left_side:
                left_side_list = self.extract_parentheses_content(copy_mapping, left_side)

            left_obj, left_field , list_flg= self.transform_var(copy_mapping, left_side)

            # 右辺の式の変数も変換処理にかける
            right_index = None
            if '[' in right_side:
                right_side_list = self.extract_parentheses_content(copy_mapping, right_side)
                right_index = right_side_list[0]
            else:
                right_index = ''
            right_transformed = self.transform_right_expr(copy_mapping, right_side, right_index)
            left_part_str = None
            if left_field is not None and left_field != '':
                if '(' in left_field:
                    left_part_str = left_field.split('(')[0]

                if '[' in left_field:
                    left_part_str = left_field.split('[')[0]

                if len(right_side_list) > 0:
                    pos = right_transformed.rfind('(')
                    right_list_index = right_side_list[0]
                    if len(right_side_list) > 1:
                        right_begin_index = int(right_side_list[1].strip()) - 1
                        right_end_index = right_begin_index + int(right_side_list[2].strip())
                        right_transformed = right_transformed[:pos].rstrip().split('.')[0] + 'get('+ right_list_index + ').' + right_transformed[:pos].rstrip().split('.')[1] + 'substring(' +  str(right_begin_index) + ',' + str(right_end_index) + ')'

                # セッター呼び出し形式に変換
                if len(left_side_list) > 0:
                    if len(left_side_list) == 1:
                        return f"{prefix_spaces}{left_obj}.set{left_part_str}({left_side_list[0]} , {right_transformed});"
                    else:
                        list_index = left_side_list[0]
                        begin_index = int(left_side_list[1].strip()) - 1
                        end_index = begin_index + int(left_side_list[2].strip())
                        return f"{prefix_spaces}{left_obj}.get{left_part_str}().replace({begin_index},{end_index},{right_transformed});"
                else:
                    return f"{prefix_spaces}{left_obj}.set{left_field}({right_transformed});"
            elif right_transformed is not None and right_transformed != '':
                if right_transformed == '1' and  left_side.startswith('IDX'):
                    return  'int ' + left_side + ' = 0 ;'
                return  prefix_spaces + left_side + ' = ' + right_transformed + ' ;'
            else:
                # セッター変換なしは元の行を返す
                return line

        # 4. 代入文以外の行は変数名をゲッター呼び出し形式に変換（CNT/IDXは除外）
        result = []
        var_buffer = ''
        i = 0
        length = len(trimmed_line)

        def flush_var_buffer(buf, peek_next_chars):
            # バッファ内の単語をゲッター形式に変換して返す
            if not buf:
                return ''
            if self.is_skip_var(buf):
                return buf
            # list_flg = False
            obj, field , list_flg= self.transform_var(copy_mapping, buf)
            if field is not None:
                if field != '':
                    if 'CST' in field:
                        return f"{obj}.{field}"
                    else:
                        if '[' in peek_next_chars:
                            index_list = self.extract_parentheses_content(copy_mapping, peek_next_chars)
                            index_inside = index_list[0]
                            return f"{obj}.get{field}({index_inside})"
                        else:
                            return f"{obj}.get{field}()"
                else:
                    return obj
            else:
                return buf

        while i < length:
            c = trimmed_line[i]

            if c.isalnum() or c == '_':
                var_buffer += c
                i += 1
                if i == length:
                    result.append(flush_var_buffer(var_buffer, ''))
                    var_buffer = ''
            else:
                if var_buffer:
                    peek = self.extract_next_bracket_content(trimmed_line, i)
                    if peek and peek.startswith('['):
                        result.append(flush_var_buffer(var_buffer, peek))
                        var_buffer = ''
                        i += len(peek)
                        continue
                    else:
                        result.append(flush_var_buffer(var_buffer, ''))
                        var_buffer = ''
                result.append(c)
                i += 1
        if var_buffer:
            result.append(flush_var_buffer(var_buffer, ''))

        return prefix_spaces + ''.join(result)

    def extract_next_bracket_content(self, s, start_index):
        if start_index >= len(s):
            return ''
        if s[start_index] not in ('[', '('):
            return ''
        open_char = s[start_index]
        close_char = ']' if open_char == '[' else ')'
        stack = 1
        end = start_index + 1
        while end < len(s) and stack > 0:
            if s[end] == open_char:
                stack += 1
            elif s[end] == close_char:
                stack -= 1
            end += 1
        if stack == 0:
            return s[start_index:end]
        return ''

    def replace_dash(self, s):
        # 只替换左右都是字母或下划线的'-'
        pattern = r'(?<!\s)-(?!\s)'
        return re.sub(pattern, '_', s)

    def process_java_code(self, mapping_data, java_code):
        # Javaコードの全文を受け取り、行単位で変換し結合して返す
        output = []
        in_block_comment = False  # /* */ コメント内かどうかの状態管理
        for line_java in java_code:
            if line_java.strip() == '':
                continue
            line = self.replace_dash(line_java)
            if in_block_comment:
                output.append(line)
                if '*/' in line:
                    in_block_comment = False  # コメント終了検出
                continue

            if '/*' in line:
                start_idx = line.find('/*')
                end_idx = line.find('*/', start_idx + 2)
                if end_idx == -1:
                    # 開始のみで終了なしはブロックコメント開始として状態維持
                    in_block_comment = True
                    output.append(line)
                    continue
                else:
                    # 1行で終わるブロックコメントはそのまま出力
                    output.append(line)
                    continue

            # 単一行コメント（//）の処理。コード部とコメント部を分離し、コード部のみ変換
            if '//' in line:
                comment_pos = line.find('//')
                code_part = line[:comment_pos]
                comment_part = line[comment_pos:]
                transformed_code_part = self.replace_line(mapping_data, code_part)
                output.append(transformed_code_part + comment_part)
                continue

            # その他コード行を変換
            transformed_line = self.replace_line(mapping_data, line)
            output.append(transformed_line)

        return output

    def transform_right_expr(self, copy_mapping, expr, right_index):
        if '[' in expr:
            expr = expr.split('[')[0]

        # 1. token正则支持变量、数字、字符串、操作符和符号
        token_pattern = re.compile(
            r'([A-Za-z_][A-Za-z0-9_]*)'  # 变量名和方法名，支持大写小写和数字、下划线
            r'|(\d+)'  # 数字
            r'|("(?:\\.|[^"\\])*")'  # 双引号字符串，支持转义
            r"|('(?:\\.|[^'\\])*')"  # 单引号字符串，支持转义
            r'|(==|!=|<=|>=|&&|\|\|)'  # 操作符
            r'|([^\s\w])'  # 单个符号（点、括号、逗号等）
        )

        tokens = []
        pos = 0
        length = len(expr)

        while pos < length:
            m = token_pattern.match(expr, pos)
            if not m:
                # 不匹配任何token时，直接把当前字符作为单独token
                tokens.append(expr[pos])
                pos += 1
                continue
            # 分组只会匹配一项，依次判断加入tokens
            tok = next(filter(lambda x: x is not None, m.groups()))
            tokens.append(tok)
            pos = m.end()

        result = []
        i = 0
        n = len(tokens)

        while i < n:
            token = tokens[i]
            # 如果是变量名
            if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', token):
                # 判断后续是不是点号紧跟方法调用 (链式调用)
                # 例: var.method(
                j = i + 1
                chain = token
                while j + 1 < n and tokens[j] == '.' and re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', tokens[j + 1]):
                    chain += '.' + tokens[j + 1]
                    j += 2
                # 如果后面紧跟括号，是方法调用，整体不转换变量名，只转换第一个变量名
                if j < n and tokens[j] == '(':
                    # chain 是 类似 var.method.method2
                    # chain拆成第一部分变量名和剩余方法链
                    parts = chain.split('.', 1)
                    first_var = parts[0]
                    rest = '.' + parts[1] if len(parts) > 1 else ''

                    # 先对第一个变量名调用transform_var 转换成getter表达式
                    obj, field, list_flg = self.transform_var(copy_mapping, first_var)
                    if field is not None and field != '':
                        if 'CST' in field.upper():
                            prefix = f"{obj}.{field}"
                        else:
                            prefix = f"{obj}.get{field}({right_index})"
                    elif field == '':
                        prefix = obj
                    else:
                        prefix = first_var

                    # 还原方法链和后续token直到匹配结束括号
                    # 找寻配对的括号区域，简单扫描（这里假设括号匹配正确）
                    end_pos = j
                    stack = 1
                    while end_pos + 1 < n and stack > 0:
                        end_pos += 1
                        if tokens[end_pos] == '(':
                            stack += 1
                        elif tokens[end_pos] == ')':
                            stack -= 1
                    # 拼接括号内及之后所有token
                    method_call = ''.join(tokens[j:end_pos + 1])

                    result.append(prefix + rest + method_call)
                    i = end_pos + 1
                    continue
                else:
                    # 没有方法调用，则调用transform_var转换为getter调用
                    obj, field, list_flg = self.transform_var(copy_mapping, token)
                    if field is not None and field != '':
                        if 'CST' in field.upper():
                            result.append(f"{obj}.{field}")
                        else:
                            if right_index is not None:
                                result.append(f"{obj}.get{field}({right_index})")
                            else:
                                result.append(f"{obj}.get{field}()")
                    elif field == '':
                        result.append(obj)
                    else:
                        result.append(token)
                    i += 1
            else:
                # 字符串、数字、操作符、标点符号 直接加入
                result.append(token)
                i += 1

        # 右边代码中token不插入额外空格，直接拼接，避免出现不必要空格
        return ''.join(result)

    def find_key_by_value_contains(self, map_data, target_value, field_type):
        target_value_edit = target_value.replace('_', '-')
        for key, dict_list in map_data.items():
            # dict_list 应该是列表，里面元素是字典
            for d in dict_list:
                if isinstance(d, dict) and d.get(field_type) == target_value_edit:
                    return key
        return None  # 没找到


