import os


class Env:
    @staticmethod
    def get_bool(variable_name, default=False):
        variable = os.environ.get(variable_name, None)
        if variable is None:
            return default
        return variable.lower() == 'true'

    @staticmethod
    def get_str(variable_name, default=''):
        variable = os.environ.get(variable_name, None)
        if variable is None:
            return default
        return variable

    @staticmethod
    def get_list(variable_name, default=None):
        if default is None:
            default = []

        variable = os.environ.get(variable_name, None)
        if not variable:
            return default

        return [item.strip() for item in variable.split(',') if item.strip()]
