import os
import json
import time
import _socket
import requests

from logger import log
from dotenv import load_dotenv
from motion_control import control_transports
from map_render import get_map, draw_transport_actions

load_dotenv()
api_token = os.getenv('API_TOKEN')


class RewindClient():
    RED = 0xff0000
    GREEN = 0x00ff00
    BLUE = 0x0000ff
    PURPLE = 0xf000e9
    YELLOW = 0xfff222
    DARK_RED = 0x770000
    DARK_GREEN = 0x007700
    DARK_BLUE = 0x000077
    DARK_PURPLE = 0x71006d
    DARK_YELLOW = 0xA39B23
    TRANSPARENT = 0x7f000000
    INVISIBLE = 0x01000000

    def __init__(self, host=None, port=None):
        self._socket = _socket.socket()
        self._socket.setsockopt(_socket.IPPROTO_TCP, _socket.TCP_NODELAY, True)
        if host is None:
            host = "127.0.0.1"
            port = 9111
        self._socket.connect((host, port))

    @staticmethod
    def _to_geojson(points):
        flat = []
        for p in points:
            flat.append(p[0])
            flat.append(p[1])
        return flat

    def _send(self, obj):
        if self._socket:
            self._socket.sendall(json.dumps(obj).encode('utf-8'))

    def line(self, x1, y1, x2, y2, color):
        self._send({
            'type': 'polyline',
            'points': [x1, y1, x2, y2],
            'color': color
        })

    def polyline(self, points, color):
        self._send({
            'type': 'polyline',
            'points': RewindClient._to_geojson(points),
            'color': color
        })

    def circle(self, x, y, radius, color, fill=False):
        self._send({
            'type': 'circle',
            'p': [x, y],
            'r': radius,
            'color': color,
            'fill': fill
        })

    def rectangle(self, x1, y1, x2, y2, color, fill=False):
        self._send({
            'type': 'rectangle',
            'tl': [x1, y1],
            'br': [x2, y2],
            'color': color,
            'fill': fill
        })

    def triangle(self, p1, p2, p3, color, fill=False):
        self._send({
            'type': 'triangle',
            'points': RewindClient._to_geojson([p1, p2, p3]),
            'color': color,
            'fill': fill
        })

    def circle_popup(self, x, y, radius, message):
        self._send({
            'type': 'popup',
            'p': [x, y],
            'r': radius,
            'text': message
        })

    def rect_popup(self, tl, br, message):
        self._send({
            'type': 'popup',
            'tl': RewindClient._to_geojson([tl]),
            'br': RewindClient._to_geojson([br]),
            'text': message
        })

    def message(self, msg):
        self._send({
            'type': 'message',
            'message': msg
        })

    def set_options(self, layer=None, permanent=None):
        data = {'type': 'options'}
        if layer is not None:
            data['layer'] = layer
        if permanent is not None:
            data['permanent'] = permanent
        self._send(data)

    def end_frame(self):
        self._send({'type': 'end'})


# Создание экземпляра клиента
client = RewindClient()

USE_TEST_SERVER = False

if USE_TEST_SERVER:
    URL_ROUND = 'https://games-test.datsteam.dev/rounds/magcarp'
    URL_MOVE = 'https://games-test.datsteam.dev/play/magcarp/player/move'
else:
    URL_ROUND = 'https://games.datsteam.dev/rounds/magcarp'
    URL_MOVE = 'https://games.datsteam.dev/play/magcarp/player/move'


def fetch_rounds():
    """
    Запрашивает данные раундов с внешнего API.

    Отправляет GET-запрос на указанный URL для получения данных о раундах игры.
    В случае успешного запроса возвращает данные в формате JSON,
    при ошибке печатает сообщение об ошибке и возвращает None.

    Возвращает:
    dict: Данные раундов в формате JSON или None в случае ошибки.
    """
    try:
        response = requests.get(URL_ROUND, headers={'X-Auth-Token': api_token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка запроса данных карты: {e}")
        return None


def fetch_map_data(transports):
    """
    Отправляет данные о транспортах на сервер и
    получаетобновленную информацию о карте.

    Отправляет POST-запрос на API для обновления данных о
    транспортах на основе их текущих действий.
    В случае успешного запроса возвращает обновленные данные карты в
    формате JSON, при возникновении HTTP-ошибки печатает сообщение и
    тело ответа, и возвращает None.

    Параметры:
    transports (list): Список данных о транспортах.

    Возвращает:
    dict: Обновленные данные карты в формате JSON или None в случае ошибки.
    """
    try:
        data = {'transports': transports}
        response = requests.post(
            URL_MOVE, json=data, headers={'X-Auth-Token': api_token}
            )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        print(f"HTTP ошибка: {e}")
        print(f"Тело ответа сервера: {response.text}")
        return None


def fetch_map_data_mock(transports):
    """
    Загружает данные карты из локального файла mock.json для тестирования.

    Открывает локальный файл mock.json и загружает данные карты в формате JSON.
    Используется в тестовых целях, чтобы не делать запросы к реальному API.

    Параметры:
    transports (list): Список данных о транспортах.

    Возвращает:
    dict: Данные карты, загруженные из mock.json.
    """
    with open('./mock.json', 'r') as file:
        map_data = json.load(file)
        return map_data


def main():
    """
    Основной цикл программы для управления транспортами и обновления карты.

    В цикле запрашивает данные карты, управляет
    транспортами и выводит действия на экран.
    Цикл продолжается до тех пор, пока не будет
    прерван пользователем (KeyboardInterrupt).
    Каждую итерацию программа рассчитывает действия транспортов,
    обновляет данные карты и выводит их.
    Прерывается с обработкой ошибок и закрытием сокета клиента.

    Исключения:
    KeyboardInterrupt: Останавливает цикл при нажатии Ctrl+C.
    Exception: Обрабатывает все остальные исключения,
    печатает сообщение об ошибке.
    """
    transports = []
    tick = 0
    try:
        while True:
            start = time.time()
            response = fetch_map_data(transports)

            log(response, client)

            # Установка постоянных опций для клиента
            client.set_options(permanent=True)
            client.rectangle(
                0, 0, response["mapSize"]["x"], response["mapSize"]["y"],
                client.GREEN
                )
            client.set_options(permanent=False)

            # Получение и отображение карты
            get_map(client, response)
            transports = control_transports(response)

            # Отрисовка действий транспорта
            draw_transport_actions(client, response, transports)

            tick += 1
            time.sleep(0.1)
            end = time.time()
            print(f'tick time: {end - start}')
    except KeyboardInterrupt:
        print("Клиент остановлен пользователем.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Закрытие сокета клиента
        client._socket.close()


if __name__ == "__main__":
    main()
