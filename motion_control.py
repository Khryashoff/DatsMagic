import math

from calculations import (sum_vector, subtract_vector, vector_from_points,
                          calculate_distance, calculate_angle_between_vectors,
                          normalize_vector, normalize_max_vector,
                          create_stop_acceleration)


MIN_HEALTH_FOR_SHIELD = 50


def control_transports(data):
    """
    Управляет транспортами на основе их текущего состояния и окружения.

    Параметры:
    data (dict): Данные о транспортах, аномалиях, врагах и монетах.
                 Ожидаются ключи:
                 -'transports'
                 -'bounties'
                 -'enemies'
                 -'maxAccel'
                 -'attackRange'
                 -'attackDamage'.

    Возвращает:
    list: Список команд для транспортов, каждая из которых включает:
          - 'acceleration': Ускорение для транспорта.
          - 'activateShield': Активация щита (True/False).
          - 'id': Идентификатор транспорта.
          - 'attack': Команда атаки, если враг выбран (опционально).
    """
    transports_commands = []

    # Инициализация команд для текущего транспорта
    for transport in data['transports']:
        command = {
            "acceleration": {"x": 0, "y": 0},
            "activateShield": False,
            "id": transport["id"]
        }

        # Текущие вектора ускорения
        currentVector = transport["velocity"]
        anomalyVector = transport["anomalyAcceleration"]

        # Общий вектор ускорения
        total_acceleration = sum_vector(currentVector, anomalyVector)

        # Поиск ближайшей монеты
        nearest_bounty = None
        min_distance = float('inf')
        max_points = float('-inf')
        bounty_with_max_points = None

        for bounty in data['bounties']:
            distance_to_bounty = calculate_distance(
                transport['x'], transport['y'], bounty['x'], bounty['y']
                )

            # Вычисление вектора к текущей монете
            directionVectorToBounty = vector_from_points(transport, bounty)

            # Условия для нахождения ближайшей монеты с учётом угла
            if distance_to_bounty < min_distance:
                min_distance = distance_to_bounty
                nearest_bounty = bounty

            # Проверка угла между векторами
            angle_between_temp = calculate_angle_between_vectors(
                total_acceleration, directionVectorToBounty
                )

            # Определение монеты с наибольшими очками, доступной для сбора
            if (
                abs(angle_between_temp) <= 15 and distance_to_bounty <= 200
                ) or (
                    angle_between_temp <= 45 and distance_to_bounty <= 50
                    ):
                if bounty['points'] - distance_to_bounty > max_points:
                    max_points = bounty['points'] - distance_to_bounty
                    bounty_with_max_points = bounty

        # Вычисление итогового направления для движения
        directionVector = vector_from_points(
            {"x": transport["x"], "y": transport["y"]}, bounty_with_max_points
            if bounty_with_max_points else nearest_bounty
            )
        coef = math.sqrt(
            transport['velocity']['x'] ** 2 + transport['velocity']['y'] ** 2
            ) / data["maxAccel"] / (
                1.2 if calculate_angle_between_vectors(
                    directionVector, transport
                    ) > 20 else 2
                )
        normalizedCf = max(coef, 1)

        # Корректировка ускорения
        resultWithCoef = subtract_vector(
            directionVector,
            {"x": total_acceleration["x"]*normalizedCf,
             "y": total_acceleration["y"] * normalizedCf}
             )
        if normalize_vector(
            directionVector, 1) == normalize_vector(
                total_acceleration, 1
                ):
            command["acceleration"] = {'x': 0, 'y': 0}
        else:
            command["acceleration"] = normalize_max_vector(
                resultWithCoef, data['maxAccel']
                )

        # Корректировка ускорения, если текущая скорость выше желаемой
        velocity_magnitude = math.sqrt(
            transport['velocity']['x'] ** 2 + transport['velocity']['y'] ** 2
            )
        if velocity_magnitude > data["maxAccel"]:
            angle_between = calculate_angle_between_vectors(
                transport['velocity'], directionVector
                )
            if angle_between > 30:
                stop_accel = create_stop_acceleration(transport['velocity'])
                command["acceleration"] = normalize_vector(
                    stop_accel, data['maxAccel']
                    )

        # Активация щита при низком здоровье
        if (transport["health"] <= MIN_HEALTH_FOR_SHIELD
                and transport["shieldCooldownMs"] == 0):
            command["activateShield"] = True

        # Поиск врага для атаки
        chosen_enemy = None
        min_distance = float('inf')
        if transport["attackCooldownMs"] == 0:
            for enemy in data['enemies']:
                distance_to_enemy = calculate_distance(
                    transport['x'], transport['y'], enemy['x'], enemy['y']
                    )
                if (distance_to_enemy <= data['attackRange']
                        and enemy["shieldLeftMs"] == 0):
                    if enemy["health"] <= data["attackDamage"]:
                        chosen_enemy = enemy
                        break
                    if distance_to_enemy < min_distance:
                        min_distance = distance_to_enemy
                        chosen_enemy = enemy

        # Атака выбранного врага
        if chosen_enemy:
            x = chosen_enemy['x']
            y = chosen_enemy['y']
            evy = chosen_enemy["velocity"]["y"]
            evx = chosen_enemy["velocity"]['x']
            rx = round(x + (evx / 3))
            ry = round(y + (evy / 3))
            command["attack"] = {"x": rx, "y": ry}

        # Добавление команды для транспорта
        transports_commands.append(command)

    return transports_commands
