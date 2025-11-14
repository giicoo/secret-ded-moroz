import string
import random

def code_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def distribute_santa_gifts(participants: list) -> dict:
    """
    :param participants: список ID участников (например, ["id1", "id2", "id3"])
    :return: словарь {дарящий: получатель}
    """
    if len(participants) < 2:
        raise ValueError("Должно быть как минимум 2 участника для распределения.")

    # Копируем список и перемешиваем
    shuffled = participants.copy()

    # Цикл повторного перемешивания, чтобы никто не получил самого себя
    attempts = 0
    while True:
        random.shuffle(shuffled)
        # Проверка: никто не дарит сам себе
        if all(giver != receiver for giver, receiver in zip(participants, shuffled)):
            break
        attempts += 1
        if attempts > 100:
            raise RuntimeError("Не удалось корректно распределить участников. Попробуйте ещё раз.")

    # Формируем словарь: кто кому дарит
    gifts = {participants[i]: shuffled[i] for i in range(len(participants))}
    return gifts
