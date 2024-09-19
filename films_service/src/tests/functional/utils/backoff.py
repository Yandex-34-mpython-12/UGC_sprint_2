import logging
import time
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backoff(func, start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время,
    если возникла ошибка. Использует наивный экспоненциальный рост времени повтора
    (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * (factor ^ n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать время ожидания на каждой итерации
    :param border_sleep_time: максимальное время ожидания
    :return: результат выполнения функции
    """

    @wraps(func)
    def inner(*args, **kwargs):
        n = 1
        t = 0
        while True:
            if t < border_sleep_time:
                t = start_sleep_time * (factor ^ n)
            else:
                t = border_sleep_time
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f'An error occurred: {e}', exc_info=True)
                logger.info(
                    f'\nSleeping for {round(t, 1)} seconds. And function repeat execution: {func.__name__}')
                time.sleep(t)
                n = n + 1

    return inner
