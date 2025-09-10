# pytest: disable=collection
import ast


class CodeHelper():  # noqa: F401
    def __init__(self, code: str, stdout: str):
        self.code = code
        self.stdout = stdout

    def var(self, var_name: str, expected_value, msg=None):
        """
        Проверяет, что в переданном Python-коде переменной `var_name` присвоено ожидаемое значение `expected_value`.

        Функция парсит код с помощью модуля `ast`, ищет все присваивания переменной
        `var_name` и проверяет соответствие последнего присвоенного значения ожидаемому.
        Пробелы удаляются перед сравнением.

        Args:
            code (str):
                Строка с Python-кодом, который будет анализироваться.
            var_name (str):
                Имя переменной, значение которой нужно проверить.
            expected_value (any):
                Ожидаемое значение переменной. Может быть числом, строкой, списком и т.д.
                Для строк пробелы игнорируются при сравнении.
            msg (str, optional):
                Сообщение об ошибке, которое будет возвращено, если значение переменной
                не соответствует ожидаемому. Если None (по умолчанию), формируется
                стандартное сообщение.

        Returns:
            bool | str | SyntaxError:
                * True — если переменной присвоено ожидаемое значение.
                * str — сообщение об ошибке, если переменная не объявлена или
                  её значение не соответствует ожидаемому.
                * SyntaxError — если переданный код содержит синтаксическую ошибку.

        Examples:
            >>> var("x = 10", "x", 10)
            True

            >>> var("x = 1\\nx = 2", "x", 1)
            'Переменной `x` было переписвоено значение 2, ожидалось 1'

            >>> var("y = 'hello'", "z", "hello")
            'Переменная `z` не объявлена'

            >>> var("x = pd.DataFrame([1,2,3])", "x", "pd.DataFrame([1,2,3])")
            True
        """

        try:
            tree = ast.parse(self.code)
        except SyntaxError as err:
            return err

        assignments = {}

        # Парсим переменную
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == var_name:
                        try:
                            assignments[var_name] = ast.literal_eval(node.value)   
                            if isinstance(assignments[var_name], str):
                                assignments[var_name] = assignments[var_name].replace(" ", "")
                        except Exception:
                            assignments[var_name] = ast.unparse(node.value).replace(" ", "")

        # print(assignments.get(var_name, None))

        # Готовим expected
        if isinstance(expected_value, str):
            strip_expected_value = expected_value.replace(" ", "")
        else:
            strip_expected_value = expected_value

        if var_name not in assignments:
            return f"Переменная `{var_name}` не объявлена"
        if assignments[var_name] != strip_expected_value:
            return msg or f"Переменной `{var_name}` было переписвоено значение {assignments[var_name]}, ожидалось {expected_value}"
        else:
            return True

    def call(self, func_name: str, expected_args=None, msg=None):
        """
        Проверяет, что в переданном коде есть вызов указанной функции
        с ожидаемыми позиционными и/или именованными аргументами.

        Функция разбирает Python-код с помощью модуля `ast`, ищет последний вызов функции,
        сравнивает фактические аргументы вызова с ожидаемыми и возвращает
        результат проверки.

        Args:
            code (str):
                Строка с Python-кодом, который будет анализироваться.
            func_name (str):
                Имя функции, вызов которой нужно проверить.
            expected_args (list | None, optional):
                Список ожидаемых аргументов. Может содержать:
                    * строковые литералы или выражения для позиционных аргументов,
                    * кортежи вида (имя_аргумента, значение) для именованных аргументов,
                    * числа и другие литералы.
                Пробелы внутри строк удаляются автоматически.
                Если None (по умолчанию), то проверяется только сам факт вызова функции.
            msg (str | None, optional):
                Сообщение об ошибке, которое будет возвращено в случае
                несоответствия. Если None (по умолчанию), формируется стандартное сообщение.

        Returns:
            bool | str | SyntaxError:
                * True — если функция вызвана с ожидаемыми аргументами
                  (или если `expected_args` не переданы и вызов найден).
                * str — сообщение об ошибке (если функция не найдена или аргументы не совпадают).
                * SyntaxError — если переданный код содержит синтаксическую ошибку.

        Examples:
            >>> call("print(123, sep='\\t')", "print", [123, ("sep", "\\t")])
            True

            >>> call("print(123)", "print", [123, ("sep", "\\t")])
            'Функция `print` вызвана с аргументами [123], ожидаются [123, ("sep", "\\t")]'

            >>> call("x = 1", "print")
            'Не найден вызов функции `print`'

            >>> call("print(123, end=var)", "print", [("end", "var")])
            True
        """

        try:
            tree = ast.parse(self.code)
        except SyntaxError as err:
            return err

        # Вспомогательная функция:
        # из любого node (Attribute / Call / Subscript / Name)
        # собирает "цепочку" имён слева направо
        def extract_chain(node):
            if isinstance(node, ast.Attribute):
                return extract_chain(node.value) + [node.attr]
            if isinstance(node, ast.Subscript):
                return extract_chain(node.value)
            if isinstance(node, ast.Call):
                return extract_chain(node.func)
            if isinstance(node, ast.Name):
                return [node.id]
            try:
                return [ast.unparse(node)]
            except Exception:
                return []

        # Все включения функции
        candidates = []  # список (node, chain, full)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                chain = extract_chain(node.func)
                if chain and (chain[-1] == func_name or ".".join(chain).endswith(func_name)):
                    candidates.append((node, chain, ".".join(chain)))
            elif isinstance(node, ast.Attribute):
                chain = extract_chain(node)
                if chain and (chain[-1] == func_name or ".".join(chain).endswith(func_name)):
                    candidates.append((node, chain, ".".join(chain)))

        if not candidates:
            return msg or f"Не найден вызов функции `{func_name}`"

        # Если аргументы не нужны — достаточно факта наличия
        if expected_args is None:
            return True

        # Проверяем каждый кандидат, ищем совпадение
        for node, chain, full in candidates:
            if not isinstance(node, ast.Call):
                # нашли только атрибут без вызова → пропускаем
                continue

            # Отдельно обрабатываем позиционные и именованные аргументы
            pos_args, kw_args = [], []
            for arg in node.args:
                try:
                    val = ast.literal_eval(arg)
                    if isinstance(val, str):
                        val = val.replace(" ", "")
                except Exception:
                    val = ast.unparse(arg).replace(" ", "")
                pos_args.append(val)

            for kw in node.keywords:
                try:
                    val = ast.literal_eval(kw.value)
                    if isinstance(val, str):
                        val = val.replace(" ", "")
                except Exception:
                    val = ast.unparse(kw.value).replace(" ", "")
                kw_args.append((kw.arg, val))

            combined = pos_args + kw_args

            norm_expected = []
            for a in expected_args:
                if isinstance(a, str):
                    norm_expected.append(a.replace(" ", ""))
                elif isinstance(a, (list, tuple)) and len(a) == 2:
                    name, val = a
                    if isinstance(val, str):
                        val = val.replace(" ", "")
                    norm_expected.append((name, val))
                else:
                    norm_expected.append(a)

            if set(norm_expected).issubset(set(combined)):
                return True

        # Если ни один кандидат не подошёл
        return msg or f"Функция `{func_name}` вызвана с аргументами {combined}, ожидаются {expected_args}"

    def output(self, expected_output: str, include=None, msg=None):
        """
        Проверяет, что строковый вывод функции соответствует ожидаемому.
        Предназначено для проверки вывода после print().

        Args:
            actual_output (str): Строка, полученная после print().
            expected_output (str): Ожидаемый вывод в виде строки.
            include (bool, optional): Условие на строгое соотвествие вывода или частичное включение
            msg (str, optional): Сообщение об ошибке, если вывод отличается.

        Returns:
            bool | str: True, если вывод совпадает; иначе сообщение об ошибке.
        """
        actual_str = "\n".join([line.strip() for line in self.stdout.splitlines() if line.strip()])
        expected_str = "\n".join([line.strip() for line in expected_output.splitlines() if line.strip()])

        if actual_str == expected_str and include is None:
            return True
        elif expected_str in actual_str and include is True:
            return True
        else:
            return msg or f"Фактический вывод: {actual_str}, ожидается: {expected_str}"

    def contains(self, expected_code: str, msg: str = None):
        """
        Проверяет, что в коде студента есть определённая подстрока
        """
        actual_str = "\n".join([line.strip() for line in self.code.splitlines() if line.strip()]).replace(" ", "").replace("\"", "'")
        expected_str = "\n".join([line.strip() for line in expected_code.splitlines() if line.strip()]).replace(" ", "").replace("\"", "'")

        if expected_str not in actual_str:
            return msg or f"Ожидается {expected_code}"

        return True

# Обратная совместимость - оставляем алиас
TestHelper = CodeHelper
