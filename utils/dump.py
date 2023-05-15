import csv
from pathlib import Path
from datetime import datetime
from typing import List
from models.models import User, default_occ_prefix
from utils.exec import exec_command
from utils.logger import logger


def export_in_csv(file_name: str) -> None:
    user_list = User.select()
    data_for_write = [
        [
            user.computer_name,
            user.username,
            user.password,
            user.user_type,
            user.is_user_already_make,
            user.ksc_last_date,
            user.nextcloud_last_date,
        ]
        for user in user_list
    ]
    write(file_name, data_for_write)


def daily_report(default_file_prefix: str) -> None:
    logger.debug(f"Start to make report")
    file_name: Path = Path(default_file_prefix) / f"{strfdate(datetime.now())}.csv"
    user_list = User.select()
    data_for_write = [
        [
            user.computer_name,
            user.username,
            user.ksc_last_date,
            user.nextcloud_last_date,
        ]
        for user in user_list
    ]
    write(str(file_name), data_for_write)
    rescan_nextcloud_dir(default_file_prefix)


def write(file_name: str, data_for_write: List[List[str]]) -> None:
    with open(f"{file_name}", "w", encoding="cp1251", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        for row in data_for_write:
            writer.writerow(row)


def strfdate(date: datetime, format: str = "%Y%m%d") -> str:
    try:
        return date.strftime(format)
    except AttributeError:
        return str(date)


def rescan_nextcloud_dir(scan_path: str) -> None:
    username: str = Path(scan_path).parent.stem
    command = f"{default_occ_prefix} files:scan {username}"
    user_string = exec_command(command)
