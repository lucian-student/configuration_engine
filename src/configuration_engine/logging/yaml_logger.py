from typing import Dict
import io
import yaml
from configuration_engine.logging.logger import Logger

class YamlLogger(Logger):

    def log(self, data: Dict):
        yaml.dump(
            data,
            self.stream(),
            default_flow_style=False,
            allow_unicode=True,
            explicit_start=True,
        )


class YamlStringLogger(YamlLogger):

    def __init__(self):
        self._stream = io.StringIO()

    def stream(self) -> io.TextIOBase:
        return self._stream


class YamlFileLogger(YamlLogger):

    def __init__(self, path: str):
        """
        Throws:
            OSError
        """
        self._stream = open(path, "a")

    def log(self, data):
        super().log(data)
        self._stream.flush()

    def stream(self) -> io.TextIOBase:
        return self._stream
