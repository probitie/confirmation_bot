from project import *


@dataclass
class Student:
    """
    обьект для хранения данных о юзере

    пока что просто для хранения имени / пароля
    """
    login: str
    password: str


if __name__ == '__main__':
    s = Student('', '')
    print()
