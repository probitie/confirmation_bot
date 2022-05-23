from project import *
from project.driver import NureDriver


class PresenceConfirmation:
    """
    Подтверждает присутствие на парах

    """

    COURSES_URL = "https://dl.nure.ua/my/"

    def __init__(self, nure_driver: NureDriver):
        """"""
        self.nure_driver = nure_driver
        self._visits_urls = self._get_visits_urls()

        logging.debug("PresenceConfirmation is running")

    def confirm(self) -> List[str]:
        """
        Подтверждает присутствие на парах

        Проходит по всем ссылкам на курсы, и пытается отметиться

        :return: ссылки на предметы, на которых отметиться удалось
        """

        confirmed_urls = list(filter(self._confirm_presence, self._visits_urls))  # применяю подтверждения ко всем ссылкам посещений
        # длина confirmed_urls всегда должна быть равна
        # 1 (пара была отмечена)
        # либо 0 (нет пар, на которых нужно отметиться в данный момент)
        # если длина больше 1 - значит что за 1 раз было отмечено больше 1 пары - это по сути невозможно

        confirmed_urls_length = len(confirmed_urls)
        if confirmed_urls_length > 1:
            logging.critical(f"length of confirmed urls is {confirmed_urls_length}, expected 1 or 0")
        elif confirmed_urls_length == 0:
            logging.info("There isn`t any pair to confirm")

        return confirmed_urls

    def _get_visits_urls(self) -> List[str]:
        """
        Возвращает все ссылки на страницы посещений

        переходит на страницу личного кабинета, выбирает текущие курсы,
        и далее полчает ссылки на сами курсы, потом на посещения
        """

        self._open_courses_page()

        self._select_current_courses()

        courses = self._pick_up_courses_urls()

        visits = self._pick_up_visits_urls(courses)

        return visits

    def _pick_up_courses_urls(self) -> List[str]:
        """Собирает ссылки на курсы"""
        elements = self._get_courses_elements()

        def find_url_in_elem(el: WebElement) -> str:
            """находит ссылку на курс из вебэлемента курса"""
            a = WebDriverWait(el, 5).until(
                ec.presence_of_element_located((By.CSS_SELECTOR,
                                                'a[class="aalink coursename mr-2"]')))
            return a.get_attribute("href")

        urls = list(map(find_url_in_elem, elements))

        logging.debug(f"visits urls amount is {len(urls)}")
        return urls

    def _get_courses_elements(self) -> List[WebElement]:
        """Возвращает список из вебэлементов каждого курса"""

        card_deck = WebDriverWait(self.nure_driver, 5).until(
            ec.presence_of_element_located((By.CSS_SELECTOR,
                                            'div[class="card-deck dashboard-card-deck "]')))

        cards = WebDriverWait(card_deck, 5).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                 'div[class="card dashboard-card"]')))

        logging.debug(f"courses amount is {len(cards)}")
        return cards

    def _pick_up_visits_urls(self, courses_urls: List[str]) -> List[str]:
        """Возвращает ссылки на страницы посещений по переданым ссылкам на курсы """

        urls = list(map(self._pick_up_visits_url, courses_urls))
        return urls

    def _pick_up_visits_url(self, courses_url: str) -> str:
        """Возвращает ссылку на страницу посещений по переданой ссылке на курс"""
        self.nure_driver.get(courses_url)

        # TODO divs / visits_div = find div in divs where div.text = "Відвідування"
        divs = WebDriverWait(self.nure_driver, 5).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                 'div[class="activityinstance"]')))

        visits_div = filter(lambda div: "Відвідування" in div.text, divs).__next__()

        visits_a = visits_div.find_element_by_tag_name('a')
        visits_url = visits_a.get_attribute("href")

        logging.debug(f"visits url is {visits_url}")
        return visits_url

    def _select_current_courses(self):
        """В выпадающем меню выбирает '(показать) текущие курсы' """

        drop_down_button = WebDriverWait(self.nure_driver, 2).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR,
                                        'button[id="groupingdropdown"]')))
        # открытие меню
        drop_down_button.click()

        drop_down_list = WebDriverWait(self.nure_driver, 2).until(
            ec.presence_of_element_located((By.CSS_SELECTOR,
                                            'ul[class="dropdown-menu show"]')))

        li_items = WebDriverWait(drop_down_list, 2).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                 'li')))
        # 4 li списка - это кнопка с фильтром 'Текущие'
        select_current = li_items[3]

        select_current.click()

        logging.debug("current courses is selected")

    def _open_courses_page(self):
        """Открывает страницу с расписанием"""
        self.nure_driver.get(self.COURSES_URL)
        logging.debug("courses page is opened")

    def _confirm_presence(self, url: str) -> bool:
        """
        подтверждает присутствие по переданой ссылке

        возвращает True, если отметиться удалось - иначе False
        """

        # переходим на страницу предмета
        self.nure_driver.get(url)

        # ищем ссылку, по которой нужно перейти, чтобы отметить присутствие

        try:

            visits_table = WebDriverWait(self.nure_driver, 1).until(
                ec.presence_of_element_located((By.CSS_SELECTOR,
                                                'table[class="generaltable attwidth boxaligncenter"]')))
            visits_table_urls = WebDriverWait(visits_table, 1).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                     'a')))
        except TimeoutException:
            # если тут ссылок вдруг не оказалось
            logging.debug("nothing to confirm on subject page")
            return False

        # поиск среди всех ссылок в этом элементе тех, которые отвечает за отправление посещаемости
        text = "Отправить посещаемость"
        confirm_elements = list(filter(lambda el: text in el.text, visits_table_urls))

        # переходим по ним ( ожидается что такая ссылка будет только одна но кто его знает )
        for confirm_element in confirm_elements:
            self.nure_driver.get(confirm_element.get_attribute('href'))

            try:
                logging.debug("there is a complicated confirmation")
                self._get_complicated_confirmation()  # дополнительное подтверждение
            except TimeoutException:
                logging.debug("there isn`t complicated confirmation")

        logging.info(f"pair confirmed at {url}")

        return True

    def _get_complicated_confirmation(self):
        """ пройти обновленное подтверждение посещения ( после нажатия на кнопку посещаемость )"""
        self._select_checkbox_attended()
        self._press_confirm()

    def _press_confirm(self):
        """нажимает на кнопку подтверждения посещаемости в новой усложненной форме"""
        button = WebDriverWait(self.nure_driver, 1).until(
            ec.presence_of_element_located((By.CSS_SELECTOR,
                                            '''div[class="form-group  fitem  "]''')))
        button.click()
        logging.debug("confirm button pressed")

    def _select_checkbox_attended(self):
        """Выбирает на странице посещений чекбокс 'присутствовал' """
        checkbox = WebDriverWait(self.nure_driver, 1).until(
                ec.presence_of_element_located((By.CSS_SELECTOR,
                                                'label[class="form-check-inline form-check-label  fitem  "]')))
        checkbox.click()
        logging.debug("selected checkbox attended")

    def _select_checkbox_late(self):
        """Выбирает на странице посещений чекбокс 'опоздал' """
        checkbox = WebDriverWait(self.nure_driver, 1).until(
                ec.presence_of_element_located((By.CSS_SELECTOR,
                                                'label[class="form-check-inline form-check-label  fitem  "]')))
        checkbox.click()
        logging.debug("selected checkbox late")


if __name__ == '__main__':
    pass

