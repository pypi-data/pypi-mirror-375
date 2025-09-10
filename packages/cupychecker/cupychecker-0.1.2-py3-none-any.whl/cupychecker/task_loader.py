import os
import yaml
import requests


def load_local(module: str, task: str):
    """
    Получение встроенного списка проверок для задачи в формате YAML из пакета cupychecker
    """

    path = os.path.join(
        os.path.dirname(__file__),
        "exercises",
        "modules",
        f"module_{module}",
        "tasks",
        f"task_{task}.yaml")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_remote(module: str, task: str, host: str):
    """
    Получение списка проверок для задачи в формате YAML с сервера
    """
    
    endpoint = "/task_checks"

    response = requests.get(
        host + endpoint,
        params={
            "module": module,
            "task": task
        }
    )

    return response.json().get("data")


def load_from_str(task_conf_str: str):
    """
    Парсинг YAML из строки
    """
    
    return yaml.safe_load(task_conf_str)

