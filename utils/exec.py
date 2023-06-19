import re
import subprocess
from utils.logger import logger
from typing import List, Literal
from datetime import date, datetime
from time import perf_counter
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        try:
            result = func(*args, **kwargs)
        except KeyboardInterrupt:
            logger.info("Exit from keyboard")
            exit(0)
        end_time = perf_counter()
        logger.debug(f"Iteration time {end_time - start_time:.07f} seconds")
        return result

    return wrapper


def exec_command(command: str) -> bool:
    result = subprocess.Popen(
        command,
        shell=True,
    )
    result.wait()
    if result.returncode == 0:
        return True
    return False


def exec_command_return(command: str) -> str | bool:
    result = subprocess.Popen(
        command,
        shell=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    result.wait()
    if result.returncode == 0:
        return result.stdout.read()
    return False


def parse_user_list(user_string: str) -> List[str]:
    user_list: List[str] = list()
    for user_line in user_string.strip().split("\n"):
        left_side = re.split(r":", user_line)[0]
        for word in re.split(r"\s", left_side):
            if word not in ["", "-"]:
                user_list.append(word)
    return user_list


def parse_user_info(user_info_string: str) -> "datetime" | Literal[False]:
    if re.findall(r"has never logged in, yet", user_info_string):
        return False
    if re.findall(r"last login", user_info_string):
        string_date = re.split(r"last login: ", user_info_string)[-1]
        return datetime.strptime(string_date.strip(), "%d.%m.%Y %H:%M")
