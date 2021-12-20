"""
Testing creation of Option class and methods
Command line: py -m pytest tests/test_option_class.py
"""
import math
import pytest
from option_class import Option
import datetime
from utils.webdriver import get_value_from_the_web


@pytest.fixture
def input_data():
    return {
        "price": 100,
        "strike": 110,
        "maturity": "2025-01-01",
        "risk_free_rate": 0.001,
        "volatility": 0.2,
        "dividend_yield": 0
    }


@pytest.fixture
def option_instance(input_data):
    return Option(**input_data)


@pytest.fixture
def ref_value(input_data):
    return get_value_from_the_web(input_data)


def test_option_attr(option_instance, input_data):
    input_data["maturity"] = datetime.date(2025, 1, 1)
    for attr_name, attr_value in input_data.items():
        assert getattr(option_instance, attr_name) == attr_value
    for attr in type(option_instance)._LAZY_ATTR:
        assert getattr(option_instance, attr) is None


def test_black_scholes_method_no_div(option_instance, input_data, ref_value):
    c, p = option_instance.black_scholes_price()
    assert math.isclose(round(c, 2), ref_value["call_price"], rel_tol=0.01, abs_tol=0.01)
    assert math.isclose(round(p, 2), ref_value["put_price"], rel_tol=0.01, abs_tol=0.01)


def test_black_scholes_method_with_div(input_data):
    input_data["dividend_yield"] = 0.03
    option_instance = Option(**input_data)
    c, p = option_instance.black_scholes_price()
    ref_value = get_value_from_the_web(input_data)
    assert math.isclose(round(c, 2), ref_value["call_price"], rel_tol=0.01, abs_tol=0.01)
    assert math.isclose(round(p, 2), ref_value["put_price"], rel_tol=0.01, abs_tol=0.01)


def test_sterilize_attr_bs(option_instance, input_data):
    _ = option_instance.black_scholes_price()
    option_instance.strike = 120
    assert option_instance.strike == 120
    assert option_instance._BS_price is None
    assert option_instance._MC_price is None
    c, p = option_instance.black_scholes_price()
    input_data["strike"] = 120
    ref_value = get_value_from_the_web(input_data)
    assert math.isclose(round(c, 2), ref_value["call_price"], rel_tol=0.01, abs_tol=0.01)
    assert math.isclose(round(p, 2), ref_value["put_price"], rel_tol=0.01, abs_tol=0.01)


def test_monte_carlo_method_no_div(option_instance, ref_value):
    c, p = option_instance.monte_carlo_price()
    assert math.isclose(round(c, 2), ref_value["call_price"], rel_tol=0.01, abs_tol=0.01)
    assert math.isclose(round(p, 2), ref_value["put_price"], rel_tol=0.01, abs_tol=0.01)


def test_monte_carlo_method_with_div(input_data):
    input_data["dividend_yield"] = 0.03
    option_instance = Option(**input_data)
    c, p = option_instance.monte_carlo_price()
    ref_value = get_value_from_the_web(input_data)
    assert math.isclose(round(c, 2), ref_value["call_price"], rel_tol=0.1, abs_tol=0.1)
    assert math.isclose(round(p, 2), ref_value["put_price"], rel_tol=0.1, abs_tol=0.1)


def test_sterilize_attr_mc(option_instance, input_data):
    _ = option_instance.monte_carlo_price()
    option_instance.strike = 120
    assert option_instance.strike == 120
    assert option_instance._BS_price is None
    assert option_instance._MC_price is None
    c, p = option_instance.monte_carlo_price()
    input_data["strike"] = 120
    ref_value = get_value_from_the_web(input_data)
    assert math.isclose(round(c, 2), ref_value["call_price"], rel_tol=0.1, abs_tol=0.1)
    assert math.isclose(round(p, 2), ref_value["put_price"], rel_tol=0.1, abs_tol=0.1)


def test_greek_no_div(option_instance, ref_value):
    greeks = ["theta", "gamma", "delta", "vega", "rho"]
    for greek in greeks:
        assert math.isclose(getattr(option_instance, greek)()[0], ref_value["call_greeks"][greek], rel_tol=0.1,
                            abs_tol=0.1)
        assert math.isclose(getattr(option_instance, greek)()[1], ref_value["put_greeks"][greek], rel_tol=0.1,
                            abs_tol=0.1)


def test_greek_with_div(input_data):
    greeks = ["theta", "gamma", "delta", "vega", "rho"]
    input_data["dividend_yield"] = 0.03
    option_instance = Option(**input_data)
    ref_value = get_value_from_the_web(input_data)
    for greek in greeks:
        assert math.isclose(getattr(option_instance, greek)()[0], ref_value["call_greeks"][greek], rel_tol=0.1,
                            abs_tol=0.1)
        assert math.isclose(getattr(option_instance, greek)()[1], ref_value["put_greeks"][greek], rel_tol=0.1,
                            abs_tol=0.1)
