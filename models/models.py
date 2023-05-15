import re
from enum import Enum
from typing import (
    List,
    Any,
    Callable,
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
from utils.exec import (
    exec_command,
    exec_command_return,
)
from utils.logger import logger
from functools import lru_cache
from datetime import datetime

default_occ_prefix = "sudo -u www-data php /var/www/nextcloud/occ "
default_group = "MSIO"

db = SqliteDatabase("database.db")


class EnumField(CharField):
    def __init__(self, choices: Callable, *args: Any, **kwargs: Any) -> None:
        super(CharField, self).__init__(*args, **kwargs)
        self.choices = choices
        self.max_length = 255

    def db_value(self, value: Any) -> Any:
        return value.value

    def python_value(self, value: Any) -> Any:
        return self.choices(type(list(self.choices)[0].value)(value))


def get_user_list(user_string: str) -> List[str]:
    user_list: List[str] = list()
    for user_line in user_string.strip().split("\n"):
        left_side = re.split(r":", user_line)[0]
        for word in re.split(r"\s", left_side):
            if word not in ["", "-"]:
                user_list.append(word)
    return user_list


class User(Model):
    class ComputerType(Enum):
        AQUARIUS = "Aquarius Cmp"
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
    ksc_last_date = DateTimeField(default=datetime.fromtimestamp(0))

    class Meta:
        database = db

    @staticmethod
    def is_computer_exists(computer_name: str) -> bool:
        user = User.select().where(User.computer_name == computer_name)
        if user.exists():
            if user[0].is_user_already_make:
                logger.error(f"User {user[0].username} is already make")
                return True
            else:
                return False
            return True
        return False

    @staticmethod
    def is_user_have_in_nextcloud(username: str) -> bool:
        user_list = User.get_user_list_from_cloud()
        if user_list == False:
            return False
        if username in user_list:
            logger.error(f"User {username} is have in nextcloud base")
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
        user_list: List[str] = get_user_list(user_string)
        return user_list

    def save(self, force_insert: bool = ..., only=...):
        if self.is_user_have_in_nextcloud(username=str(self.username)):
            logger.error(f"User {self.username} is already make")
            return
        self.make_user()
        try:
            return super().save()
        except IntegrityError as ex:
            logger.exception(
                f"User {self.username} already have in database and nextcloud is duplicate user. Make somthing with this.\n{ex}"
            )
            duplicated_user = User.select().where(User.username == self.username)
            if duplicated_user.exists():
                user = duplicated_user[0]
                user.is_user_already_make = True
                user.save()

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


def init_models() -> None:
    db.create_tables([User])
