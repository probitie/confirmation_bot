from project import *
from project.driver import NureDriver
from project.presence_confirmation import PresenceConfirmation
from project.student import Student
from project.config import Config

import logging.config

# откючение логгеров сторонних библиотек
logging.config.dictConfig({
    'version': 1,
    # Other configs ...
    'disable_existing_loggers': True
})


class Main:
    def __init__(self):
        """тк возможно что к боту будут прикручиваться новые фичи, все будет запускаться через этот файл"""
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t %(asctime)s.%(msecs)03d:%(filename)s:%(lineno)d:%(message)s',
                            datefmt='%H:%M:%S')

        self.cfg = Config()
        assert self.cfg.login != '' and self.cfg.password != ''
        self.student = Student(self.cfg.login, self.cfg.password)

        self.driver = NureDriver()
        self.driver.log_into_nure(self.student)
        self.presence_confirmation = PresenceConfirmation(self.driver)
        self.run_with_interval()

    def _pairs_datetime(self):
        """возвращает список начала и конца каждой пары, но дата уже переведена в datetime"""
        pairs = []
        for pair in self.cfg.pairs:
            pair_datetime = self._get_start_end_time_of_pair(pair)
            pairs.append(pair_datetime)
        return pairs

    def run_with_interval(self):
        """запускает подтверждение присутствия на паре в определенные промежутки времени (начало каждой пары)"""

        pairs_datetime = self._pairs_datetime()

        skip = False

        for (pair_start, pair_end) in pairs_datetime:

            time_left = self.get_time_left_for_pair(pair_start)
            self.wait(time_left)

            # этот блок позвояет в случае, если уже прошло несколько пар, до запуска бота, выполнить подтверждение
            # только 1 раз ( остальные разы он просто пропускает, до того момента когда time_left не будет больше 0
            if time_left == 0 and skip:
                continue
            elif time_left > 0 and skip:
                skip = False

            skip = True
            self.presence_confirmation.confirm()

    @staticmethod
    def wait(seconds):
        logging.debug(
            f"waiting to the next pair: {int(seconds / 3600)} hours {int((seconds % 3600) / 60)} minutes {seconds % 3600 % 60} seconds")
        time.sleep(seconds)

    def get_time_left_for_pair(self, pair_start: datetime.datetime):
        """возвращает количество секунд, оставшееся до начала пары"""
        now = datetime.datetime.now()
        pair_start_with_delay = pair_start + datetime.timedelta(minutes=self.cfg.confirmation_interval_min)
        if pair_start_with_delay < now:
            return 0  # если пара уже началась( текущее время больше времени начала пары) - то нужно подтвердить сейчас
        else:
            delta = pair_start_with_delay - now
            return delta.total_seconds()

    @staticmethod
    def _get_start_end_time_of_pair(string: str) -> List[datetime.datetime]:
        """
        Возвращает Datetime начала и конца пары

        :return: (start_pair_time, end_pair_time)
        """

        date_format = "%H:%M"

        # разбиваем текст элемента, получаем с него часы и минуты пары
        str_start, str_end = string.split('/')

        # переводим часы и минуты в datetime
        start_clock = datetime.datetime.strptime(str_start, date_format)
        end_clock = datetime.datetime.strptime(str_end, date_format)

        # теперь к часам и минутам добавляем остальные компоненты даты
        # - чтобы получилась полная однозначная дата начала/конца пары
        start = datetime.datetime.now().replace(hour=start_clock.hour, minute=start_clock.minute, second=0,
                                                microsecond=0)
        end = datetime.datetime.now().replace(hour=end_clock.hour, minute=end_clock.minute, second=0, microsecond=0)
        logging.debug(f"pair starts at {start} and ends at {end}")

        return [start, end]


if __name__ == '__main__':
    try:
        Main()
    except:
        logging.error(traceback.format_exc())
    finally:
        input("press enter to finish the program")

