import requests

from .helpers import TestHelper


def run_code(code, host='http://localhost:8000'):
    """
    Запуск кода на Runner
    """
    endpoint = '/run'
    response = requests.post(
        host + endpoint,
        json={
            'code': f'{code}'
        }
    )
    response.raise_for_status()

    return response.json()


def check_result(code: str, stdout: str, task_conf: dict, host=None):
    """
    Проверка результата
    """
    
    _test = TestHelper(code=code, stdout=stdout)

    # Итеративно выполняем каждую проверку
    for check in task_conf.get('checks'):
        if 'message' in check:
            message = check['message']
        else:
            message = None

        if check['type'] == 'var':
            result = _test.var(
                var_name=check['expected']['var'],
                expected_value=check['expected']['value'],
                msg=message
            )

        if check['type'] == "call":
            if 'args' in check['expected']:
                expected_args = check['expected']['args']
            else:
                expected_args = None
            result = _test.call(
                func_name=check['expected']['func'],
                expected_args=expected_args,
                msg=message
            )

        elif check['type'] == "output":
            if 'include' in check['expected']:
                include = check['expected']['include']
            else:
                include = None
            result = _test.output(
                expected_output=check['expected']['stdout'],
                include=include,
                msg=message
            )

        elif check['type'] == "contains":
            result = _test.contains(
                expected_code=check['expected']['code'],
                msg=message
            )

        if result is not True:
            return result

    return True

