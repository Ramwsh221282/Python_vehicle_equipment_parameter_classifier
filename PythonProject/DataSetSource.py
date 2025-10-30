import csv
import os.path
from collections import Counter
from typing import List, Tuple, Callable


def create_engine_type_dataset() -> List[Tuple[str, str]]:
    dataset = []

    # === ДИЗЕЛЬ ===
    diesel_examples = [
        "Двигатель дизельный",
        "Тип двигателя: дизель",
        "Дизельный двигатель Cummins",
        "Мощность: 250 л.с., тип двигателя - дизель",
        "ДВС: дизель, жидкостного охлаждения",
        "Дизель, 6 цилиндров, турбонаддув",
        "Тип мотора: дизельный",
        "Используется дизельное топливо",
        "Двигатель: дизель, соответствие Tier 3",
        "Топливная система: дизельная",
        # С техническими характеристиками
        "Характеристики: Марка - Komatsu, Тип двигателя - Дизель, Мощность - 180 кВт",
        "Тип двигателя: Дизель\nМодель: 6D107\nМощность: 147 кВт",
        # Вопросы
        "Какой тип двигателя? Дизельный.",
        "Уточните тип двигателя: дизель",
        # Шумные тексты
        "Продам харвестер. Двигатель дизельный, наработка 5000 м/ч. Гидравлика в норме.",
        "После капитального ремонта. Дизель работает отлично. Цена договорная.",
    ]
    for text in diesel_examples:
        dataset.append((text, "дизель"))

    # === БЕНЗИН ===
    gasoline_examples = [
        "Двигатель бензиновый",
        "Тип двигателя: бензин",
        "Бензиновый мотор Honda",
        "Работает на бензине АИ-95",
        "Тип топлива: бензин",
        "Бензин, 4 цилиндра, карбюратор",
        "Мотор: бензин",
        "Бензиновый двигатель, 1.6 л",
        "Тип ДВС: бензин",
        "Используется бензин",
        # Спецификации
        "Марка: УАЗ, Тип двигателя: Бензин, Объём: 2.7 л",
        "Тип двигателя: Бензин\nМощность: 128 л.с.\nЭкологический класс: Евро-4",
        # Вопросы
        "Какой двигатель? Бензиновый.",
        "Тип двигателя бензин?",
        # Шум
        "Лесовоз в отличном состоянии. Двигатель бензин, расход 18 л/100км.",
    ]
    for text in gasoline_examples:
        dataset.append((text, "бензин"))

    # === ГАЗ ===
    gas_examples = [
        "Двигатель газовый",
        "Тип двигателя: газ",
        "Работает на сжиженном газе",
        "Газовый мотор",
        "Тип топлива: газ",
        "Газ/бензин",
        "Двигатель: газ",
        "Газовое оборудование установлено",
        "Тип ДВС: газ",
        "Используется природный газ",
        # Спецификации
        "Тип двигателя: Газ\nМодель: ГАЗ-560\nМощность: 100 л.с.",
        # Шум
        "Форвардер с газовым двигателем. Пробег 12000 км.",
    ]
    for text in gas_examples:
        dataset.append((text, "газ"))

    # === ЭЛЕКТРО ===
    electric_examples = [
        "Двигатель электрический",
        "Тип двигателя: электро",
        "Электромотор",
        "Работает от аккумуляторов",
        "Электрический привод",
        "Тип топлива: электричество",
        "Электро",
        "Электродвигатель, 50 кВт",
        "Тип ДВС: электро",
        "Полностью электрический",
        # Спецификации
        "Тип двигателя: Электро\nНапряжение: 400 В\nЁмкость батареи: 60 кВтч",
        # Шум
        "Новый электрический погрузчик. Время работы 8 часов.",
    ]
    for text in electric_examples:
        dataset.append((text, "электро"))

    # === ГИБРИДНЫЙ ===
    hybrid_examples = [
        "Двигатель гибридный",
        "Тип двигателя: гибридный",
        "Гибридная силовая установка",
        "Комбинированный двигатель",
        "Гибрид: дизель + электро",
        "Тип топлива: гибрид",
        "Гибридный привод",
        "ДВС + электромотор",
        "Тип ДВС: гибридный",
        "Система гибридная",
        # Спецификации
        "Тип двигателя: Гибридный\nДизель: 150 л.с.\nЭлектромотор: 50 кВт",
        # Шум
        "Продам гибридный экскаватор. Экономия топлива 30%.",
    ]
    for text in hybrid_examples:
        dataset.append((text, "гибридный"))

    # === ЭТАНОЛ === (редкий, но добавим)
    ethanol_examples = [
        "Двигатель работает на этаноле",
        "Тип двигателя: этанол",
        "Этаноловый мотор",
        "Топливо: этанол",
        "Двигатель под этанол",
        "Этанол, биотопливо",
        # Спецификации
        "Тип двигателя: Этанол\nМощность: 110 л.с.",
    ]
    for text in ethanol_examples:
        dataset.append((text, "этанол"))

    # === НЕИЗВЕСТНО / НЕРЕЛЕВАНТНО ===
    unknown_examples = [
        # Техника без упоминания типа двигателя
        "Экскаватор после пожара",
        "Продам харвестер без двигателя",
        "Лесовоз на запчасти",
        "Форвардер в хорошем состоянии",
        "Кабина от комбайна",
        "Гидравлическая стрела в сборке",
        "Топливный бак 320 литров",
        "Мосты от трактора",
        "Коробка передач ZF",
        "Рулевая колонка",
        # Общие фразы
        "Цена договорная",
        "Срочно! Звоните!",
        "Возможен торг",
        "Без торга",
        "Только серьёзным покупателям",
        # Шумные описания без типа двигателя
        "Джойстик с четырьмя переключателями\nСистема отопления\nУниверсальный ключ\nРадио с CD",
        "Солнцезащитные шторки\nРемень безопасности\nГалогеновое освещение\nСветодиодный маячок",
        "Стрела 6.2 м\nРукоять 3.05 м\nТраки 600 мм\nХодовая тележка",
        "Двигатель Tier 2",  # ← ВАЖНО: нет типа топлива!
        "Модель: Соболь 2752\nГод: 2023\nЦвет: белый\nПробег: 37738 км",  # ← как text6 без "Тип двигателя"
        "Характеристики техники:\nМарка: John Deere\nГод выпуска: 2020\nНаработка: 4500 м/ч",
        # Абстрактные фразы
        "После капитального ремонта",
        "В отличном состоянии",
        "Не битый, не крашеный",
        "Один владелец",
    ]
    for text in unknown_examples:
        dataset.append((text, "неизвестно"))
    return dataset

# написать распределение меток по классам (в количестве).
def print_dataset_class_distribution_levels(dataset: List[Tuple[str, str]]):
    datasetLength: int = len(dataset)
    print(f'Количество данных: {datasetLength}')
    labels = [label for _, label in dataset]
    label_counts = Counter(labels)
    print('-' * 40)
    print(f'Распределение классов:')
    for label, count in label_counts.items():
        percentage = (count / datasetLength) * 100
        print(f'{label:<12}: | {count:>3} | {percentage:>5.1f}%')
    print('-' * 40)
    print(f'{'Итого':<12} | {datasetLength:>3} | 100.0%')

# проверить наличие дубликатов
def has_duplicates(dataset: List[Tuple[str, str]]) -> bool:
    texts = [text for text, _ in dataset]
    unique_texts = set(texts)
    origin_length = len(texts)
    unique_length = len(unique_texts)
    return origin_length != unique_length

# вывести дубликаты
def print_has_duplicates(dataset: List[Tuple[str, str]], duplicate_cheker: Callable[[List[Tuple[str, str]]], bool]) -> None:
    print('-' * 40)
    print(f'Has duplicates: {duplicate_cheker(dataset)}')

# сохранить файл.
def save_in_csv(dataset: List[Tuple[str, str]], file_name: str) -> None:
    corrected = add_csv_extension_if_not_exists(file_name)
    remove_file_if_exists(corrected)
    print('-' * 40)
    print(f'writing dataset files in csv file: {corrected}')
    with open(corrected, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['text', 'label'])
        writer.writerows(dataset)
    print(f'data set has been written to csv file: {corrected}')
    print('-' * 40)

# удалить файл, если он уже существует.
def remove_file_if_exists(file_name: str) -> None:
    if os.path.exists(file_name):
        print(f'file already exists {file_name}')
        os.remove(file_name)
        print('file has been removed')
        return None
    return None

# добавить .csv extension в название файла, если его нет.
def add_csv_extension_if_not_exists(file_name: str) -> str:
    if not file_name.endswith('.csv'):
        print(f'file {file_name} does not has .csv extension. Returning with .csv')
        return file_name + '.csv'
    return file_name










