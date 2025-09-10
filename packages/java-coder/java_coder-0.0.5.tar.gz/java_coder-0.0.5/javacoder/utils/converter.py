import re

import javalang
from javalang.parser import JavaSyntaxError


def camel_to_snake(name):
    # convert camelFormat to snake_format
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def is_collection(collection):
    return hasattr(collection, '__iter__') and hasattr(collection, '__getitem__')


def get_first_element(collect, eq_func):
    for i in collect:
        if eq_func(i):
            return i
    return None


def is_basic_type(type):
    basic_type = ['String', 'Boolean', 'Long', 'Double', 'Float', 'char', 'boolean', 'long', 'float', 'double', 'int',
                  'Integer']
    return type in basic_type


def parse_expression(expression):
    if type(expression) == str:
        try:
            return javalang.parse.parse_member_signature(expression)
        except JavaSyntaxError:
            pass
        try:
            return javalang.parse.parse_expression(expression)
        except JavaSyntaxError:
            pass
        try:
            return javalang.parse.parse_constructor_signature(expression)
        except JavaSyntaxError:
            pass
    return expression


def convert_literal_value(value):
    if type(value) == str:
        return f'"{value}"'
    else:
        return value
