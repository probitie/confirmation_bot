from selenium.webdriver.remote.remote_connection import LOGGER

from project import *

from project.student import Student


class NureDriver(webdriver.Chrome):
    """
    Оболочка для хром вебдрайвера для удобного доступа к сайту
    """

    DLNURE_LOGIN_URL = "https://dl.nure.ua/login/index.php"

    def __init__(self):

        # установление настроек для вебдрайвера
        options = webdriver.ChromeOptions()
        cap = DesiredCapabilities.CHROME.copy()

        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")

        logging.debug("Options and capabilities are enabled")

        # перед инициализацией драйвера повышаем уровень логгера селениума - чтобы он не засорял вывод
        LOGGER.setLevel(logging.WARNING)

        super().__init__(ChromeDriverManager(log_level=logging.CRITICAL).install(), options=options, desired_capabilities=cap)

        logging.debug("NureDriver is initialised")
        logging.info("Browser is opened")

    def log_into_nure(self, student: Student) -> None:
        """вход на аккаунт в дл нуре"""
        self._open_dlnure()

        logging.info("enter student login and password")

        self._type_login(student.login)
        self._type_password(student.password)
        self._press_button_to_log_in()

    def _open_dlnure(self):
        """ открывает страницу dlnure """
        logging.debug("Open dlnure page")
        self.get(self.DLNURE_LOGIN_URL)
        logging.debug("Dlnure page is opened")

    def _type_login(self, login: str) -> None:
        """Вводит логин студента в поле на странице логина"""

        logging.debug("enter login to input tag")

        self._sleep()
        input_line = WebDriverWait(self, 5).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR,
                                        'input[id="username"]')))

        input_line.send_keys(login)

    def _type_password(self, password: str) -> None:
        """Вводит пароль студента в поле на странице логина"""
        logging.debug("enter password to input tag")

        self._sleep()
        input_line = WebDriverWait(self, 5).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR,
                                        'input[id="password"]')))

        input_line.send_keys(password)

    def _select_checkbox(self) -> None:
        """ ОТКЛЮЧЕН - должен нажимать на чекбокс 'запомнить имя юзера' """
        # <input type="checkbox" name="rememberusername" id="rememberusername" value="1">

    def _press_button_to_log_in(self) -> None:
        """нажимает на кнопку отправки формы с логином и паролем для авторизации"""
        # "btn btn-primary btn-block mt-3" id="loginbtn">Вход</button>
        logging.debug("click to confirm authorisation")

        self._sleep()
        btn = WebDriverWait(self, 5).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR,
                                        'button[id="loginbtn"]')))
        btn.click()

    @staticmethod
    def _sleep() -> None:
        time.sleep(0.5)  # для того, чтобы действия методов были больше похожи на действия человека


if __name__ == '__main__':
    pass
