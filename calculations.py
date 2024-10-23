import math


def sum_vector(vector1, vector2):
    """
    Суммирует два вектора.

    Параметры:
    vector1 (dict): Первый вектор с ключами 'x' и 'y'.
    vector2 (dict): Второй вектор с ключами 'x' и 'y'.

    Возвращает:
    dict: Новый вектор, являющийся суммой vector1 и vector2.
    """
    return {
        'x': vector1['x'] + vector2['x'],
        'y': vector1['y'] + vector2['y']
    }


def subtract_vector(vector1, vector2):
    """
    Вычитает второй вектор из первого.

    Параметры:
    vector1 (dict): Первый вектор с ключами 'x' и 'y'.
    vector2 (dict): Второй вектор с ключами 'x' и 'y'.

    Возвращает:
    dict: Новый вектор, являющийся разностью vector1 и vector2.
    """
    return {
        'x': vector1['x'] - vector2['x'],
        'y': vector1['y'] - vector2['y']
    }


def vector_from_points(point1, point2):
    """
    Создает вектор между двумя точками.

    Параметры:
    point1 (dict): Первая точка с ключами 'x' и 'y'.
    point2 (dict): Вторая точка с ключами 'x' и 'y'.

    Возвращает:
    dict: Вектор от point1 до point2.
    """
    return {
        'x': point2['x'] - point1['x'],
        'y': point2['y'] - point1['y']
    }


def calculate_distance(x1, y1, x2, y2):
    """
    Вычисляет расстояние между двумя точками.

    Параметры:
    x1, y1 (float): Координаты первой точки.
    x2, y2 (float): Координаты второй точки.

    Возвращает:
    float: Евклидово расстояние между точками.
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def calculate_angle_between_vectors(v1, v2):
    """
    Вычисляет угол между двумя векторами в градусах.

    Параметры:
    v1 (dict): Первый вектор с координатами 'x' и 'y'.
    v2 (dict): Второй вектор с координатами 'x' и 'y'.

    Возвращает:
    float: Угол между векторами в градусах.
    """
    dot_product = v1['x'] * v2['x'] + v1['y'] * v2['y']
    magnitude_v1 = math.sqrt(v1['x'] ** 2 + v1['y'] ** 2)
    magnitude_v2 = math.sqrt(v2['x'] ** 2 + v2['y'] ** 2)

    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return math.degrees(0)
    cos_angle = dot_product / (magnitude_v1 * magnitude_v2)
    cos_angle = max(min(cos_angle, 1), -1)
    angle = math.acos(cos_angle)
    return math.degrees(angle)


def normalize_vector(vector, max_length):
    """
    Нормализует вектор до указанной максимальной длины.

    Параметры:
    vector (dict): Вектор с координатами 'x' и 'y'.
    max_length (float): Максимальная длина вектора.

    Возвращает:
    dict: Нормализованный вектор.
    """
    length = math.sqrt(vector['x'] ** 2 + vector['y'] ** 2)
    if length > 0:
        scaling_factor = min(max_length / length, 1)
        return {
            'x': vector['x'] * scaling_factor,
            'y': vector['y'] * scaling_factor
        }
    return {'x': 0, 'y': 0}


def normalize_max_vector(vector, max_length):
    """
    Нормализует вектор, если его длина превышает максимальную.

    Параметры:
    vector (dict): Вектор с координатами 'x' и 'y'.
    max_length (float): Максимальная длина вектора.

    Возвращает:
    dict: Либо нормализованный вектор, либо исходный,
    если его длина меньше или равна max_length.
    """
    length = math.sqrt(vector['x'] ** 2 + vector['y'] ** 2)
    if length > max_length:
        scaling_factor = max_length / length
        return {
            'x': vector['x'] * scaling_factor,
            'y': vector['y'] * scaling_factor
        }
    return vector


def create_stop_acceleration(velocity):
    """
    Создает вектор замедления для полной остановки объекта.

    Параметры:
    velocity (dict): Вектор скорости с координатами 'x' и 'y'.

    Возвращает:
    dict: Вектор, противоположный скорости, для остановки объекта.
    """
    return {
        "x": -velocity["x"],
        "y": -velocity["y"]
    }
