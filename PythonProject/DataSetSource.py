import glob
import os
import random
import csv
import re
from typing import List, Tuple, Callable, Counter


def write_to_csv_file(file_path: str, items: List[Tuple[str, str]], columns: List[str]) -> None:
    delete_file(file_path)
    adjusted_file_path = adjust_csv_extension(file_path)
    csv_dictionary: List[dict[str, str]] = [{ 'text': text, 'label': label } for text, label in dict(items).items()]
    with open(adjusted_file_path, 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=columns)
        csv_writer.writeheader()
        csv_writer.writerows(csv_dictionary)

def write_list_to_csv_file(file_path: str, items: List[str]) -> None:
    delete_file(file_path)
    adjusted_file_path = adjust_csv_extension(file_path)
    with open(adjusted_file_path, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for item in items:
            writer.writerow([item])



def read_data_set(file_path: str) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    with open(file_path, 'r', encoding='utf-8', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            if len(row) == 2:
                text, label = row[0], row[1]
                items.append((text, label))
    return items

def read_data_set_as_list(file_path: str) -> List[str]:
    adjusted_file_path = adjust_csv_extension(file_path)
    items: List[str] = []
    with open(adjusted_file_path, 'r', encoding='utf-8', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            items.append(row[0])
    return items

def file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)

def delete_file(file_path: str) -> None:
    if file_exists(file_path):
        os.remove(file_path)

def has_csv_extension(file_path: str) -> bool:
    return file_path.endswith('.csv')

def adjust_csv_extension(file_path: str) -> str:
    if not has_csv_extension(file_path):
        return file_path + '.csv'
    return file_path

def print_classes_statistics(items: List[str], ignore_small:bool=True) -> None:
    tags: List[str] = []
    for text in items:
        found = re.findall(r'\{([^}]*)\}', text)
        tags.extend(found)
    unique_tags: List[str] = list(set(tags))
    print(f'Всего классов: {len(unique_tags)}')
    print(f'Классы: {unique_tags}')
    tag_counts: Counter = Counter(tags)
    tags_group: List[Tuple[str, int]] = tag_counts.most_common()
    print(f'Статистика по классам:')
    print('-', 40)
    for group in tags_group:
        if ignore_small:
            if group[1] < 10:
                continue
        print(f'{group[0]} - {group[1]}')
    print('-', 40)

def merge_with_other_list(current: List[str], other: List[str]) -> List[str]:
    new_items: List[str] = []
    new_items.extend(current)
    new_items.extend(other)
    data_unique = set(new_items)
    return list(data_unique)

def create_engine_type_dataset() -> List[Tuple[str, str]]:

    # items = read_data_set('engine_types_final_data_set.csv')
    # items.remove(items[0])
    # return items

    # current_path = os.getcwd()
    # required_extension = '.csv'
    # csv_files = glob.glob(os.path.join(current_path, f'*{required_extension}'))
    #
    # all_items: List[Tuple[str, str]] = []
    # for file_path in csv_files:
    #     items = read_data_set(file_path)
    #     if len(items) > 0:
    #         items.remove(items[0]) # remove [text, label] - header
    #     all_items.extend(items)
    #
    # return all_items

    dataset = []
    examples_per_class = 150

    items = [
        "Техника {brand} {model} прошла плановое ТО в {service_center}. Наработка на момент обслуживания: {motochasi_value} м/ч.",
        "В парке числится {category} {brand} {model}, {year} года выпуска. VIN: {vin}. Ответственный оператор: {operator_name}.",
        "Согласно инструкции, максимальная нагрузка для {brand} {model} не должна превышать {loading_weight} при работе в {les_area_type}.",
        "Журнал поломок: у {brand} {model} ({year}) зафиксирован износ гидромотора на {motochasi_value} м/ч. Рекомендовано ТО каждые {service_interval} м/ч.",
        "Аналитическая справка: доля техники {brand} {model} в лесхозе выросла на {growth_percent}% за {year}. Основное применение: {les_task_type}.",
        "Данные телематики: {brand} {model} находился в зоне {coordinates} с {start_time} по {end_time}. Средняя наработка за смену: {avg_hours} м/ч.",
        "В архиве хранится карточка на {brand} {model} — дата поступления: {acquisition_date}, первоначальная стоимость: {initial_price} руб.",
        "Сервисный отчёт: замена масла в двигателе {engine_desc} на {brand} {model} выполнена при наработке {motochasi_value} м/ч.",
        "По данным ГИС, {brand} {model} зарегистрирован в реестре спецтехники под номером {registry_id}. Владелец: {owner_org}.",
        "Оператор {operator_name} отметил: «{brand} {model} работает стабильно, но требует регулировки стрелы после {motochasi_value} м/ч.»",
        "В руководстве по эксплуатации указано: запрещено использовать {brand} {model} на склонах круче {max_slope}° без дополнительной фиксации.",
        "Лог системы мониторинга: {timestamp} — у {brand} {model} зафиксирован перегрев двигателя {engine_desc} при температуре окружающей среды {ambient_temp}°C.",
        "Инвентарная запись №{inventory_num}: {brand} {model}, {year}, двигатель {engine_power} л.с., текущая наработка — {hours} м/ч.",
        "Сравнительный анализ: {brand} {model} показал на {efficiency_percent}% лучшую производительность в {les_area_type}, чем аналоги.",
        "Запись в CRM: техника {brand} {model} простаивала {downtime_days} дней в {month} из-за ожидания запчастей для {engine_desc}.",
        "Нормативный документ ссылается на допустимую массу {brand} {model} — не более {explluatacionnaya_massa} при движении по грунтовым дорогам.",
        "Мобильное приложение зафиксировало: оператор {user_id} завершил смену на {brand} {model}. Выполнено задач: {tasks_completed}.",
        "Акт диагностики: у {brand} {model} ({year}) выявлен износ ходовой. Рекомендовано ТО при достижении {next_service_hours} м/ч.",
        "В базе данных обновлён статус: {brand} {model} переведён из категории «в работе» в «на ремонте». Причина: {failure_reason}.",
        "Отчёт по ГСМ: {brand} {model} израсходовал {fuel_consumption} л топлива за {hours} м/ч работы в условиях {les_work_site}.",
        "Сертификат соответствия №{cert_id} выдан на {brand} {model} с двигателем {engine_desc}, соответствующим нормам Евро-{euro_class}.",
        "Заметка инженера: «{brand} {model} — надёжная техника, но требует усиленного ТО гидравлики после {motochasi_threshold} м/ч.»",
        "Данные GPS: {brand} {model} перемещён из {location_from} в {location_to} для выполнения задачи «{task_type}».",
        "Статистика парка: средний ресурс двигателя {engine_desc} на технике {brand} {model} составляет {avg_engine_life} м/ч.",
        "Протокол испытаний: {brand} {model} выдержал нагрузку {load_test_value} в течение {test_duration} часов без сбоев.",
        "Внутреннее распоряжение: с {effective_date} разрешено использовать {brand} {model} только с дополнительной защитой кабины в {les_area_type}.",
        "Лог переписки: «Подскажите, совместим ли гидромолот {attachment_model} с {brand} {model}?» — «Да, при условии давления не выше {max_pressure} бар.»",
        "Архивная справка: первый {brand} {model} поступил в организацию в {year}. Списан в {write_off_year} с наработкой {final_hours} м/ч.",
        "Данные из системы учёта: {brand} {model} простаивал в {month} {year} по причине «{downtime_reason}». Потери: {downtime_cost} руб.",
        "Рекомендация по модернизации: установка системы {upgrade_system} на {brand} {model} повышает эффективность на {efficiency_gain}% при работе в {les_task_type}."
        "Техника {brand} {model} ({category}) прошла диагностику гидравлики. Рекомендовано ТО каждые {service_interval_hours} м/ч.",
        "В парке зарегистрирован {category} {brand} {model}. VIN: {vin}. Ответственный: {operator_name}. Текущая наработка: {hours} м/ч.",
        "Согласно нормативу, {category} {brand} {model} допущен к работе в условиях {les_area_type} при наличии {safety_equipment}.",
        "Журнал неисправностей: у {category} {brand} {model} зафиксирован износ стрелы на {motochasi_value} м/ч. Причина: {failure_cause}.",
        "Аналитика эффективности: {category} {brand} {model} показал производительность {output_rate} м³/ч при работе в {les_task_type}.",
        "Данные телематики: {category} {brand} {model} находился в зоне {coordinates}. Средний расход топлива: {fuel_consumption} л/м/ч.",
        "Инвентарная карточка №{inventory_id}: {category} — {brand} {model}, двигатель {engine_desc}, масса {explluatacionnaya_massa}.",
        "Сервисный отчёт: замена масла в КПП {category} {brand} {model} выполнена при наработке {motochasi_value} м/ч.",
        "В CRM обновлён статус: {category} {brand} {model} переведён в категорию «требует ремонта». Причина: {repair_reason}.",
        "Руководство по эксплуатации: запрещено использовать {category} {brand} {model} без {extra_safety_feature} на склонах.",
        "Лог системы мониторинга: у {category} {brand} {model} зафиксировано превышение вибрации в гидросистеме при {engine_rpm} об/мин.",
        "Сравнительный анализ: {category} {brand} {model} на {efficiency_percent}% эффективнее аналогов при выполнении {task_type}.",
        "Запись в базе ГСМ: {category} {brand} {model} израсходовал {fuel_liters} л за смену при наработке {hours} м/ч.",
        "Сертификат соответствия №{cert_number} выдан на {category} {brand} {model} с двигателем {engine_power} л.с.",
        "Оператор {operator_name} отметил в приложении: «{category} {brand} {model} работает стабильно, но шумит насос.»",
        "Норма выработки для {category} {brand} {model} в условиях {les_work_site}: {output_norm} м³/м/ч.",
        "Акт осмотра: {category} {brand} {model} соответствует требованиям. Ходовая, гидравлика, кабина — в норме. Состояние: {condition}.",
        "Данные GPS: {category} {brand} {model} перемещён из {location_from} в {location_to} для выполнения задачи «{task_description}».",
        "Статистика отказов: у {category} {brand} {model} чаще всего выходит из строя {component_name} (средний ресурс: {mtbf_hours} м/ч).",
        "Внутреннее распоряжение: с сегодняшнего дня {category} {brand} {model} должен эксплуатироваться только с {attachment_type}.",
        "Лог переписки: «Подходит ли гидромолот {attachment_model} для {category} {brand} {model}?» — «Да, при давлении до {max_pressure} бар.»",
        "Архивная запись: в парке числится {category} {brand} {model} с наработкой {motochasi_value} м/ч. Владелец: {owner_org}.",
        "Протокол испытаний: {category} {brand} {model} выдержал нагрузку {load_value} в течение {duration_hours} ч без сбоев.",
        "Рекомендация инженера: усилить защиту днища у {category} {brand} {model} при работе в {les_area_type}.",
        "Данные учёта простоев: {category} {brand} {model} простаивал {downtime_days} дней из-за отсутствия {spare_part}.",
        "Мобильное приложение зафиксировало завершение смены на {category} {brand} {model}. Выполнено: {tasks_completed} операций.",
        "Согласно СТО, минимальный интервал ТО для {category} {brand} {model} — {service_interval_hours} м/ч при работе в {les_work_site}.",
        "Заметка в техкарте: {category} {brand} {model} — слабое место: {weak_component}. Контролировать после {inspection_threshold} м/ч.",
        "Данные по экологичности: {category} {brand} {model} соответствует нормам Евро-{euro_class} при использовании топлива {fuel_grade}.",
        "Анализ парка: доля {category} марки {brand} (модель {model}) составляет {market_share_percent}% от общего количества техники."
        "В реестре техники зарегистрировано: {category} — {brand} {model}. VIN: {vin}. Ответственный: {operator_name}.",
        "Сервисный журнал: у {category} {brand} {model} выполнена замена масла в двигателе {engine_desc} при наработке {motochasi_value} м/ч.",
        "Техническое описание: {category} {brand} {model} предназначен для выполнения задач типа {les_task_type} в условиях {les_area_type}.",
        "Лог мониторинга: {category} {brand} {model} зафиксировал перегрев гидросистемы при температуре {hydraulic_temp}°C.",
        "Инвентарная запись №{inventory_id}: {category} — {brand} {model}, двигатель {engine_power} л.с., объём {engine_volume}.",
        "Акт диагностики: у {category} {brand} {model} выявлен износ ходовой части. Рекомендовано ТО при достижении {next_service_hours} м/ч.",
        "В CRM обновлён статус: {category} {brand} {model} переведён в режим «ограниченная эксплуатация» из-за неисправности {failed_component}.",
        "Норма расхода топлива для {category} {brand} {model} в условиях {les_work_site}: {fuel_norm} л/м/ч.",
        "Оператор {operator_name} отметил: «{category} {brand} {model} работает стабильно, но требует регулировки стрелы после {motochasi_value} м/ч.»",
        "Сравнительный отчёт: {category} {brand} {model} показал на {efficiency_gain}% выше производительность, чем аналоги при задаче «{task_type}».",
        "Данные GPS-трекера: {category} {brand} {model} находился в районе {coordinates} в течение {duration_hours} ч.",
        "Протокол испытаний: {category} {brand} {model} выдержал нагрузку {load_value} без сбоев в системе {system_name}.",
        "Запись в журнале ГСМ: {category} {brand} {model} израсходовал {fuel_consumption} л топлива за смену.",
        "Руководство по ТБ: запрещено использовать {category} {brand} {model} без {safety_equipment} при работе на склонах круче {slope_deg}°.",
        "Аналитика простоев: {category} {brand} {model} простаивал {downtime_days} дней из-за отсутствия запчасти {spare_part_name}.",
        "Сертификат соответствия №{cert_id} выдан на {category} {brand} {model} с двигателем, соответствующим Евро-{euro_class}.",
        "Лог переписки: «Поддерживает ли {category} {brand} {model} гидромолот {attachment_model}?» — «Да, при давлении до {max_pressure} бар.»",
        "Архивная карточка: {category} {brand} {model} числится в парке с наработкой {motochasi_value} м/ч. Владелец: {owner_org}.",
        "Заметка инженера: «{category} {brand} {model} — надёжный, но требует усиленного контроля {component_name} после {inspection_threshold} м/ч.»",
        "Данные телематики: средняя скорость {category} {brand} {model} в зоне {work_zone} — {avg_speed} км/ч при наработке {hours} м/ч.",
        "Внутреннее распоряжение: с сегодняшнего дня {category} {brand} {model} должен эксплуатироваться только с дополнительной защитой {protection_type}.",
        "Статистика отказов: у {category} {brand} {model} чаще всего выходит из строя {weak_component} (средний ресурс: {mtbf_hours} м/ч).",
        "Акт приёмки: {category} {brand} {model} передан от {from_dept} к {to_dept}. Состояние: {condition}. Наработка: {hours} м/ч.",
        "Норматив выработки: {category} {brand} {model} должен выполнять не менее {output_norm} м³ за смену в условиях {les_area_type}.",
        "Мобильное приложение зафиксировало: оператор {user_id} завершил работу на {category} {brand} {model}. Выполнено задач: {tasks_completed}.",
        "Согласно СТО, интервал ТО для {category} {brand} {model} — каждые {service_interval} м/ч при интенсивной эксплуатации.",
        "Данные по экологичности: выбросы {category} {brand} {model} соответствуют нормам при использовании топлива {fuel_grade}.",
        "Лог перемещений: {category} {brand} {model} переведён из {location_from} в {location_to} для выполнения задачи «{task_description}».",
        "Анализ парка: доля техники типа {category} марки {brand} (модель {model}) составляет {share_percent}% от общего количества единиц.",
        "Протокол осмотра: у {category} {brand} {model} проверены гидравлика, КПП и кабина. Замечаний нет. Состояние: {state}.",
        "Сертификат соответствия №{cert_id} выдан на технику {brand} {model} с двигателем {engine_desc}.",
        "В руководстве по эксплуатации {brand} {model} указано: максимальная грузоподъёмность — {loading_weight}.",
        "Лог системы мониторинга: у {brand} {model} зафиксировано падение давления в гидросистеме до {hydraulic_pressure} бар.",
        "Оператор {operator_name} отметил в отчёте: «{brand} {model} работает без сбоев, но требует регулировки КПП после {motochasi_value} м/ч.»",
        "Согласно СТО, интервал замены масла для {brand} {model} — каждые {oil_change_interval} м/ч при работе в {les_area_type}.",
        "В CRM зарегистрирован простой {brand} {model} на {downtime_hours} часов из-за поломки {component_name}.",
        "Данные телематики: {brand} {model} находился в зоне {coordinates} с {start_time} по {end_time}.",
        "Акт диагностики: у {brand} {model} выявлен износ подшипников стрелы. Рекомендовано ТО при {next_service_hours} м/ч.",
        "Норма расхода топлива для {brand} {model} в условиях {les_work_site}: {fuel_consumption_norm} л/м/ч.",
        "Инвентарная карточка №{inventory_num}: {brand} {model}, VIN {vin}, владелец — {owner_org}.",
        "Протокол испытаний: {brand} {model} выдержал нагрузку {load_test_value} в течение {test_duration} часов.",
        "Заметка инженера: «{brand} {model} — надёжная техника, но требует усиленного контроля {critical_component} после {inspection_threshold} м/ч.»",
        "Лог переписки: «Поддерживает ли {brand} {model} навесное оборудование {attachment_type}?» — «Да, при условии {compatibility_condition}.»",
        "Аналитика эффективности: {brand} {model} показал производительность {output_rate} м³/ч при выполнении {task_type}.",
        "Данные ГСМ: за смену {brand} {model} израсходовал {fuel_liters} литров топлива при наработке {hours} м/ч.",
        "Внутреннее распоряжение: с сегодняшнего дня {brand} {model} должен эксплуатироваться только с {safety_feature}.",
        "Статистика отказов: у {brand} {model} чаще всего выходит из строя {failing_part} (средний ресурс: {mtbf_hours} м/ч).",
        "Сервисный отчёт: выполнена замена фильтров на {brand} {model} при наработке {motochasi_value} м/ч.",
        "Руководство по ТБ: запрещено использовать {brand} {model} без {protective_equipment} на склонах круче {max_slope}°.",
        "Архивная запись: {brand} {model} числится в парке с текущей наработкой {hours} м/ч. Ответственный: {operator_name}.",
        "Данные GPS: средняя скорость {brand} {model} в районе {work_zone} — {avg_speed} км/ч.",
        "Сравнительный анализ: {brand} {model} на {efficiency_percent}% эффективнее аналогов при работе в {les_task_type}.",
        "Протокол осмотра: у {brand} {model} проверены ходовая, гидравлика и кабина. Замечаний нет. Состояние: {condition}.",
        "Лог перемещений: {brand} {model} переведён из {location_from} в {location_to} для выполнения задачи «{task_description}».",
        "Норматив выработки: {brand} {model} должен выполнять не менее {output_norm} м³ за смену в условиях {les_area_type}.",
        "Мобильное приложение зафиксировало: оператор {user_id} завершил смену на {brand} {model}. Выполнено: {tasks_completed} операций.",
        "Данные по экологичности: выбросы {brand} {model} соответствуют нормам Евро-{euro_class} при использовании топлива {fuel_grade}.",
        "Акт приёмки-передачи: {brand} {model} передан от {from_dept} к {to_dept}. Наработка: {hours} м/ч. Состояние: {state}.",
        "Анализ парка: доля техники {brand} {model} составляет {market_share}% от общего количества единиц в категории {machine_type}.",
        "Замечание инспектора: у {brand} {model} отсутствует маркировка {safety_label}, требуется устранение до {deadline_date}.",
        "В парке зарегистрирован {category} {brand} {model}. VIN: {vin}. Ответственный оператор: {operator_name}. Текущая наработка: {hours} м/ч.",
        "Сервисный журнал: у {category} {brand} {model} выполнена замена масла в двигателе {engine_desc} при наработке {motochasi_value} м/ч.",
        "Техническое описание: {category} {brand} {model} предназначен для выполнения задач типа {les_task_type} в условиях {les_area_type}.",
        "Лог мониторинга: {category} {brand} {model} зафиксировал перегрев гидросистемы при температуре {hydraulic_temp}°C.",
        "Инвентарная запись №{inventory_id}: {category} — {brand} {model}, двигатель {engine_power} л.с., объём {engine_volume}.",
        "Акт диагностики: у {category} {brand} {model} выявлен износ ходовой части. Рекомендовано ТО при достижении {next_service_hours} м/ч.",
        "В CRM обновлён статус: {category} {brand} {model} переведён в режим «ограниченная эксплуатация» из-за неисправности {failed_component}.",
        "Норма расхода топлива для {category} {brand} {model} в условиях {les_work_site}: {fuel_norm} л/м/ч.",
        "Оператор {operator_name} отметил: «{category} {brand} {model} работает стабильно, но требует регулировки стрелы после {motochasi_value} м/ч.»",
        "Сравнительный отчёт: {category} {brand} {model} показал на {efficiency_gain}% выше производительность, чем аналоги при задаче «{task_type}».",
        "Данные GPS-трекера: {category} {brand} {model} находился в районе {coordinates} в течение {duration_hours} ч.",
        "Протокол испытаний: {category} {brand} {model} выдержал нагрузку {load_value} без сбоев в системе {system_name}.",
        "Запись в журнале ГСМ: {category} {brand} {model} израсходовал {fuel_consumption} л топлива за смену.",
        "Руководство по ТБ: запрещено использовать {category} {brand} {model} без {safety_equipment} при работе на склонах круче {slope_deg}°.",
        "Аналитика простоев: {category} {brand} {model} простаивал {downtime_days} дней из-за отсутствия запчасти {spare_part_name}.",
        "Сертификат соответствия №{cert_id} выдан на {category} {brand} {model} с двигателем, соответствующим Евро-{euro_class}.",
        "Лог переписки: «Поддерживает ли {category} {brand} {model} гидромолот {attachment_model}?» — «Да, при давлении до {max_pressure} бар.»",
        "Архивная карточка: {category} {brand} {model} числится в парке с наработкой {motochasi_value} м/ч. Владелец: {owner_org}.",
        "Заметка инженера: «{category} {brand} {model} — надёжный, но требует усиленного контроля {component_name} после {inspection_threshold} м/ч.»",
        "Данные телематики: средняя скорость {category} {brand} {model} в зоне {work_zone} — {avg_speed} км/ч при наработке {hours} м/ч.",
        "Внутреннее распоряжение: с сегодняшнего дня {category} {brand} {model} должен эксплуатироваться только с дополнительной защитой {protection_type}.",
        "Статистика отказов: у {category} {brand} {model} чаще всего выходит из строя {weak_component} (средний ресурс: {mtbf_hours} м/ч).",
        "Акт приёмки: {category} {brand} {model} передан от {from_dept} к {to_dept}. Состояние: {condition}. Наработка: {hours} м/ч.",
        "Норматив выработки: {category} {brand} {model} должен выполнять не менее {output_norm} м³ за смену в условиях {les_area_type}.",
        "Мобильное приложение зафиксировало: оператор {user_id} завершил работу на {category} {brand} {model}. Выполнено задач: {tasks_completed}.",
        "Согласно СТО, интервал ТО для {category} {brand} {model} — каждые {service_interval} м/ч при интенсивной эксплуатации.",
        "Данные по экологичности: выбросы {category} {brand} {model} соответствуют нормам при использовании топлива {fuel_grade}.",
        "Лог перемещений: {category} {brand} {model} переведён из {location_from} в {location_to} для выполнения задачи «{task_description}».",
        "Анализ парка: доля техники типа {category} марки {brand} (модель {model}) составляет {share_percent}% от общего количества единиц.",
        "Протокол осмотра: у {category} {brand} {model} проверены гидравлика, КПП и кабина. Замечаний нет. Состояние: {state}.",
        "По данным системы учёта, {category} {brand} {model} имеет средний ресурс двигателя {engine_desc} — {avg_engine_life} м/ч.",
        "В протоколе совещания указано: рекомендовано стандартизировать парк на {category} {brand} {model} из-за низкого уровня простоев.",
        "Журнал ТО №{service_log_id}: у {category} {brand} {model} заменены фильтры гидравлики при наработке {motochasi_value} м/ч.",
        "Согласно внутреннему стандарту {company_std}, {category} {brand} {model} должен проходить диагностику каждые {diagnostic_interval} м/ч.",
        "Лог датчика вибрации: у {category} {brand} {model} зафиксировано превышение допустимого уровня на {vibration_excess}% при {engine_load}% нагрузки.",
        "Анализ ГСМ за {month}: {category} {brand} {model} показал фактический расход {actual_fuel} л/м/ч против нормы {norm_fuel} л/м/ч.",
        "Запись в электронной карте техники: {category} {brand} {model}, серийный номер {serial_number}, текущее местоположение — {current_location}.",
        "Рекомендация по модернизации: установка системы {upgrade_kit} на {category} {brand} {model} повышает надёжность на {reliability_gain}%.",
        "Данные по безопасности: за {period} у {category} {brand} {model} не зафиксировано аварийных ситуаций. Состояние систем: {safety_status}.",
        "В отчёте инспектора: {category} {brand} {model} соответствует требованиям по шуму и вибрации в кабине (уровень: {noise_level} дБ).",
        "Лог запроса запчастей: для {category} {brand} {model} заказан {part_name} (артикул {part_number}) в связи с износом на {motochasi_value} м/ч.",
        "Нормативная производительность {category} {brand} {model} при работе в {les_work_site}: {productivity_rate} м³/ч.",
        "Заметка в техкарте: у {category} {brand} {model} наблюдается повышенный износ гусениц при эксплуатации в {terrain_type}.",
        "Данные мониторинга: {category} {brand} {model} находился в режиме простоя {idle_hours} ч из-за ожидания погрузки.",
        "Протокол калибровки: датчики навигации на {category} {brand} {model} откалиброваны. Точность: ±{accuracy_meters} м.",
        "Внутренний аудит: {category} {brand} {model} имеет полный комплект документации и маркировки согласно {regulation_ref}.",
        "Статистика по отказам за {quarter}: у {category} {brand} {model} зафиксировано {failure_count} инцидентов с системой {system_name}.",
        "Руководство оператора: при работе на {category} {brand} {model} запрещено превышать угол крена {max_roll_angle}°.",
        "Акт списания запчастей: для ТО {category} {brand} {model} израсходованы {consumables_list} на сумму {spare_cost} руб.",
        "Лог доступа: оператор {operator_id} авторизован для управления {category} {brand} {model} с {access_start} по {access_end}.",
        "Анализ эффективности: {category} {brand} {model} обеспечивает на {uptime_percent}% больше наработки в сутки по сравнению с предыдущей моделью.",
        "Запись в системе обучения: оператор {trainee_name} прошёл курс по эксплуатации {category} {brand} {model}. Дата завершения: {completion_date}.",
        "Данные по износу: ресурс стрелы у {category} {brand} {model} оценивается в {boom_life_hours} м/ч при работе в {work_intensity} режиме.",
        "Протокол испытаний на холодный пуск: {category} {brand} {model} запустился при температуре {cold_start_temp}°C без посторонней помощи.",
        "В отчёте по экологии: выбросы NOx у {category} {brand} {model} составляют {nox_emission} г/кВт·ч, что ниже нормы на {emission_margin}%.",
        "Лог обновления ПО: на {category} {brand} {model} установлена версия {software_version} системы управления. Дата: {update_date}.",
        "Рекомендация по хранению: при простое более {storage_days} дней {category} {brand} {model} должен быть законсервирован по инструкции {conservation_guide}.",
        "Данные по совместимости: навесное оборудование {attachment_brand} {attachment_model} сертифицировано для {category} {brand} {model}.",
        "Анализ топливной эффективности: {category} {brand} {model} потребляет на {fuel_saving_percent}% меньше топлива при том же объёме работ.",
        "Запись в журнале инцидентов: у {category} {brand} {model} зафиксирован ложный срабатывание датчика {sensor_type} в {incident_time}.",
        "Сертификат на соответствие требованиям безопасности выдан для {brand} {model} категории {category}.",
        "В базе техники зарегистрировано: {brand} {model}, тип — {category}. VIN: {vin}. Наработка: {hours} м/ч.",
        "По результатам испытаний, {brand} {model} ({category}) выдержал нагрузку {load_test_value} без деформаций несущих узлов.",
        "Лог системы диагностики: у {brand} {model} ({category}) зафиксировано снижение давления в контуре гидравлики до {hydraulic_pressure} бар.",
        "Нормативный документ №{doc_id} регламентирует эксплуатацию {brand} {model} в классе техники «{category}» при температуре до {min_temp}°C.",
        "Оператор отметил: «{brand} {model} ({category}) требует регулировки гидрораспределителя после {motochasi_value} м/ч работы.»",
        "В отчёте по ТО указано: замена масла в редукторе выполнена на {brand} {model} ({category}) при наработке {service_hours} м/ч.",
        "Анализ простоев показал: {brand} {model} категории {category} простаивал из-за неисправности {component_name} в течение {downtime_hours} ч.",
        "Данные телематики: {brand} {model} ({category}) находился в зоне {work_zone} с {start_time} по {end_time}. Средняя наработка в сутки: {avg_daily_hours} м/ч.",
        "Согласно внутреннему стандарту, {brand} {model} ({category}) должен проходить инспекцию ходовой каждые {inspection_interval} м/ч.",
        "В журнале ГСМ зафиксирован расход топлива {fuel_consumption} л/м/ч для {brand} {model} категории {category} в условиях {terrain_type}.",
        "Протокол калибровки: система навигации на {brand} {model} ({category}) откалибрована с точностью ±{gps_accuracy} м.",
        "Запись в CRM: статус {brand} {model} ({category}) изменён на «готов к работе» после замены {replaced_part}.",
        "Руководство по эксплуатации: максимальная скорость передвижения {brand} {model} категории {category} — {max_speed} км/ч.",
        "Лог запроса запчастей: для {brand} {model} ({category}) заказан {part_name} (артикул {part_number}) в связи с износом.",
        "Акт осмотра: у {brand} {model} категории {category} проверены тормоза, гидравлика и кабина. Замечаний нет. Состояние: {condition}.",
        "Статистика надёжности: средний интервал между отказами у {brand} {model} ({category}) — {mtbf_hours} м/ч.",
        "Внутреннее распоряжение: с {effective_date} разрешено использовать {brand} {model} категории {category} только с {safety_attachment}.",
        "Данные по экологичности: уровень шума кабины {brand} {model} ({category}) — {cabin_noise} дБ, что соответствует норме.",
        "Анализ эффективности: {brand} {model} категории {category} выполняет {output_norm} м³/ч при работе в {les_area_type}.",
        "Лог переписки: «Поддерживает ли ПО версию {software_version} на {brand} {model} ({category})?» — «Да, с обновлением до {required_update}.»",
        "Заметка инженера: «{brand} {model} ({category}) демонстрирует повышенный износ гусениц на каменистом грунте.»",
        "Протокол хранения: при простое более {storage_days} дней {brand} {model} категории {category} должен быть законсервирован.",
        "Данные мониторинга: температура масла в двигателе {brand} {model} ({category}) не превышала {max_oil_temp}°C в течение смены.",
        "В отчёте по обучению: оператор {operator_name} прошёл инструктаж по управлению {brand} {model} категории {category}.",
        "Анализ совместимости: навесное оборудование {attachment_model} сертифицировано для {brand} {model} ({category}).",
        "Лог инцидентов: у {brand} {model} категории {category} зафиксирован ложный срабатывание датчика {sensor_type} в {timestamp}.",
        "Норма выработки: {brand} {model} ({category}) должен выполнять не менее {min_output} м³ за смену в условиях {work_conditions}.",
        "Запись в архиве: {brand} {model} категории {category} числится в парке с {acquisition_date}. Текущая наработка: {hours} м/ч.",
        "Рекомендация по модернизации: установка {upgrade_kit} на {brand} {model} ({category}) повышает производительность на {efficiency_gain}%.",
        "В реестре парка значится: {brand} {model}, класс техники — {category}. Ответственный: {operator_name}.",
        "Система мониторинга зафиксировала перегрев трансмиссии у {brand} {model} ({category}) при нагрузке {load_percent}%.",
        "По данным аналитики, {brand} {model} категории {category} имеет на {reliability_index}% выше индекс надёжности по сравнению с аналогами.",
        "Журнал ТО: на {brand} {model} ({category}) выполнена замена ремней привода при наработке {motochasi_value} м/ч.",
        "Внутренний стандарт №{std_id} регламентирует допустимый износ гусениц для {brand} {model} категории {category}.",
        "Оператор сообщил: «{brand} {model} ({category}) требует балансировки колёс после {hours} м/ч эксплуатации в {terrain_type}.»",
        "Протокол диагностики: у {brand} {model} категории {category} выявлено снижение компрессии в цилиндре №{cylinder_num}.",
        "Данные по топливной экономичности: {brand} {model} ({category}) потребляет {fuel_rate} л/м/ч при средней нагрузке.",
        "Лог обновления прошивки: на {brand} {model} категории {category} установлена версия ПО {firmware_version}.",
        "Акт приёмки после ремонта: {brand} {model} ({category}) возвращён в эксплуатацию. Заменены: {replaced_components}.",
        "Норматив по шуму: уровень в кабине {brand} {model} категории {category} не должен превышать {noise_limit} дБ.",
        "Запись в системе обучения: оператор {trainee_id} завершил курс по управлению {brand} {model} ({category}).",
        "Анализ износа: ресурс гидромотора у {brand} {model} категории {category} оценивается в {hydromotor_life} м/ч.",
        "Лог запроса на ТО: запланировано обслуживание {brand} {model} ({category}) на {scheduled_date} при наработке ~{planned_hours} м/ч.",
        "Сертификат на навесное оборудование: {attachment_name} совместим с {brand} {model} категории {category}.",
        "Данные по вибрации: RMS-уровень на стреле {brand} {model} ({category}) — {vibration_rms} мм/с, в пределах нормы.",
        "В отчёте по экологии: выбросы CO₂ у {brand} {model} категории {category} составляют {co2_emission} г/кВт·ч.",
        "Рекомендация инженера: усилить защиту днища у {brand} {model} ({category}) при работе в условиях {work_environment}.",
        "Лог инцидентов: у {brand} {model} категории {category} зафиксирован сбой в CAN-шине в {incident_time}.",
        "Норма производительности: {brand} {model} ({category}) должен обрабатывать не менее {min_throughput} м³/ч в {les_task_type}.",
        "Запись в архиве техники: {brand} {model}, тип — {category}, серийный номер — {serial_number}, текущее состояние — {state}.",
        "Протокол испытаний на устойчивость: {brand} {model} категории {category} выдержал крен {tilt_angle}° без опрокидывания.",
        "Данные по простою: {brand} {model} ({category}) не эксплуатировался {idle_days} дней из-за отсутствия оператора.",
        "Внутреннее уведомление: с {effective_date} все {brand} {model} категории {category} должны быть оснащены {mandatory_equipment}.",
        "Анализ совместимости масел: рекомендовано использовать {oil_spec} для двигателя {brand} {model} ({category}).",
        "Лог калибровки датчиков: на {brand} {model} категории {category} откалиброваны датчики угла поворота стрелы.",
        "Отчёт по безопасности: за {period} у {brand} {model} ({category}) не зафиксировано нарушений правил эксплуатации.",
        "Заметка в техкарте: {brand} {model} категории {category} имеет усиленную раму, что увеличивает ресурс на {frame_life_gain}%.",
        "Данные GPS-трекинга: маршрут {brand} {model} ({category}) включал {waypoints_count} точек в зоне {work_area}.",
        "Протокол хранения: при консервации {brand} {model} категории {category} требуется заполнение системы антифризом {antifreeze_type}.",
        "Наработка: {hours} м/ч. Цена: {price}.",
        "Моточасы — {hours}. Стоимость: {price}.",
        "Техника с наработкой {hours} моточасов. Цена указана: {price}.",
        "Всего {hours} м/ч на двигателе. Отдам за {price}.",
        "Цена снижена! Всего {hours} моточасов. Берите за {price}.",
        "Реальный пробег по моточасам: {hours}. Цена: {price}.",
        "Не гонял — всего {hours} м/ч. Цена: {price}.",
        "Стоимость — {price}. Наработка — {hours} моточасов.",
        "Отличное состояние! Всего {hours} м/ч. Цена: {price}.",
        "Цена: {price}. Моточасы: {hours}.",
        "Продаю с наработкой {hours} м/ч. Цена фиксирована: {price}.",
        "Всего {hours} моточасов. Цена — {price}, торг неуместен.",
        "Наработка по моточасам: {hours}. Цена: {price}.",
        "Цена {price} за технику с {hours} моточасами.",
        "Моточасы: {hours}. Цена: {price}. Собственник.",
        "Всего {hours} м/ч. Цена — {price}. Звонить до 21:00.",
        "Цена: {price}. Моточасов: {hours}. Без посредников!",
        "Техника с {hours} моточасами. Цена: {price}.",
        "Наработка — {hours} м/ч. Цена: {price}. Возможна доставка.",
        "Всего {hours} моточасов. Цена: {price}. Срочно!",
        "Цена: {price}. Моточасы — {hours}. Документы в порядке.",
        "Моточасы: {hours}. Цена: {price}. Под ключ.",
        "Наработка {hours} м/ч. Цена — {price}. Торг уместен.",
        "Цена: {price}. Всего {hours} моточасов. Проверено лично.",
        "Моточасы — {hours}. Цена: {price}. Не для перепродажи.",
        "Всего {hours} м/ч. Цена: {price}. Гарантия на двигатель.",
        "Цена: {price}. Наработка: {hours} моточасов. Возможен обмен.",
        "Моточасы: {hours}. Цена: {price}. Только серьёзным покупателям.",
        "Наработка — {hours} м/ч. Цена: {price}. Всё работает.",
        "Цена: {price}. Моточасов: {hours}. Реальному покупателю.",
        "Всего {hours} моточасов. Цена — {price}.",
        "Наработка: {hours} м/ч. Стоимость: {price}.",
        "Цена {price} при наработке {hours} моточасов.",
        "Моточасы — {hours}. Отдам за {price}.",
        "Техника с {hours} м/ч. Цена: {price}.",
        "Всего {hours} моточасов на двигателе. Цена: {price}.",
        "Цена: {price}. Моточасов — {hours}.",
        "Наработка по моточасам: {hours}. Цена фиксирована — {price}.",
        "Моточасы: {hours}. Цена: {price}. Без торга.",
        "Всего {hours} м/ч. Цена — {price}, реальному покупателю.",
        "Цена: {price}. Наработка — {hours} моточасов. Собственник.",
        "Моточасы — {hours}. Цена: {price}. Документы оригиналы.",
        "Наработка: {hours} моточасов. Цена снижена до {price}!",
        "Цена: {price}. Всего {hours} м/ч. Проверено в работе.",
        "Моточасы: {hours}. Цена: {price}. Возможна рассрочка.",
        "Всего {hours} моточасов. Цена — {price}. Забирайте быстро!",
        "Цена: {price}. Моточасы — {hours}. Не битая, не крашеная.",
        "Наработка — {hours} м/ч. Цена: {price}. Подходит для аренды.",
        "Моточасы: {hours}. Цена: {price}. Техника в работе до сих пор.",
        "Всего {hours} моточасов. Цена — {price}. Без долгов и залогов.",
        "Цена: {price}. Наработка: {hours} м/ч. Готов к работе.",
        "Моточасы — {hours}. Цена: {price}. Только до конца недели.",
        "Наработка: {hours} моточасов. Цена: {price}. Пишите в Telegram.",
        "Всего {hours} м/ч. Цена — {price}. Не упусти шанс!",
        "Цена: {price}. Моточасов — {hours}. Состояние — как новое.",
        "Моточасы: {hours}. Цена: {price}. Подходит для лесозаготовки.",
        "Наработка — {hours} моточасов. Цена: {price}. Срочная продажа!",
        "Всего {hours} м/ч. Цена — {price}. Все узлы в норме.",
        "Цена: {price}. Моточасы — {hours}. Возможен обмен на недвижимость.",
        "Моточасы: {hours}. Цена: {price}. Гарантия 30 дней.",
        "Всего {hours} м/ч. Цена — {price}.",
        "Наработка: {hours} моточасов. Цена: {price}.",
        "Цена {price} при {hours} моточасах.",
        "Моточасы — {hours}. Беру {price}.",
        "Техника с наработкой {hours} м/ч. Цена: {price}.",
        "Всего {hours} моточасов на счету. Цена — {price}.",
        "Цена: {price}. Моточасов — {hours}.",
        "Наработка по тахометру: {hours} м/ч. Цена: {price}.",
        "Моточасы: {hours}. Цена: {price}. Без посредников.",
        "Всего {hours} м/ч. Цена — {price}, торг при осмотре.",
        "Цена: {price}. Наработка — {hours} моточасов. Собственник.",
        "Моточасы — {hours}. Цена: {price}. Документы в порядке.",
        "Наработка: {hours} моточасов. Цена снижена до {price}!",
        "Цена: {price}. Всего {hours} м/ч. Проверено лично.",
        "Моточасы: {hours}. Цена: {price}. Возможна доставка по РФ.",
        "Всего {hours} моточасов. Цена — {price}. Звонить с 9 до 20.",
        "Цена: {price}. Моточасов — {hours}. Не для перекупов.",
        "Наработка — {hours} м/ч. Цена: {price}. Под ключ.",
        "Моточасы: {hours}. Цена: {price}. Техника в работе каждый день.",
        "Всего {hours} моточасов. Цена — {price}. Без долгов.",
        "Цена: {price}. Наработка: {hours} м/ч. Готов к работе сразу.",
        "Моточасы — {hours}. Цена: {price}. Только до конца месяца.",
        "Наработка: {hours} моточасов. Цена: {price}. Пишите в WhatsApp.",
        "Всего {hours} м/ч. Цена — {price}. Не гниёт в гараже!",
        "Цена: {price}. Моточасов — {hours}. Состояние — отличное.",
        "Моточасы: {hours}. Цена: {price}. Подходит для стройки.",
        "Наработка — {hours} моточасов. Цена: {price}. Срочно! Звоните!",
        "Всего {hours} м/ч. Цена — {price}. Все работает исправно.",
        "Цена: {price}. Моточасы — {hours}. Возможен обмен.",
        "Моточасы: {hours}. Цена: {price}. Гарантия на двигатель 2 недели.",
        "{hours} моточасов — реальные. Цена: {price}.",
        "Цена {price}. Наработка: {hours} м/ч (по сервисной книжке).",
        "Моточасы: {hours}. Цена — {price}, только наличка.",
        "Всего {hours} м/ч. Цена: {price}. Без лишних вопросов.",
        "Наработка — {hours}. Цена: {price}. Звоните — покажу в работе.",
        "Цена: {price}. Моточасов — {hours}. Не для гаража!",
        "Моточасы: {hours}. Цена: {price}. Подходит для карьера.",
        "Всего {hours} м/ч. Цена — {price}. Торг только при осмотре.",
        "Цена: {price}. Наработка: {hours} моточасов. Срочно нужен ремонт?",
        "Моточасы — {hours}. Цена: {price}. Реальному пользователю.",
        "Наработка: {hours} м/ч. Цена: {price}. Не дилер, не фирма.",
        "Цена {price}. Моточасов — {hours}. Всё живое — работает!",
        "Моточасы: {hours}. Цена: {price}. Подходит для проката.",
        "Всего {hours} моточасов. Цена — {price}. Не тронута после ТО.",
        "Цена: {price}. Наработка — {hours} м/ч. Возможен лизинг.",
        "Моточасы — {hours}. Цена: {price}. Забирай — не греши!",
        "Наработка: {hours} моточасов. Цена: {price}. Только серьёзно.",
        "Цена: {price}. Моточасов — {hours}. Не китай, не самосбор.",
        "Моточасы: {hours}. Цена: {price}. Подходит для стройки и леса.",
        "Всего {hours} м/ч. Цена — {price}. ПТС оригинал, без залогов.",
        "Цена: {price}. Наработка: {hours} моточасов. Не греет, не дымит.",
        "Моточасы — {hours}. Цена: {price}. Под ключ, всё работает.",
        "Наработка: {hours} м/ч. Цена: {price}. Для тех, кто знает толк.",
        "Цена {price}. Моточасов — {hours}. Не ржавый гаражный экземпляр.",
        "Моточасы: {hours}. Цена: {price}. Подходит для нового бизнеса.",
        "Всего {hours} моточасов. Цена — {price}. Один владелец, не фирма.",
        "Цена: {price}. Наработка — {hours} м/ч. Гидравлика, стрела — ОК.",
        "Моточасы — {hours}. Цена: {price}. Подходит для демонстрации.",
        "Наработка: {hours} моточасов. Цена: {price}. Не для перепродажи!",
        "Цена: {price}. Моточасов — {hours}. Всё как на фото (если бы было).",
        "Наработка: {hours} м/ч. Цена — {price}. Не тратьте время — звоните!",
        "Моточасы — {hours}. Цена: {price}. Техника не простаивает — работает ежедневно.",
        "Всего {hours} моточасов. Цена: {price}. Подходит даже для новичка.",
        "Цена: {price}. Наработка — {hours} м/ч. Не упусти — таких больше нет!",
        "Моточасы: {hours}. Цена: {price}. Заберёте — не пожалеете.",
        "Наработка: {hours} м/ч. Цена — {price}. Без скрытых дефектов.",
        "Цена: {price}. Моточасов — {hours}. Работает как часы.",
        "Моточасы — {hours}. Цена: {price}. Подходит для тяжёлых условий.",
        "Всего {hours} моточасов. Цена: {price}. Не для перекупщиков — только в работу!",
        "Цена: {price}. Наработка — {hours} м/ч. Всё проверено лично.",
        "Моточасы: {hours}. Цена: {price}. Можно оформить в лизинг.",
        "Наработка: {hours} м/ч. Цена — {price}. Документы чистые, без обременений.",
        "Цена: {price}. Моточасов — {hours}. Не греет, не стучит, не дымит.",
        "Моточасы — {hours}. Цена: {price}. Подходит для коммунальных работ.",
        "Всего {hours} моточасов. Цена: {price}. Реальному покупателю — быстрый выезд!"
    ]

    current_data_set: List[str] = read_data_set_as_list('vehicle_advertisement_templates_v4')
    current_data_set = merge_with_other_list(current_data_set, items)
    print_classes_statistics(current_data_set)


    # current_data_set.extend(items)
    # data_unique = set(current_data_set)
    # data_list = list(data_unique)
    # write_list_to_csv_file('vehicle_advertisement_templates_v5', data_list)


    return []




