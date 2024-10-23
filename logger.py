def log(response, client):
    """
    Логирует информацию о текущем состоянии игры и транспортах.

    Параметры:
    - response (dict): Ответ сервера, содержащий
    информацию об игровых параметрах и транспортах.
    - client (object): Клиент для вывода сообщений в систему или интерфейс.

    Логируемая информация:
    1. Общая информация:
        - Points: Очки, набранные игроком.
        - attackCooldownMs: Время восстановления атаки (в миллисекундах).
        - attackDamage: Урон от атаки.
        - attackExplosionRadius: Радиус взрыва атаки.
        - attackRange: Дальность атаки.
        - maxAccel: Максимальное ускорение транспорта.
        - maxSpeed: Максимальная скорость транспорта.

    2. Информация по каждому транспорту:
        - ID: Уникальный идентификатор транспорта.
        - Status: Текущий статус транспорта.
        - Health: Уровень здоровья транспорта.
        - Position: Координаты транспорта на карте (x, y).
        - Velocity: Вектор скорости транспорта (x, y).
        - Self Acceleration: Ускорение транспорта, обусловленное собственными
        действиями (x, y).
        - Anomaly Acceleration: Ускорение транспорта под воздействием
        аномалий (x, y).
        - Attack Cooldown: Время до следующей атаки (в миллисекундах).
        - Shield Cooldown: Время до восстановления щита и
        оставшееся время работы щита (в миллисекундах).
        - Death Count: Количество смертей транспорта за игру.

    Функция выводит информацию в системный лог или
    интерфейс через объект `client`.
    """
    client.message(f'POINST {response["points"]}')
    client.message(f'attackCooldownMs {response["attackCooldownMs"]}')
    client.message(f'attackDamage {response["attackDamage"]}')
    client.message(
        f'attackExplosionRadius {response["attackExplosionRadius"]}'
        )
    client.message(f'attackRange {response["attackRange"]}')
    client.message(f'maxAccel {response["maxAccel"]}')
    client.message(f'maxSpeed {response["maxSpeed"]}')

    for i, transport in enumerate(response["transports"]):
        client.message('---------------------------------')
        client.message(f'Transport {i+1}:')
        client.message(f'ID {transport["id"]}')
        client.message(f'Status {transport["status"]}')
        client.message(f'Health {transport["health"]} / 100')
        client.message(f'Position: (x: {transport["x"]}, y: {transport["y"]})')
        client.message(
            f'Velocity: (x: {transport["velocity"]["x"]}, '
            f'y: {transport["velocity"]["y"]})'
            )
        client.message(
            f'Self Acceleration: (x: {transport["selfAcceleration"]["x"]}, '
            f'y: {transport["selfAcceleration"]["y"]})'
            )
        client.message(
            f'Anomaly Acceleration: ( '
            f'x: {transport["anomalyAcceleration"]["x"]}, '
            f'y: {transport["anomalyAcceleration"]["y"]})'
            )
        client.message(f'Attack Cooldown: {transport["attackCooldownMs"]} ms')
        client.message(
            f'Shield Cooldown: '
            f'{transport["shieldLeftMs"]}/{transport["shieldCooldownMs"]} ms'
            )
        client.message(f'Death Count: {transport["deathCount"]}')
        client.message('---------------------------------')
