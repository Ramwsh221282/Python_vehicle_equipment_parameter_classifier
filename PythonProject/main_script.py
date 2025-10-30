import csv
from collections import Counter
from DataSetSource import *

def main():
    dataset: list[tuple[str, str]] = create_engine_type_dataset()
    print_dataset_class_distribution_levels(dataset)
    print_has_duplicates(dataset, has_duplicates)
    save_in_csv(dataset, 'engine_types.csv')


if __name__ == '__main__':
    main()
