"""
parse input for the application
"""


def param_parser(param_dict):
    parsed_param = {}
    for key, value in param_dict.items():
        try:
            parsed_param[key] = float(value)
        except ValueError:
            parsed_param[key] = value
    return parsed_param