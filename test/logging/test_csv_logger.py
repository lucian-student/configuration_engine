from configuration_engine.logging import CSVStringLogger
from test.fixtures.logging.csv_logger import basic_data
import csv
from io import StringIO
import pytest


def parse_csv_with_types(content, type_map):
    f = StringIO(content)
    reader = csv.DictReader(f)
    result = []
    for row in reader:
        typed_row = {}
        for key, value in row.items():
            if key in type_map:
                typed_row[key] = type_map[key](value)
            else:
                typed_row[key] = value
        result.append(typed_row)
    return result


def test_csv_logger(basic_data):

    type_map = {}
    for key, val in basic_data[0].items():
        type_map[key] = type(val)

    logger = CSVStringLogger()
    for data in basic_data:
        logger.log(data)
    content = logger.stream().getvalue()
    actual_data = parse_csv_with_types(content, type_map)
    for actual, expected in zip(actual_data, basic_data):
        assert actual.keys() == expected.keys(), "Key mismatch"
        for key in actual:
            if isinstance(expected[key], float):
                assert actual[key] == pytest.approx(
                    expected[key], abs=1e-8
                ), f"Mismatch at key '{key}'"
            else:
                assert actual[key] == expected[key], f"Mismatch at key '{key}'"
