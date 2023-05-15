import csv
from models.models import User


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
        ]
        for user in user_list
    ]
    with open(f"{file_name}", "w", encoding="cp1251", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        for row in data_for_write:
            writer.writerow(row)
