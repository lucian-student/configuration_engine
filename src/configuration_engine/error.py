class ConfigurationEngineError(Exception):
    pass


class NotFittedError(ConfigurationEngineError):
    pass


def error_message(module: str, action: str, problem: str):
    return f"{module} :: {action} - {problem}"
