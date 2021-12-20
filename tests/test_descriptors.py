"""
Testing validators descriptors
Command line: py -m tests/test_descriptors.py
"""

import pytest
import datetime
from utils.descriptors import FutureDate, RealNumber


@pytest.fixture
def input_data_real_number():
    return {
        "min_value": -10,
        "max_value": 100,
        "sterilize_attr": ["_BS", "_MC"]
    }


@pytest.fixture
def instance_class_real_number(input_data_real_number):
    obj = type("TestClassRN", (), {"price": RealNumber(**input_data_real_number)})
    instance = obj()
    instance._BS = 100
    instance._MC = 20
    return instance


def test_rn_descriptor_param(instance_class_real_number, input_data_real_number):
    for attr_name, attr_value in input_data_real_number.items():
        assert type(instance_class_real_number).__dict__["price"].__dict__[attr_name] == attr_value


@pytest.mark.parametrize("value", [15, 15.5])
def test_valid_rn_attr(instance_class_real_number, value):
    instance_class_real_number.price = value
    assert instance_class_real_number.price == value


@pytest.mark.parametrize("value, error", [(-12, ValueError), ("10", TypeError), (101, ValueError)])
def test_invalid_rn_attr(instance_class_real_number, value, error):
    with pytest.raises(error):
        instance_class_real_number.price = value


def test_sterilize_rn_attr(instance_class_real_number):
    assert instance_class_real_number._BS == 100
    assert instance_class_real_number._MC == 20
    instance_class_real_number.price = 15
    assert instance_class_real_number._BS is None
    assert instance_class_real_number._MC is None


@pytest.fixture
def input_data_future_date():
    return {
        "date_format": "%Y-%m-%d",
        "sterilize_attr": ["_BS", "_MC"]
    }


@pytest.fixture
def instance_class_future_date(input_data_future_date):
    obj = type("TestClassFD", (), {"maturity": FutureDate(**input_data_future_date)})
    instance = obj()
    instance._BS = 100
    instance._MC = 20
    return instance


def test_fd_descriptor_param(instance_class_future_date, input_data_future_date):
    for attr_name, attr_value in input_data_future_date.items():
        assert type(instance_class_future_date).__dict__["maturity"].__dict__[attr_name] == attr_value


@pytest.mark.parametrize("date", ["2025-01-01", datetime.date(2025, 1, 1), datetime.datetime(2025, 1, 1, 0, 0, 0)])
def test_valid_fd_attr(instance_class_future_date, date):
    instance_class_future_date.maturity = date
    if isinstance(date, datetime.datetime):
        assert instance_class_future_date.maturity == date.date()
    elif isinstance(date, datetime.date):
        assert instance_class_future_date.maturity == date
    else:
        assert instance_class_future_date.maturity == datetime.datetime.strptime(date, "%Y-%m-%d").date()


@pytest.mark.parametrize("date", ["1 January 2025", "2020-01-01", datetime.date(2020, 1, 1),
                                  datetime.datetime(2020, 1, 1, 0, 0, 0)])
def test_invalid_fd_attr(instance_class_future_date, date):
    with pytest.raises(ValueError):
        instance_class_future_date.maturity = date


def test_sterilize_fd_attr(instance_class_future_date):
    assert instance_class_future_date._BS == 100
    assert instance_class_future_date._MC == 20
    instance_class_future_date.maturity = "2025-01-01"
    assert instance_class_future_date._BS is None
    assert instance_class_future_date._MC is None
