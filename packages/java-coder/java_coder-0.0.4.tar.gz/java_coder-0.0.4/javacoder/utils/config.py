#!/user/bin/env python
# -*- coding: utf-8 -*-
# Time: 2025/9/7 15:09
# Author: chonmb
# Software: PyCharm
import json
import os
import inspect
import javacoder


class Configuration:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(inspect.getfile(javacoder)), 'config.json')
        if os.path.exists(self.config_file) and os.path.isfile(self.config_file):
            with open(self.config_file, 'r') as f:
                self.configuration = json.load(f)
        else:
            self.configuration = self.load_default_configuration()

    def get_property(self, prop):
        if self.configuration and prop in self.configuration:
            return self.configuration[prop]
        else:
            return None

    def set_property(self, prop, value):
        if not self.configuration:
            self.configuration = {}
        self.configuration[prop] = value

    def load_default_configuration(self):
        return {
            'debug_mode': False
        }

    def set_global_property(self, prop, value):
        self.set_property(prop, value)
        with open(self.config_file, 'w') as f:
            global_config = json.load(f)
            global_config[prop] = value
            f.write(json.dumps(global_config))


configuration = Configuration()


def get_property(prop):
    return configuration.get_property(prop)


def set_property(prop, value):
    return configuration.set_property(prop, value)


def set_global_property(prop, value):
    return configuration.set_global_property(prop, value)
