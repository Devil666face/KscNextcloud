from enum import Enum
from models.enum import EnumField
from typing import (
    List,
    Annotated,
    Literal,
    Tuple,
)
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    IntegerField,
    BooleanField,
    TextField,
    IntegrityError,
    DateTimeField,
)
from api.server import KscRawData
from utils.exec import (
    exec_command,
    exec_command_return,
    parse_user_list,
    parse_user_info,
)
from utils.logger import logger
from functools import lru_cache
from datetime import datetime

default_occ_prefix = "sudo -u www-data php /var/www/nextcloud/occ "
default_group = "MSIO"

db = SqliteDatabase("database.db")


class User(Model):
    class ComputerType(Enum):
        AQUARIUS = "Aquarius Cmp"
        XIAOMI = "Xiaomi"
        OBT = "OBT"
        HIGHTON = "HightonElectronics"
        MIG = "MIG"
        RTAB = "RTAB-910"
        ULEFON = "Ulefone Power Armor"
        NONE = "NONE"

    id = IntegerField(primary_key=True)
    computer_name = CharField(default=None, unique=True)
    username = CharField(default=None, unique=True)
    password = CharField(default=None)
    user_type = EnumField(null=False, choices=ComputerType)
    is_user_already_make = BooleanField(default=False)
    ksc_last_date = DateTimeField(
        default=datetime.fromtimestamp(0), formats=["%d.%m.%Y %H:%M"]
    )
    nextcloud_last_date = DateTimeField(
        default=datetime.fromtimestamp(0), formats=["%d.%m.%Y %H:%M"]
    )

    class Meta:
        database = db

    @staticmethod
    def is_computer_exists(computer_name: str) -> bool:
        user = User.select().where(User.computer_name == computer_name)
        if user.exists():
            if user[0].is_user_already_make:
                logger.info(f"User {user[0].username} is already make")
                return True
            else:
                return False
            return True
        return False

    def is_user_have_in_nextcloud(self, username: str) -> bool:
        user_list = User.get_user_list_from_cloud()
        if user_list == False:
            return False
        if username in user_list:
            logger.debug(f"User {username} is have in nextcloud base")
            return True
        return False

    @staticmethod
    @lru_cache(maxsize=None)
    def get_user_list_from_cloud() -> List[str] | Literal[False]:
        command = f"{default_occ_prefix} user:list"
        user_string = exec_command_return(command)
        if user_string == False:
            logger.error(f"Not get user from nexcloud base")
            return False
        user_list: List[str] = parse_user_list(user_string)
        return user_list

    def is_user_have_in_base(self, computer_name: str) -> bool:
        record = User.select().where(User.computer_name == computer_name)
        if record.exists() and record[0].is_user_already_make:
            return True
        return False

    def exception_for_user_is_exists_in_nextcloud(self) -> bool:
        duplicated_user = User.select().where(User.username == self.username)
        if duplicated_user.exists():
            user = duplicated_user[0]
            user.is_user_already_make = True
            user.save()
            return True
        self.is_user_already_make = True
        self.save()
        return False

    def create_and_save(self) -> None | bool:
        if self.is_user_have_in_nextcloud(
            username=str(self.username)
        ) and self.is_user_have_in_base(str(self.computer_name)):
            logger.error(f"Dont create user {self.username} is already make")
            return
        if self.make_user():
            try:
                return self.save()
            except IntegrityError as ex:
                logger.error(
                    f"User {self.username} already have in database and nextcloud is duplicate user."
                )
                return self.exception_for_user_is_exists_in_nextcloud()
        else:
            return self.exception_for_user_is_exists_in_nextcloud()

    def make_user(self) -> bool:
        command = f'echo -e "{self.password}\n{self.password}" | {default_occ_prefix} user:add --group="{default_group}" {self.username}'
        if exec_command(command):
            self.is_user_already_make = True
            logger.success(
                f"Successfull make user {self.username} for computer {self.computer_name}"
            )
            return True
        return False

    def autoinit(self) -> "User":
        self.user_type = self.get_user_type(computer_name=str(self.computer_name))
        self.username, self.password = self.get_username_and_password(self.user_type)
        logger.debug(
            f"comp={self.computer_name}, username={self.username}, password={self.password}, type={self.user_type}"
        )
        return self

    def __str__(self) -> str:
        param_list: List[str] = [
            f"{key}:{value}"
            for key, value in zip(
                self.__dict__["__data__"], self.__dict__["__data__"].values()
            )
        ]
        return "\n".join(param_list)

    @staticmethod
    def get_user_type(
        computer_name: str,
    ) -> Annotated[ComputerType, "Return Type of computer"]:
        for comp_type in User.ComputerType:
            if str(computer_name).find(comp_type.value) != -1:
                if (
                    comp_type == User.ComputerType.AQUARIUS
                    and computer_name.find("_") == -1
                ):
                    """This check for username Aquarius CMP NS208R 0000000000078"""
                    return User.ComputerType.NONE
                return comp_type
        return User.ComputerType.NONE

    def get_username_and_password(
        self, user_type: Annotated[ComputerType, "Type of computer"]
    ) -> tuple[str, str]:
        uniq_user_password = str(self.computer_name).split()[-1]
        len_line = len(uniq_user_password)
        if user_type == User.ComputerType.AQUARIUS:
            username = str(uniq_user_password.split("_")[0])[-6:len_line]
            password = str(uniq_user_password.split("_")[1])[-8:len_line]
        else:
            username = uniq_user_password[0:6]
            password = uniq_user_password[6:len_line]
        return (username, password)

    @staticmethod
    def remove_all() -> None:
        for user in User.select():
            logger.debug(f"Delete {user.computer_name}")
            user.delete().execute()

    @staticmethod
    def update_ksc_last_connect_date(computer_list: List[KscRawData]) -> None:
        logger.debug("Update ksc last connection dates")
        for host in computer_list:
            User.update({User.ksc_last_date: host.ksc_last_date}).where(
                User.computer_name == host.computer_name
            ).execute()

    @staticmethod
    def update_nextcloud_last_connect_date() -> None:
        def get_user_info(username: str) -> "datetime":
            command = f"{default_occ_prefix} user:lastseen {user.username}"
            user_info_raw_string = exec_command_return(command)
            if not user_info_raw_string:
                return
            return parse_user_info(user_info_raw_string)

        for user in User.select():
            date: datetime | Literal[False] = get_user_info(user.username)
            if not date:
                continue
            logger.debug(
                f"Last connection in nextcloud for {user.computer_name} - {date}"
            )
            User.update({User.nextcloud_last_date: date}).where(
                User.computer_name == user.computer_name
            ).execute()


def init_models() -> None:
    db.create_tables([User])
