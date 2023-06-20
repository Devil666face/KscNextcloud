#!./venv/bin/python
import os
from typing import List
from dotenv import load_dotenv
from models.models import (
    User,
    init_models,
)
from utils.logger import logger
from utils.handler import args
from utils.dump import (
    export_in_csv,
    daily_report,
)
from utils.exec import timer
from api.server import (
    KscServer,
    KscRawData,
)
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

default_report_path = os.getenv("REPORT_PATH", "/var/www/nextcloud/data/32pus/files")


@timer
def iter():
    logger.info("Start to make users")
    User.get_user_list_from_cloud.cache_clear()
    server = KscServer(
        ip=os.getenv("IP", "10.94.177.129"),
        username=os.getenv("USERNAME", "Администратор"),
        password=os.getenv("PASSWORD", "-"),
    )
    computer_list: List[KscRawData] = server.list_of_computer_names()
    not_exist_computer_name_list: List[KscRawData] = [
        host
        for host in computer_list
        if not User.is_computer_exists(computer_name=host.computer_name)
    ]
    init_name_and_password_comp: List[User] = [
        User(computer_name=host.computer_name, ksc_last_date=host.ksc_last_date)
        .autoinit()
        .create_and_save()
        for host in not_exist_computer_name_list
        if User.get_user_type(computer_name=host.computer_name)
        != User.ComputerType.NONE
    ]
    User.update_ksc_last_connect_date(computer_list)
    User.update_nextcloud_last_connect_date()

    # user_list_from_cloud: List[str] = User.get_user_list_from_cloud()
    # unique_user_list: List[User] = [
    #     user
    #     for user in init_name_and_password_comp
    #     if user.username not in user_list_from_cloud
    # ]
    # for user in unique_user_list:
    #     user.save()


if __name__ == "__main__":
    init_models()
    if args.remove:
        logger.info("Delete all data from database.db")
        User.remove_all()
    elif args.write:
        logger.info("Make database dump")
        export_in_csv(file_name="dump.csv")
    elif args.iteration:
        logger.info("Exec only one iteration")
        iter()
    elif args.daemon:
        scheduler = BlockingScheduler()
        background_scheduler = BackgroundScheduler()
        logger.info("Exec in every 60 min daemon mode")
        scheduler.add_job(iter, "interval", minutes=60)
        background_scheduler.add_job(
            daily_report, "interval", hours=12, args=[default_report_path]
        )
        iter()
        background_scheduler.start()
        scheduler.start()
    elif args.report:
        logger.info(
            f"Make today report with last connection dates in {default_report_path}"
        )
        daily_report(default_report_path)
    else:
        logger.error("You dont add options use -h/--help for have info")
