def get_map(client, response):
    """
    Визуализирует карту с разными объектами на основе данных ответа сервера.

    Метод использует утилиту Rewind Viewer
    (https://github.com/kswaldemar/rewind-viewer) для создания и отрисовки
    графического интерфейса. В качестве графических элементов
    используются геометрические фигуры, отображающие информацию об:
    - аномалиях,
    - монетах,
    - врагах,
    - транспортах,
    - разыскиваемых целей.

    Параметры:
    client (object): Объект клиента, предоставляющий методы для
    графической визуализации (например, `circle`, `rectangle`, `line` и т.д.).
    response (dict): Словарь с данными о состоянии карты,
    содержащий списки аномалий, врагов, монет, транспортов и разыскиваемых.

    Ключевые категории из `response`:
    - 'anomalies': Список аномалий на карте с координатами и радиусами.
    - 'bounties': Список монет с координатами и очками.
    - 'enemies': Список врагов с координатами, уровнем здоровья и щитом.
    - 'transports': Список транспортов с координатами,
       скоростью, ускорением и состоянием здоровья.
    - 'wantedList': Список разыскиваемых целей с координатами.
    """

    if response is not None:
        # Отрисовка аномалий
        for anomaly in response['anomalies']:
            client.set_options(layer=1)
            client.circle(
                anomaly['x'], anomaly['y'],
                anomaly['radius'], client.DARK_PURPLE
                )
            client.circle(
                anomaly['x'], anomaly['y'],
                anomaly["effectiveRadius"], client.PURPLE
                )
            client.circle_popup(
                anomaly['x'], anomaly['y'],
                anomaly['radius'], f'Anomaly {anomaly['id']}'
                )

        # Отрисовка монет
        for bounty in response['bounties']:
            client.set_options(layer=2)
            client.circle(
                bounty['x'], bounty['y'],
                bounty['radius'], client.YELLOW
                )
            client.circle_popup(
                bounty['x'], bounty['y'],
                bounty['radius'], f'Bounty - {bounty['points']}'
                )

        # Отрисовка врагов
        for enemy in response['enemies']:
            client.set_options(layer=3)
            client.rectangle(
                enemy['x'] - 10, enemy['y'] - 10,
                enemy['x'] + 10, enemy['y'] + 10, client.RED
                )
            client.circle_popup(enemy['x'], enemy['y'], 10, 'enemy')

            # Отрисовка полоски здоровья врага
            health_x_start = enemy['x'] - 15
            health_y = enemy['y'] - 15
            health_length = 30
            health_current_length = (enemy['health'] / 100) * health_length
            client.rectangle(
                health_x_start, health_y,
                health_x_start + health_current_length, health_y + 5,
                client.RED
                )
            client.rectangle(
                health_x_start + health_current_length, health_y,
                health_x_start + health_length, health_y + 5, client.DARK_RED
                )

            # Отрисовка отображения щита врага, если он активен
            if (enemy['shieldLeftMs'] > 0):
                client.rectangle(
                    enemy['x'] - 5, enemy['y'] - 5,
                    enemy['x'] + 5, enemy['y'] + 5, client.PURPLE
                    )

        # Отрисовка собственных транспортов
        for transport in response['transports']:
            client.set_options(layer=4)
            client.rectangle(
                transport['x'] - 10, transport['y'] - 10,
                transport['x'] + 10, transport['y'] + 10, client.DARK_GREEN
                )
            client.circle_popup(
                transport['x'], transport['y'],
                10, f'Transport {transport['id']}'
                )

            # Отрисовка полоски здоровья транспорта
            health_x_start = transport['x'] - 15
            health_y = transport['y'] - 15
            health_length = 30
            health_current_length = (transport['health'] / 100) * health_length
            client.rectangle(
                health_x_start, health_y,
                health_x_start + health_current_length, health_y + 5,
                client.RED
                )
            client.rectangle(
                health_x_start + health_current_length, health_y,
                health_x_start + health_length, health_y + 5, client.DARK_RED
                )

            # Отрисовка отображения щита транспорта, если он активен
            if (transport['shieldLeftMs'] > 0):
                client.rectangle(
                    transport['x'] - 5, transport['y'] - 5,
                    transport['x'] + 5, transport['y'] + 5, client.PURPLE
                    )

            # Отрисовка вектора ускорения транспорта
            self_accel_end_x = (
                transport['x'] + transport['selfAcceleration']['x']
                )
            self_accel_end_y = (
                transport['y'] + transport['selfAcceleration']['y']
                )
            client.line(
                transport['x'], transport['y'],
                self_accel_end_x, self_accel_end_y, client.DARK_GREEN
                )

            # Отрисовка вектора ускорения получаемого от аномалий
            self_accel_end_x = (
                transport['x'] + transport['anomalyAcceleration']['x']
                )
            self_accel_end_y = (
                transport['y'] + transport['anomalyAcceleration']['y']
                )
            client.line(
                transport['x'], transport['y'],
                self_accel_end_x, self_accel_end_y, client.DARK_PURPLE
                )

            # Отрисовка вектора скорости транспорта
            self_accel_end_x = transport['x'] + transport['velocity']['x']
            self_accel_end_y = transport['y'] + transport['velocity']['y']
            client.line(
                transport['x'], transport['y'],
                self_accel_end_x, self_accel_end_y, client.BLUE
                )

        # Отрисовка разыскиваемых целей
        for wanted in response['wantedList']:
            client.set_options(layer=5)
            client.circle(wanted['x'], wanted['y'], 0.5, client.DARK_RED)
            client.circle_popup(wanted['x'], wanted['y'], 10, 'wanted')

    # Завершение кадра для отображения
    client.end_frame()


def draw_transport_actions(client, response, transports_commands):
    """
    Отрисовывает действия транспортов на основе передаваемых команд.

    Параметры:
    client (object): Объект клиента для визуализации графических объектов.
    response (dict): Ответ с данными о транспортах (координаты, id и т.д.).
    transports_commands (list): Список команд для транспортов.

    Логика:
    - Если команда относится к атаке, то отображается траектория выстрела от
      текущего транспорта до атакуемой цели.
    """
    for transport in response['transports']:
        transport_id = transport['id']
        transport_x = transport['x']
        transport_y = transport['y']

        # Обрабатываются команды для каждого транспорта
        for command in transports_commands:
            if command['id'] == transport_id and 'attack' in command:

                # Передаются координаты цели для атаки
                attack_x, attack_y = (
                    command['attack']['x'], command['attack']['y']
                    )

                # Отображается вектор выстрела
                client.line(
                    transport_x, transport_y, attack_x, attack_y,
                    client.DARK_PURPLE
                    )
