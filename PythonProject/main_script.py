import csv
from collections import Counter
from DataSetSource import create_engine_type_dataset

def main():
    # загрузка датасета
    dataSet = create_engine_type_dataset()

    labels = [label for _, label in dataSet]
    label_counts = Counter(labels)

    # анализ распределения классов двигателей
    for label, count in sorted(label_counts.items()):
        percentage = count / len(labels)
        print(f"{label:<12} | {count:>3} | {percentage:>5.1f}%")
    print("-" * 30)
    print(f"ИТОГО | {len(dataSet):>3} | 100.0%")



